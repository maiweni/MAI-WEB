# 🧩 **WSL2 在 Windows 上配置 SSH 远程访问的完整教程（含自动启动）**

本教程将指导你在 **Windows + WSL2 Ubuntu** 环境中，搭建一个可从局域网其他设备直接 SSH 登录的开发环境。
 教程包含：

- 安装 SSH 服务
- 自动启动 SSH（无密码）
- 配置 WSL2 网卡与防火墙
- 从另一台电脑成功 SSH 连接

适用于 Windows 11（含可启用“镜像网络”模式的 WSL2）。

------

# 📌 **一、安装 openssh-server**

进入 WSL2：

```bash
sudo apt update
sudo apt install openssh-server -y
```

检查 SSH 是否安装成功：

```bash
sudo service ssh status
```

如出现：

```
sshd is running
```

说明 SSH 已成功安装。

------

# 📌 **二、配置 SSH 自动启动（WSL2 专用方案）**

由于 WSL2 默认不会像原生 Linux 那样自动启动 systemd 服务，因此需要手动让 SSH 服务在每次进入 WSL 时自动启动。

### 1. 编辑 `/etc/profile`

```bash
sudo nano /etc/profile
```

在末尾添加一行：

```bash
sudo service ssh start >/dev/null 2>&1
```

保存退出：

- Ctrl + O → 回车
- Ctrl + X

这样，**每次你打开 WSL2 时 SSH 会自动启动**。

------

# 📌 **三、为自动启动的 SSH 去掉 sudo 密码提示**

SSH 启动命令需要 root 权限，因此必须配置此命令免密码执行。

### 1. 打开 sudoers 配置

```bash
sudo visudo
```

### 2. 添加免密配置（把 mawen 替换成你的用户名）

在文件末尾添加：

```
mawen ALL=(ALL) NOPASSWD: /usr/sbin/service
```

保存退出。

这样，执行：

```bash
sudo service ssh start
```

将不会再提示输入密码，从而确保 WSL2 启动 SSH 不会被阻塞。

------

# 📌 **四、查看 WSL2 的局域网 IP 地址**

执行：

```bash
ip addr show eth0 | grep inet
```

你会看到类似：

```
inet xxx.xxx.xx.xx/24 ...
```

其中的：

```
xxx.xxx.xx.xx
```

就是你 WSL2 的真实局域网 IP。

> Windows 11 的 WSL2 支持“镜像网络（mirrored networking）”，因此 WSL2 现在拥有一个可以直接被局域网访问的 IP。

------

# 📌 **五、放行 Windows 防火墙的 22 端口**

否则局域网设备无法访问你的 SSH 服务。

在 Windows（以管理员身份）运行 PowerShell：

```powershell
New-NetFirewallRule -DisplayName "WSL2 SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow
```

------

# 📌 **六、从另一台电脑测试 SSH 登录**

在同一局域网下的任意电脑(Windows/Mac/Linux)运行：

```bash
ssh mawen@xxx.xxx.xx.xx
```

第一次连接会提示：

```
Are you sure you want to continue connecting (yes/no)?
```

输入：

```
yes
```

然后输入你的 WSL 用户密码。

出现 shell 提示符后，即成功进入 WSL2。

------

# 🎉 **七、结果验证**

如果你已经看到：

```
mawen@maiwen:~$
```

说明你的 SSH 远程访问完全配置成功！

你现在可以像远程服务器一样使用 WSL2：

- 用 VS Code Remote SSH 远程开发
- 从另一台电脑部署项目
- 在局域网内当作服务器使用
- 运行 Python、Docker、LLM 推理、模型微调等任务

------

# 🧵 **附录：关键命令汇总**

| 功能             | 命令                                 |
| ---------------- | ------------------------------------ |
| 安装 SSH         | `sudo apt install openssh-server -y` |
| 启动 SSH         | `sudo service ssh start`             |
| 查看 SSH 状态    | `sudo service ssh status`            |
| 自动启动配置文件 | `/etc/profile`                       |
| 免密配置命令     | `sudo visudo`                        |
| 查看 IP 地址     | `ip addr show eth0`                  |
| 放行防火墙       | `New-NetFirewallRule ...`            |
| 测试连接         | `ssh user@IP`                        |

------

