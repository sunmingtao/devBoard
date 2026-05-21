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