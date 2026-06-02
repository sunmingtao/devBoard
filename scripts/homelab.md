Kubernetes外卖系统宇宙 

Pod=骑手

ReplicaSet=猪头小队长，负责维持骑手数量（e.g. 必须维持10个骑手，有人生病需及时替换）

Deployment=区域招聘主管，决定骑手数量，骑手该用什么装备（电动车，衣服，头盔），给骑手贴区域标签（普陀区，静安区，徐汇区），制定新老交替策略（新骑手逐步替代老骑手，还是年纪到了就一刀切）

Service=区域调度经理，不跟招聘主管直接交流，根据区域标签把订单交给骑手（静安区订单来了，找所有静安区骑手，随机派单）。通过内部QQ接订单，不直接跟客户交流。

Ingress=全国客服总机，通过全国统一客服电话接客户订单，转给对应区域调度经理（Service）

Controller=锦衣卫监察，确保每个人都按照工作手册干活。

ArgoCd Application=外包公司总负责人
- Rollout App=负责安插高级灰度调度经理
- External Secret App=负责安插保密科科长
- Kafka App=安装消息管道（跨区骑手通过消息管道交流）
- Prometheus App=安装监控系统
- Grafana App=安装警报观测平台
- Kafka Export App=安装消息管道上的监控器（管道是否畅通）

ArcoCd Custom Resource=非Kubernetes原产，来自外包公司的资源
- Rollout=高级灰度调度经理
- Secret=保密科科长
- ServiceMonitor=定义监控目标

### 2026-05-17

```bash
sudo apt install docker.io -y

sudo usermod -aG docker $USER
newgrp docker

sudo vi /etc/sysctl.d/99-dmesg.conf
# kernel.dmesg_restrict = 0

sudo sysctl --system

dmesg -K

sudo vgdisplay
lsblk

sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```

### 2026-05-18

```
sudo apt-get install -y ansible
cd infra/ansible
ansible-galaxy collection install -r collections/requirements.yml
ansible homelab -m ping

sudo vi /etc/sudoers.d/90-mike-ansible
  # mike ALL=(ALL) NOPASSWD:ALL

# Effective ssh config
sshd -T | egrep '^(pubkeyauthentication|permitrootlogin|passwordauthentication|kbdinteractiveauthentication)'

# Only run selected tags
ansible-playbook playbooks/bootstrap.yml --tags locale
```

### 2026-05-19
```
getent passwd
getent group
groups mike
id mike

kubectl -n argocd port-forward svc/argocd-server 8080:443

# From laptop, keep Argo CD bound to homelab localhost and tunnel over SSH.
ssh -L 9090:127.0.0.1:8080 mike@192.168.0.46 -i ~/.ssh/homelab 'kubectl -n argocd port-forward svc/argocd-server 8080:443'

# Then open on laptop:
# https://localhost:9090

kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

lsof -i :8080
```

### 2026-05-20

```
vi /etc/hosts
  192.168.0.46    dev.devboard.local prod.devboard.local

curl http://dev.devboard.local:30080/
curl http://prod.devboard.local:30080/
```

Edit C:\Windows\System32\drivers\etc\hosts
Add `192.168.0.46    dev.devboard.local prod.devboard.local`

### 2026-05-21

Print credentials



```
node {
    def creds

    stage('Sandbox') {
        withCredentials([usernamePassword(credentialsId: 'my-creds', passwordVariable: 'C_PASS', usernameVariable: 'C_USER')]) {
            creds = "\nUser: ${C_USER}\nPassword: ${C_PASS}\n"
        }
        println creds
    }
}
```

Script console

