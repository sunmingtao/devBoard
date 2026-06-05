#!/usr/bin/env bash
set -e

DATA_DISK="/dev/nvme1n1"
DATA_DIR="/data"

echo "=== 1. Basic packages ==="
sudo apt update
sudo apt install -y \
  curl wget git unzip build-essential \
  python3 python3-venv python3-pip \
  ffmpeg ubuntu-drivers-common \
  htop nvtop

echo "=== 2. Mount data disk to /data ==="
if lsblk "$DATA_DISK" >/dev/null 2>&1; then
  if ! mount | grep -q " $DATA_DIR "; then
    sudo mkdir -p "$DATA_DIR"

    if ! sudo blkid "$DATA_DISK" >/dev/null 2>&1; then
      echo "Formatting $DATA_DISK ..."
      sudo mkfs.ext4 "$DATA_DISK"
    fi

    UUID=$(sudo blkid -s UUID -o value "$DATA_DISK")
    if ! grep -q "$UUID" /etc/fstab; then
      echo "UUID=$UUID $DATA_DIR ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
    fi

    sudo mount -a
  fi

  sudo chown -R ubuntu:ubuntu "$DATA_DIR"
else
  echo "WARNING: $DATA_DISK not found. Skipping /data mount."
fi

echo "=== 3. Setup cache dirs ==="
mkdir -p /data/tmp /data/pip-cache /data/hf-cache/hub /data/ollama
sudo chmod 1777 /data/tmp
sudo chown -R ubuntu:ubuntu /data/pip-cache /data/hf-cache

cat >> ~/.bashrc <<'EOF'

# AI workload cache paths
export TMPDIR=/data/tmp
export PIP_CACHE_DIR=/data/pip-cache
export HF_HOME=/data/hf-cache
export HUGGINGFACE_HUB_CACHE=/data/hf-cache/hub
EOF

export TMPDIR=/data/tmp
export PIP_CACHE_DIR=/data/pip-cache
export HF_HOME=/data/hf-cache
export HUGGINGFACE_HUB_CACHE=/data/hf-cache/hub

echo "=== 4. Install NVIDIA driver ==="
sudo ubuntu-drivers autoinstall
echo "NVIDIA driver installed. Reboot is required before GPU works."

echo "=== 5. Create Python venv ==="
mkdir -p /data
cd /data
git clone https://github.com/sunmingtao/devBoard.git
cd /data/devBoard/scripts/subtitle_pipeline

python3 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

echo "=== 6. Install Python AI packages ==="
python -m pip install \
  faster-whisper \
  ollama\
  python-dotenv\
  nvidia-cublas-cu12 \
  nvidia-cudnn-cu12 \
  huggingface-hub

cat >> venv/bin/activate <<'EOF'

export TMPDIR=/data/tmp
export PIP_CACHE_DIR=/data/pip-cache
export HF_HOME=/data/hf-cache
export HUGGINGFACE_HUB_CACHE=/data/hf-cache/hub
export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cublas/lib:$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH
EOF

echo "=== 7. Install Ollama ==="
curl -fsSL https://ollama.com/install.sh | sudo sh

sudo mkdir -p /data/ollama
sudo chown -R ollama:ollama /data/ollama || true

sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<'EOF'
[Service]
Environment="OLLAMA_MODELS=/data/ollama"
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama

echo "=== DONE ==="
echo "Now reboot:"
echo "sudo reboot"