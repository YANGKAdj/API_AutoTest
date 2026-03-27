# VMware 安装 Debian 12 完整指南

## 一、准备工作

### 1. 下载Debian 12 Netinst镜像
- **下载地址**: https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/
- **文件名**: `debian-12.x.x-amd64-netinst.iso` (x.x是版本号)
- **大小**: 约350MB
- **推荐镜像站**:
  - 官方: https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/
  - 清华源: https://mirrors.tuna.tsinghua.edu.cn/debian-cd/current/amd64/iso-cd/
  - 中科大源: https://mirrors.ustc.edu.cn/debian-cd/current/amd64/iso-cd/

### 2. VMware版本要求
- VMware Workstation 15+ 或 VMware Player 15+
- 或 VMware Fusion (macOS)

## 二、创建虚拟机

### 步骤1: 新建虚拟机
1. 打开VMware → "创建新的虚拟机"
2. 选择 "典型(推荐)" → 下一步
3. 选择 "稍后安装操作系统" → 下一步
   - **重要**: 不要选择"安装程序光盘映像文件",会导致自动安装

### 步骤2: 选择操作系统
1. 客户机操作系统: **Linux**
2. 版本: **Debian 12.x 64位**
3. 下一步

### 步骤3: 虚拟机名称和位置
1. 虚拟机名称: `Debian-Docker-Server` (自定义)
2. 位置: 选择磁盘空间充足的路径
3. 下一步

### 步骤4: 硬件配置
**推荐配置(用于银行API项目):**

| 配置项 | 测试环境 | 生产环境 |
|--------|----------|----------|
| **内存** | 2GB | 4GB+ |
| **处理器** | 2核 | 4核+ |
| **硬盘** | 20GB (动态分配) | 50GB+ |
| **网络** | NAT / 桥接 | 桥接 |

**详细设置:**
1. 磁盘大小: 20GB (测试) / 50GB (生产)
2. 选择 "将虚拟磁盘拆分成多个文件" (方便移动)
3. 自定义硬件:
   - 内存: 2048MB (2GB)
   - 处理器: 2核
   - 网络: NAT模式(测试) 或 桥接模式(需要局域网访问)
   - CD/DVD: 选择 "使用ISO映像文件" → 浏览选择下载的debian-12.x.x-amd64-netinst.iso

### 步骤5: 完成创建
点击 "完成"

## 三、安装Debian系统

### 启动虚拟机
1. 选中虚拟机 → "开启此虚拟机"
2. 进入Debian安装界面

### 安装步骤详解

#### 1. 启动菜单
选择: `Install` (文本界面,推荐) 或 `Graphical Install` (图形界面)
- 推荐选择 `Install` (更轻量,操作一样简单)

#### 2. 语言选择
- 选择: `中文(简体)` 或 `English` (推荐英文,避免乱码问题)
- 建议: **English** (服务器通常使用英文)

#### 3. 选择位置
- Country, territory or area: `China`
- Keyboard layout: `American English`

#### 4. 配置网络
- 主机名: `debian-server` (或自定义)
- 域名: 留空 或填写你的域名

#### 5. 设置用户和密码
- Root密码: 设置强密码 (记住这个密码!)
- 创建普通用户:
  - 用户全名: `deploy` (或自定义)
  - 用户名: `deploy`
  - 密码: 设置密码

#### 6. 磁盘分区
**推荐方案(新手):**
1. 分区方法: `向导 - 使用整个磁盘`
2. 选择磁盘: `SCSI3 (0,0,0) (sda) - XX GB VMware Virtual disk`
3. 分区方案: `将所有文件放在同一个分区中(推荐新手使用)`
4. 结束分区向导并将修改写入磁盘: 选择
5. 将改动写入磁盘吗? → `是`

**高级方案(可选):**
```
/        15GB    (根分区)
swap     2GB     (交换分区,内存2GB时)
/home    剩余     (家目录)
```

#### 7. 软件包管理
- 扫描其他CD: `否`
- 网络镜像: `是`
- 选择国家: `China`
- 选择镜像站: 
  - `mirrors.tuna.tsinghua.edu.cn` (清华源,推荐)
  - 或 `mirrors.ustc.edu.cn` (中科大源)
- HTTP代理: 留空

#### 8. 软件选择 ⚠️ 重要!
**只选择以下选项:**
- [x] SSH server (必须)
- [x] 标准系统工具 (推荐)
- [ ] Debian桌面环境 (不选)
- [ ] GNOME (不选)
- [ ] ... (其他都不选)

**按空格键选择/取消,回车确认**

#### 9. 安装GRUB引导器
- 将GRUB安装到主引导记录: `是`
- 设备: `/dev/sda`

#### 10. 完成安装
- 时钟设置为UTC: `是`
- 安装完成 → `继续` (系统会重启)