```
import jenkins.model.Jenkins
import com.cloudbees.plugins.credentials.CredentialsProvider
import com.cloudbees.plugins.credentials.common.UsernamePasswordCredentials

def creds = CredentialsProvider.lookupCredentialsInItemGroup(
  UsernamePasswordCredentials.class,
  Jenkins.get(),
  null,
  null
)

creds.findAll { it.id == 'dockerhub-creds' }.each { c ->
  println "id=${c.id}"
  println "username=${c.username}"
  println "username=${c.password}"
  println "description=${c.description}"
}

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
source ~/.bashrc
nvm --version
nvm install node
nvm use node
nvm alias default node
npm audit fix --force

docker build -t devboard-frontend-vite8-check apps/frontend
```

### 2026-05-22

```
mkdir -p ~/.devboard-certs/portainer
cd ~/.devboard-certs/portainer

openssl genrsa -out homelab-ca.key 4096

openssl req -x509 -new -nodes \
  -key homelab-ca.key \
  -sha256 \
  -days 3650 \
  -out homelab-ca.crt \
  -subj "/CN=DevBoard Homelab CA"

openssl genrsa -out portainer.key 2048

cat > portainer.cnf <<'EOF'
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
CN = 192.168.0.46

[req_ext]
subjectAltName = @alt_names

[alt_names]
IP.1 = 192.168.0.46
DNS.1 = homelab01
EOF

openssl req -new \
  -key portainer.key \
  -out portainer.csr \
  -config portainer.cnf

openssl x509 -req \
  -in portainer.csr \
  -CA homelab-ca.crt \
  -CAkey homelab-ca.key \
  -CAcreateserial \
  -out portainer.crt \
  -days 825 \
  -sha256 \
  -extensions req_ext \
  -extfile portainer.cnf

ssh homelab 'mkdir -p /opt/stacks/portainer/certs'

scp portainer.crt portainer.key homelab-ca.crt homelab:/opt/stacks/portainer/certs/

cd infra/ansible
read -rsp "Pi-hole web password: " PIHOLE_WEB_PASSWORD
ansible-playbook playbooks/pihole.yml \
  -e "pihole_web_password=${PIHOLE_WEB_PASSWORD}"
unset PIHOLE_WEB_PASSWORD

```

### 2026-05-24
```
k get deploy argocd-repo-server -n argocd -o yaml

ansible-playbook -vvv playbooks/argocd.yml -e argocd_bootstrap_k3s_apps=true

ansible-playbook playbooks/argocd.yml --tags argocd_cli

# check argocd-server exposed port
k get svc -n argocd

# port-forward map homelab host port 8080 to container 443
# ssh tunnel map laptop port 8079 to homlab host 8080
 ssh -L 8079:127.0.0.1:8080 homelab   'kubectl -n argocd port-forward svc/argocd-server 8080:443'

# broardcast to the entire network
kubectl port-forward --address 0.0.0.0 svc/argocd-server 8080:443

# Get password in homelab
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Log in 
argocd login localhost:8079 --username admin --password "$ARGOCD_K3S_DEV_PASSWORD" --insecure

argocd app list
argocd app sync devboard-dev-k3s


kubectl -n argocd exec -it argocd-repo-server-56d64fd75b-75svw -c ksops -- bash
kubectl -n argocd exec -it argocd-server-5f94d97985-jpm8l -c ksops -- echo $PATH
kubectl -n argocd exec -it argocd-repo-server-56d64fd75b-75svw -c ksops -- echo $PATH


cd infra/ansible

ansible homelab -m command -a "kubectl -n argocd rollout restart deployment/argocd-repo-server"

ansible homelab -m command -a "kubectl -n argocd rollout status deployment/argocd-repo-server --timeout=300s"

ansible homelab -m command -a "kubectl -n argocd annotate application devboard-dev-k3s argocd.argoproj.io/refresh=hard --overwrite"
```

### 2026-05-25

