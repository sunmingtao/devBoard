#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INSTANCE_TYPE="${INSTANCE_TYPE:-g6.xlarge}"
ROOT_VOLUME_SIZE="${ROOT_VOLUME_SIZE:-50}"
KEY_NAME="${KEY_NAME:-aws-gpu-key}"
KEY_PATH="${KEY_PATH:-$HOME/.ssh/aws-gpu-key.pem}"
SSH_USER="${SSH_USER:-ubuntu}"
MODEL="${MODEL:-qwen3:8b}"
MEDIA_DIR="${MEDIA_DIR:-$PWD}"
MAX_LIFESPAN_MINUTES="${MAX_LIFESPAN_MINUTES:-60}"
INSTANCE_NAME="${INSTANCE_NAME:-devboard-gpu-$(date +%Y%m%d-%H%M%S)}"
SG_NAME="${SG_NAME:-devboard-gpu-test-ssh}"
AMI_PARAMETER="${AMI_PARAMETER:-/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id}"
REMOTE_INPUT_DIR="/data/devBoard/scripts/subtitle_pipeline/input"
REMOTE_PIPELINE_DIR="/data/devBoard/scripts/subtitle_pipeline"

AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-}}"

usage() {
  cat <<'EOF'
Usage: run-gpu-job.sh [--no-run]

Environment overrides:
  AWS_REGION              AWS region to use. Defaults to aws configure get region.
  KEY_NAME                EC2 key pair name. Default: aws-gpu-key
  KEY_PATH                Local private key. Default: ~/.ssh/aws-gpu-key.pem
  MEDIA_DIR               Directory containing *.wav and *.mp4 files. Default: current directory
  MODEL                   Ollama model to pull. Default: qwen3:8b
  MAX_LIFESPAN_MINUTES    Instance wall-clock lifespan before poweroff/termination. Default: 60
  SUBNET_ID               Use this subnet instead of the first default subnet.
  VPC_ID                  Use this VPC for the generated SSH security group.
  SECURITY_GROUP_ID       Use this security group instead of creating/reusing one.
  SSH_CIDR                CIDR allowed for SSH. Default: current public IP /32
EOF
}

RUN_PIPELINE=1
while (($#)); do
  case "$1" in
    --no-run)
      RUN_PIPELINE=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

log() {
  printf '\n== %s ==\n' "$*"
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

need() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required"
}

aws_ec2() {
  aws --region "$AWS_REGION" ec2 "$@"
}

aws_ssm() {
  aws --region "$AWS_REGION" ssm "$@"
}

text_or_empty() {
  [[ "$1" == "None" || "$1" == "null" ]] && return 1
  [[ -n "$1" ]]
}

wait_for_ssh() {
  local public_ip="$1"
  local timeout_seconds="${2:-900}"
  local deadline=$((SECONDS + timeout_seconds))

  while ((SECONDS < deadline)); do
    if ssh "${SSH_OPTS[@]}" "$SSH_USER@$public_ip" "true" >/dev/null 2>&1; then
      return 0
    fi
    sleep 10
  done

  return 1
}

current_public_cidr() {
  local ip
  ip="$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')" || return 1
  [[ "$ip" == *.* ]] || return 1
  printf '%s/32\n' "$ip"
}

resolve_network() {
  if [[ -n "${SUBNET_ID:-}" ]]; then
    if [[ -z "${VPC_ID:-}" ]]; then
      VPC_ID="$(aws_ec2 describe-subnets \
        --subnet-ids "$SUBNET_ID" \
        --query 'Subnets[0].VpcId' \
        --output text)"
      text_or_empty "$VPC_ID" || die "Could not resolve VPC for subnet $SUBNET_ID. Set VPC_ID."
    fi
    return
  fi

  if [[ -z "${VPC_ID:-}" ]]; then
    VPC_ID="$(aws_ec2 describe-vpcs \
      --filters Name=isDefault,Values=true \
      --query 'Vpcs[0].VpcId' \
      --output text)"
    text_or_empty "$VPC_ID" || die "No default VPC found. Set VPC_ID and SUBNET_ID."
  fi

  SUBNET_ID="$(aws_ec2 describe-subnets \
    --filters Name=vpc-id,Values="$VPC_ID" Name=default-for-az,Values=true \
    --query 'Subnets[0].SubnetId' \
    --output text)"
  text_or_empty "$SUBNET_ID" || die "No default subnet found in $VPC_ID. Set SUBNET_ID."
}

ensure_security_group() {
  if [[ -n "${SECURITY_GROUP_ID:-}" ]]; then
    SG_ID="$SECURITY_GROUP_ID"
    return
  fi

  SG_ID="$(aws_ec2 describe-security-groups \
    --filters Name=group-name,Values="$SG_NAME" Name=vpc-id,Values="$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || true)"

  if ! text_or_empty "$SG_ID"; then
    SG_ID="$(aws_ec2 create-security-group \
      --group-name "$SG_NAME" \
      --description "Temporary SSH access for devBoard GPU test" \
      --vpc-id "$VPC_ID" \
      --query 'GroupId' \
      --output text)"
  fi

  if [[ -z "${SSH_CIDR:-}" ]]; then
    SSH_CIDR="$(current_public_cidr)" || die "Could not detect public IP for SSH. Set SSH_CIDR."
  fi
  aws_ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --ip-permissions "IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=$SSH_CIDR,Description=devBoard GPU SSH}]" \
    >/dev/null 2>&1 || true
}

