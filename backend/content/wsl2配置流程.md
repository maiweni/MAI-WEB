非常棒 👍！
 下面是一篇完整、结构清晰的技术文章，
 详细总结了从 **WSL2 安装 → D 盘部署 → 用户配置 → 性能优化 → 清华镜像 → CUDA → Miniconda → pip** 的全流程。
 它可以直接作为文档保存或发布到你的博客。

------

# 🐧 在 Windows 上打造高性能 WSL2 Ubuntu 环境（D 盘安装 + CUDA + 清华镜像）

> 作者：**mawen**
>  适用系统：Windows 10/11
>  环境版本：WSL2 + Ubuntu 22.04
>  目标：在 D 盘安装 WSL2 Ubuntu，配置清华镜像、Miniconda、CUDA 12.1，并实现高性能开发环境。

------

## 🧱 一、创建 WSL 安装目录

我们将 WSL 的根文件系统安装到 D 盘，避免占用 C 盘空间。

```powershell
mkdir D:\wsl
mkdir D:\wsl\ubuntu22.04
```

------

## 🌐 二、下载 Ubuntu 22.04 Rootfs

从 Ubuntu 官方 WSL 镜像源下载最新的 rootfs：

```powershell
Invoke-WebRequest -Uri https://cloud-images.ubuntu.com/wsl/releases/jammy/current/ubuntu-jammy-wsl-amd64-wsl.rootfs.tar.gz -OutFile D:\wsl\ubuntu22.04\ubuntu22.tar.gz
```

------

## ⚙️ 三、导入到 WSL2

```powershell
wsl --import Ubuntu-22.04 D:\wsl\ubuntu22.04 D:\wsl\ubuntu22.04\ubuntu22.tar.gz --version 2
```

验证导入成功：

```powershell
wsl --list --verbose
```

显示：

```
Ubuntu-22.04   Stopped   2
```

------

## 👤 四、创建普通用户

进入系统（默认 root）：

```powershell
wsl -d Ubuntu-22.04
```

创建用户：

```bash
adduser mawen
usermod -aG sudo mawen
```

设置默认登录用户：

```bash
echo "[user]" > /etc/wsl.conf
echo "default=mawen" >> /etc/wsl.conf
```

重启：

```powershell
wsl --shutdown
wsl
```

此时进入系统为：

```
mawen@Ubuntu-22.04:~$
```

------

## 💾 五、配置 `.wslconfig`（系统资源与网络）

在 Windows 中编辑：

```
C:\Users\<用户名>\.wslconfig
```

推荐配置（24GB 内存机器）：

```ini
[wsl2]
memory=16GB
processors=8
swap=4GB
swapFile=D:\\wsl\\swap.vhdx

[experimental]
autoMemoryReclaim=gradual
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
sparseVhd=true
```

> 💡 优点：
>
> - 内存上限 16GB，自动回收；
> - 代理自动继承 Windows；
> - 网络直通（mirrored 模式）；
> - Swap 放在 D 盘，SSD 读写快；
> - VHD 自动压缩节省空间。

应用配置：

```powershell
wsl --shutdown
```

------

## 🧩 六、配置清华 APT 镜像源

在 Ubuntu 中执行：

```bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup
sudo bash -c 'cat > /etc/apt/sources.list << "EOF"
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
EOF'
sudo apt update && sudo apt upgrade -y
```

------

## ⚙️ 七、安装基础开发工具

```bash
sudo apt install -y curl wget git vim build-essential software-properties-common
```

------

## 💻 八、安装 CUDA 12.1 Toolkit（官方源）

### 1️⃣ 导入 NVIDIA GPG key

```bash
sudo mkdir -p /usr/share/keyrings/
curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub | sudo gpg --dearmor -o /usr/share/keyrings/cuda-archive-keyring.gpg
```

### 2️⃣ 添加仓库源

```bash
echo "deb [signed-by=/usr/share/keyrings/cuda-archive-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" | sudo tee /etc/apt/sources.list.d/cuda.list
```

### 3️⃣ 安装 CUDA Toolkit 12.1

```bash
sudo apt update
sudo apt install -y cuda-toolkit-12-1
```

> ⚠️ 不要安装 `cuda-drivers`，WSL2 透传 Windows 驱动即可。

### 4️⃣ 配置环境变量

```bash
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

验证：

```bash
nvcc -V
nvidia-smi
```

------

## 🧠 九、安装 Miniconda

```bash
curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o ~/miniconda.sh
bash ~/miniconda.sh
source ~/.bashrc
```

查看版本：

```bash
conda --version
```

------

## 🧭 十、配置清华 Conda 镜像源

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch
conda config --set show_channel_urls yes
```

验证：

```bash
conda config --show channels
```

------

## 🧩 十一、配置 pip 清华镜像

```bash
mkdir -p ~/.pip
tee ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
timeout = 60
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
use-deprecated = legacy-resolver
EOF
```

验证：

```bash
pip config list
```

------

## 📊 十二、检查系统状态

### 查看磁盘占用：

```bash
df -h /
```

### 查看可用内存：

```bash
free -h
```

### 查看 GPU 透传：

```bash
nvidia-smi
```

------

## ✅ 十三、总结

| 模块       | 配置/命令              | 说明                   |
| ---------- | ---------------------- | ---------------------- |
| 安装位置   | `D:\wsl\ubuntu22.04`   | 整个系统存放在 D 盘    |
| 用户       | `mawen`                | 默认用户，带 sudo 权限 |
| 内存限制   | `memory=16GB`          | `.wslconfig` 设置      |
| CUDA       | `12.1`                 | 官方 Toolkit           |
| Conda 镜像 | 清华 TUNA              | 包管理加速             |
| pip 镜像   | 清华 TUNA              | Python 包加速          |
| 网络       | `mirrored + autoProxy` | 支持自动代理与转发     |
| GPU        | `nvidia-smi` 可用      | 完整 GPU 透传支持      |

------

## 🌟 最终效果

✅ 系统安装在 D 盘
 ✅ 支持 CUDA 12.1
 ✅ 内存上限 16GB（自动回收）
 ✅ Conda + pip 均为清华源
 ✅ 网络自动继承 Windows 代理
 ✅ GPU 加速可用（`nvidia-smi`）
 ✅ 近乎满血 Linux 开发体验 💪