```
### View annotation of an app
kubectl -n argocd get app devboard-dev-k3s -o yaml | grep annotations

### View secret

kubectl get secret/devboard-backend-secret -n devboard-dev -o yaml

echo 'ZGV2LWszcy1wbGFjZWhvbGRlci1qd3Qtc2VjcmV0LWNoYW5nZS1tZQ==' | base64 -d

### Get statefulset -- pod is not ephemeral, e.g. kafka 
kubectl get sts -n devboard-dev

kubectl delete sts/devboard-kafka-controller -n devboard-dev
kubectl -n devboard-dev wait --for=delete pod/devboard-kafka-controller-0 --timeout=120s
kubectl -n devboard-dev get pvc

sudo ls -la /var/lib/rancher/k3s/server/db

kubectl -n devboard-prod scale sts devboard-kafka-controller --replicas=0

getent host
getent passwd
getent group

kubectl get pv

sudo systemctl daemon-reload
sudo systemctl start k3s-state-backup.service

journalctl -u k3s-state-backup.service
systemctl list-units
systemctl list-timers

```

### 2026-05-26

systemctl stop k3s-state-backup.service
systemctl disable k3s-state-backup.service
rm /etc/systemd/system/k3s-state-backup.service
systemctl daemon-reload


kubectl -n devboard-prod exec deploy/mysql -- \
  sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --all-databases --single-transaction' \
  > devboard-prod-mysql-$(date +%F-%H%M%S).sql
  
kubectl -n devboard-prod scale sts devboard-kafka-controller --replicas=0

kubectl -n devboard-prod wait \
  --for=delete pod/devboard-kafka-controller-0 \
  --timeout=120s

sudo tar -czf /var/backups/devboard/kafka-prod-pvc-$(date +%F-%H%M%S).tar.gz \
  -C /var/lib/rancher/k3s/storage \
  <actual-kafka-prod-pv-dir>

kubectl -n devboard-prod scale sts devboard-kafka-controller --replicas=1

kubectl -n devboard-prod rollout status sts/devboard-kafka-controller

### 2026-05-27

argocd app set devboard-kafka-prod-k3s --sync-policy none
argocd app set devboard-kafka-prod-k3s --sync-policy automated --self-heal --auto-prune

kubectl -n argocd port-forward svc/argocd-server 8080:443
argocd login localhost:8080 --username admin --password "$ARGOCD_PASSWORD" --insecure

argocd app get devboard-kafka-prod-k3s


python3 - << 'PY'
import socket
s = socket.socket()
s.bind(('',0))
print(s.getsockname())
s.close()
PY

mike@homelab:~$ set -u; echo "$HAHA" || true
-bash: HAHA: unbound variable
mike@homelab:~$ set -u; echo "$HAHA" || true
-bash: HAHA: unbound variable
mike@homelab:~$ echo $?
1
mike@homelab:~$ set +u; echo "$HAHA" || true

mike@homelab:~$ echo $?
0

kubectl -n argocd patch application devboard-kafka-prod-k3s   --type merge   -p '{"spec":{"syncPolicy":null}}'
kubectl -n argocd patch application devboard-kafka-prod-k3s   --type merge   -p '{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":true}}}}'
kubectl -n argocd patch application devboard-kafka-prod-k3s   --type merge   -p '{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":false}}}}'


kubectl -n devboard-prod get sts devboard-kafka-controller -o json | jq '.spec.syncPolicy


### 2026-05-28

exec 9> /tmp/file.lock
flock -n 9

# View File descriptor
ls -l /proc/$$/fd
echo $$

### 2026-05-29

sudo apt install ffmpeg -y
ffmpeg -version
sudo apt install python3.12-venv
python3 -m venv whisper-env
source whisper-env/bin/activate
pip install faster-whisper

nproc

### 2026-05-30

alias transjap="source /home/jacky/workspace/devBoard/scripts/whisper-env/bin/activate; cd /home/jacky/workspace/devBoard/scripts/whisper-env"

curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:8b

cat test.json | ollama run qwen3:8b --think=false

FILE_NAME="聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate"
ffmpeg -i $FILE_NAME.mp4 -vn -ac 1 -ar 16000 -af loudnorm $FILE_NAME.wav