build_user_data() {
  USER_DATA_FILE="$(mktemp)"
  cat >"$USER_DATA_FILE" <<EOF
#!/usr/bin/env bash
set -euo pipefail

deadline="\$(date -u -d '+${MAX_LIFESPAN_MINUTES} minutes' '+%Y-%m-%d %H:%M:%S UTC')"

cat >/usr/local/sbin/devboard-gpu-expire <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
/sbin/shutdown -P now "devBoard GPU lifespan expired"
SCRIPT
chmod +x /usr/local/sbin/devboard-gpu-expire

cat >/etc/systemd/system/devboard-gpu-lifespan.service <<'UNIT'
[Unit]
Description=Power off devBoard GPU instance at lifespan deadline

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/devboard-gpu-expire
UNIT

cat >/etc/systemd/system/devboard-gpu-lifespan.timer <<UNIT
[Unit]
Description=devBoard GPU one-hour lifespan guard

[Timer]
OnCalendar=\$deadline
Persistent=true
Unit=devboard-gpu-lifespan.service

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now devboard-gpu-lifespan.timer
EOF
}

cleanup() {
  [[ -n "${USER_DATA_FILE:-}" && -f "$USER_DATA_FILE" ]] && rm -f "$USER_DATA_FILE"
}
trap cleanup EXIT

need aws
need curl
need scp
need ssh

if [[ -z "$AWS_REGION" ]]; then
  AWS_REGION="$(aws configure get region || true)"
fi
[[ -n "$AWS_REGION" ]] || die "AWS_REGION is required or must be configured in aws cli"
[[ -r "$KEY_PATH" ]] || die "SSH key not found: $KEY_PATH"
[[ -f "$SCRIPT_DIR/gpu-instance-setup.sh" ]] || die "Missing $SCRIPT_DIR/gpu-instance-setup.sh"

SSH_OPTS=(
  -i "$KEY_PATH"
  -o BatchMode=yes
  -o ConnectTimeout=10
  -o StrictHostKeyChecking=accept-new
  -o ServerAliveInterval=30
)

log "Resolving Ubuntu 24.04 AMI and default network"
AMI_ID="$(aws_ssm get-parameter --name "$AMI_PARAMETER" --query 'Parameter.Value' --output text)"
text_or_empty "$AMI_ID" || die "Could not resolve Ubuntu AMI from $AMI_PARAMETER"
ROOT_DEVICE_NAME="$(aws_ec2 describe-images --image-ids "$AMI_ID" --query 'Images[0].RootDeviceName' --output text)"
text_or_empty "$ROOT_DEVICE_NAME" || ROOT_DEVICE_NAME="/dev/sda1"
resolve_network
ensure_security_group
build_user_data