## 四、系统初始化配置

### 1. 登录系统
```bash
# 用户名: root
# 密码: 安装时设置的root密码

Debian GNU/Linux 12 debian-server tty1
debian-server login: root
Password: [输入密码]
```

### 2. 检查网络
```bash
# 检查IP地址
ip addr show

# 测试网络连接
ping -c 4 baidu.com
```

### 3. 更新系统
```bash
# 更新软件源
apt update

# 升级已安装的软件包
apt upgrade -y
```

### 4. 安装必要工具
```bash
# 安装常用工具
apt install -y curl wget vim htop net-tools
```

### 5. 配置SSH远程登录(重要!)

**如果你在Windows主机上操作,推荐用SSH客户端连接:**

```bash
# 1. 检查SSH服务状态
systemctl status ssh

# 2. 查看虚拟机IP地址
ip addr show

# 假设看到IP是: 192.168.xxx.xxx (NAT模式)
# 或: 192.168.1.xxx (桥接模式)

# 3. 在Windows上使用PowerShell或CMD连接
# ssh root@虚拟机IP地址
```

**配置静态IP(可选):**
```bash
# 编辑网络配置
vim /etc/network/interfaces

# 添加静态IP配置
# iface eth0 inet static
#     address 192.168.1.100
#     netmask 255.255.255.0
#     gateway 192.168.1.1

# 重启网络服务
systemctl restart networking
```

## 五、安装Docker环境

### 1. 安装Docker
```bash
# 方法1: 使用官方脚本(推荐,最简单)
curl -fsSL https://get.docker.com | sh

# 方法2: 手动安装
apt install -y docker.io docker-compose-plugin

# 启动Docker
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
docker compose version
```

### 2. 配置Docker镜像加速(国内服务器推荐)
```bash
# 创建配置文件
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://docker.mirrors.sjtug.sjtu.edu.cn"
  ]
}
EOF

# 重启Docker
systemctl restart docker
```

### 3. 安装Git和部署项目
```bash
# 安装Git
apt install -y git

# 克隆项目
cd /opt
git clone https://github.com/your-repo/API_AutoTest.git
cd API_AutoTest

# 使用Docker Compose启动
docker compose up -d

# 查看日志
docker compose logs -f

# 查看运行状态
docker compose ps
```

## 六、常用命令

### 系统管理
```bash
# 关机
shutdown -h now

# 重启
reboot

# 查看系统信息
uname -a
cat /etc/os-release

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看进程
top
htop
```

### VMware相关
```bash
# 安装VMware Tools (增强功能)
apt install -y open-vm-tools open-vm-tools-desktop

# 重启生效
reboot
```

## 七、常见问题

### 1. 无法联网
```bash
# 检查网络接口
ip link show

# 启动网络接口(假设是eth0)
ip link set eth0 up

# 获取IP
dhclient eth0

# 检查DNS
cat /etc/resolv.conf

# 如果DNS为空,手动设置
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

### 2. SSH连接被拒绝
```bash
# 检查SSH服务
systemctl status ssh

# 如果未启动
systemctl start ssh

# 检查防火墙
apt install -y ufw
ufw allow 22
ufw enable
```

### 3. 磁盘空间不足
```bash
# 清理apt缓存
apt clean
apt autoremove

# 查看大文件
du -h --max-depth=1 / | sort -hr
```

## 八、安全建议

### 1. 修改SSH端口(可选)
```bash
vim /etc/ssh/sshd_config
# Port 22 改为 Port 2222
systemctl restart ssh
```

### 2. 配置防火墙
```bash
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp     # SSH
ufw allow 8000/tcp   # API端口
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw enable
```

### 3. 定期更新
```bash
# 设置定时任务
crontab -e
# 添加: 0 2 * * 0 apt update && apt upgrade -y
```

## 九、优化建议

### 1. 时区设置
```bash
# 设置为中国时区
timedatectl set-timezone Asia/Shanghai
```

### 2. 主机名设置
```bash
# 修改主机名
hostnamectl set-hostname bank-api-server
```

### 3. 创建SWAP(如果内存小)
```bash
# 创建2GB SWAP
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 开机自动挂载
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 快速检查清单

安装完成后,执行以下检查:

```bash
# 1. 检查系统版本
cat /etc/os-release

# 2. 检查网络
ping -c 4 baidu.com

# 3. 检查SSH
systemctl status ssh

# 4. 检查Docker
docker --version
docker run hello-world

# 5. 检查磁盘
df -h

# 6. 检查内存
free -h

# 7. 检查IP地址(用于SSH连接)
ip addr show
```

---

**安装完成后,你就可以使用SSH客户端(如Xshell、MobaXterm)从Windows连接到虚拟机进行操作了!**