ffmpeg -i $FILE_NAME.mp4 -t 00:20:00 -c copy $FILE_NAME-sample.mp4

yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" "https://www.youtube.com/watch?v=Oe2hY2PyaVQ"

python translate_srt_english.py

### 2026-05-31

ffmpeg -i INPUT.mp4 -i subtitle.srt \
-c:v copy \
-c:a copy \
-c:s mov_text \
OUTPUT.mp4


ffmpeg -i 聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample.mp4 -i 聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample_zh.srt \
-c:v copy \
-c:a copy \
-c:s mov_text \
聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample中文字幕.mp4


ffmpeg -i 聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample.mp4 -vf "subtitles=聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample_zh.srt" 聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample中文字幕.mp4

sudo apt update
sudo apt install fonts-noto-cjk

INPUT="聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample"
SRT="聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate-sample_zh"
OUTPUT="$INPUT中文字幕"
ffmpeg -i $INPUT.mp4 \
-vf "subtitles=$SRT.srt:force_style='FontName=Noto Sans CJK SC,FontSize=24'" \
$OUTPUT.mp4

python3 -m venv venv
pip install -r requirements.txt

FILE_NAME=“聪明哥-2026年最新视频-20BB-Poker-500NL-GG-winrate”
ffmpeg -i $FILE_NAME.mp4 -t 00:09:00 -c copy $FILE_NAME-sample2.mp4


deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

pip install faster-whisper
pip install ollama
pip install python-dotenv

python -c "from faster_whisper import WhisperModel; print('OK')"

pip freeze > requirements.txt

python -m unittest discover -s tests

tmux
Ctrl+D b
tmux attach

### 2026-06-01

ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 input.mp4
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 input.wav

ffmpeg -i input.mp4 \
-map 0:a:0 \
-vn \
-ac 1 \
-ar 16000 \
-af "dynaudnorm" \
-c:a pcm_s16le \
SW-473~S-new.wav

sudo apt update
sudo apt install samba -y

smbd --version

sudo vi /etc/samba/smb.conf

[workspaces]
    comment = Mike Workspace
    path = /home/mike/workspaces

    browseable = yes
    writable = yes
    read only = no

    guest ok = no
    valid users = mike

    create mask = 0664
    directory mask = 0775

    force user = mike

sudo smbpasswd -a mike
sudo smbpasswd -e mike

ls -ld /home/mike/workspaces

sudo testparm

sudo systemctl restart smbd
sudo systemctl enable smbd

sudo systemctl status smbd

sudo ufw allow samba

sudo ufw status
sudo ss -tulpn | grep smbd

python3 -c "import inspect, ollama; print(inspect.signature(ollama.chat))"


useradd -m -s /bin/bash connor
passwd connor

# show wireless interface info
iw dev wlp2s0 link
iwconfig wlp2s0

# Windows Powershell
netsh wlan show interfaces


iperf3 -s
iperf3 -c 192.168.0.46

sudo apt install cifs-utils
smbclient -L //192.168.0.61 -U smt
sudo mount -t cifs //192.168.0.61/homes /mnt/sun   -o username=smt,password=*****


sudo iw dev wlp2s0 set power_save off

### 2026-06-03

ssh-keygen -t ed25519 -f ~/.ssh/linode -C "mike@linode"

AWS service quota
request g6.xlarge

Run Script

```
#!/usr/bin/env bash
set -e

echo "== Update system =="
sudo apt update
sudo apt install -y curl git htop nvtop ffmpeg python3 python3-venv python3-pip

echo "== Check NVIDIA GPU =="
nvidia-smi || true

echo "== Install Ollama =="
curl -fsSL https://ollama.com/install.sh | sh

echo "== Enable Ollama =="
sudo systemctl enable ollama
sudo systemctl restart ollama

echo "== Install Python env for Whisper =="
mkdir -p ~/whisper-job
cd ~/whisper-job
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install faster-whisper
```