log "Launching $INSTANCE_TYPE ($INSTANCE_NAME)"
INSTANCE_ID="$(aws_ec2 run-instances \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --network-interfaces "DeviceIndex=0,SubnetId=$SUBNET_ID,Groups=[$SG_ID],AssociatePublicIpAddress=true" \
  --block-device-mappings "DeviceName=$ROOT_DEVICE_NAME,Ebs={VolumeSize=$ROOT_VOLUME_SIZE,VolumeType=gp3,DeleteOnTermination=true}" \
  --instance-initiated-shutdown-behavior terminate \
  --user-data "file://$USER_DATA_FILE" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME},{Key=Project,Value=devBoard},{Key=MaxLifespanMinutes,Value=$MAX_LIFESPAN_MINUTES}]" \
  --query 'Instances[0].InstanceId' \
  --output text)"
text_or_empty "$INSTANCE_ID" || die "Failed to launch instance"

log "Waiting for instance $INSTANCE_ID"
aws_ec2 wait instance-running --instance-ids "$INSTANCE_ID"
PUBLIC_IP="$(aws_ec2 describe-instances --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)"
text_or_empty "$PUBLIC_IP" || die "Instance has no public IP"
wait_for_ssh "$PUBLIC_IP" 900 || die "SSH did not become ready for $PUBLIC_IP"

log "Running GPU setup on $PUBLIC_IP"
scp "${SSH_OPTS[@]}" "$SCRIPT_DIR/gpu-instance-setup.sh" "$SSH_USER@$PUBLIC_IP:/tmp/gpu-instance-setup.sh"
ssh "${SSH_OPTS[@]}" "$SSH_USER@$PUBLIC_IP" "chmod +x /tmp/gpu-instance-setup.sh && /tmp/gpu-instance-setup.sh"

log "Rebooting for NVIDIA driver"
ssh "${SSH_OPTS[@]}" "$SSH_USER@$PUBLIC_IP" "sudo reboot" >/dev/null 2>&1 || true
sleep 30
wait_for_ssh "$PUBLIC_IP" 1200 || die "SSH did not return after reboot"

log "Verifying GPU and preparing Ollama"
ssh "${SSH_OPTS[@]}" "$SSH_USER@$PUBLIC_IP" \
  "nvidia-smi && sudo systemctl start ollama && ollama --version && ollama pull '$MODEL'"

log "Copying media from $MEDIA_DIR"
shopt -s nullglob
MEDIA_FILES=("$MEDIA_DIR"/*.wav "$MEDIA_DIR"/*.mp4)
shopt -u nullglob
if ((${#MEDIA_FILES[@]})); then
  ssh "${SSH_OPTS[@]}" "$SSH_USER@$PUBLIC_IP" "mkdir -p '$REMOTE_INPUT_DIR'"
  scp "${SSH_OPTS[@]}" "${MEDIA_FILES[@]}" "$SSH_USER@$PUBLIC_IP:$REMOTE_INPUT_DIR/"
else
  echo "No .wav or .mp4 files found in $MEDIA_DIR; skipping media copy."
fi

if ((RUN_PIPELINE)); then
  log "Running subtitle pipeline"
  ssh "${SSH_OPTS[@]}" "$SSH_USER@$PUBLIC_IP" \
    "cd '$REMOTE_PIPELINE_DIR' && source venv/bin/activate && python run.py"
else
  log "Skipping pipeline run"
fi

cat <<EOF

Instance: $INSTANCE_ID
Public IP: $PUBLIC_IP
SSH: ssh -i "$KEY_PATH" $SSH_USER@$PUBLIC_IP
Lifespan guard: instance powers off and terminates after $MAX_LIFESPAN_MINUTES minutes from first boot.
EOF
