# 从宿主机接入自己的虚拟机 —— SSH 通用操作文档

> **适用范围**：任意一台宿主机（Windows / macOS / Linux），通过 SSH 接入**自己机器上的 Linux 虚拟机**。
> 虚拟化平台以 VMware Workstation + Ubuntu 为例，VirtualBox 同理（差异处已标注）。
>
> **本文目标**：照着做，能从「密码登录」一路做到「免密 + 别名 + 可被脚本和自动化工具稳定调用」。
>
> **阅读方式**：全文只用到三个占位符，替换成你自己的值即可。
>
> | 占位符 | 含义 | 示例 |
> |---|---|---|
> | `VM_USER` | 虚拟机里的登录用户名 | `xuanyue` |
> | `VM_IP` | 虚拟机的 IP 地址 | `192.168.17.128` |
> | `VM_ALIAS` | 你给这台虚拟机起的 SSH 别名 | `myvm` |

---

## 0. 整体路径

```
① 前置检查（虚拟机内：SSH 服务 / 允许登录 / 防火墙 / 拿到 IP）
        ↓
② 宿主机用密码登录一次 —— 证明网络与账号都通
        ↓
③ 换成密钥登录 —— 免密，且是自动化的必要条件
        ↓
④ 写 SSH 别名 + 非交互调用参数 —— 一条命令进出
        ↓
⑤（可选）把动态 IP 固定下来 —— 一劳永逸
```

四步里任何一步卡住，都能在下文找到对应的排查表。

---

## 1. 前置检查（在**虚拟机内部**执行）

### 1.1 SSH 服务是否在运行

```bash
systemctl status ssh --no-pager
```

- 期望看到 `Active: active (running)`。
- **未安装**（提示 `Unit ssh.service could not be found`）：

  ```bash
  sudo apt update && sudo apt install -y openssh-server
  ```

- **未启动 / 未开机自启**：

  ```bash
  sudo systemctl enable --now ssh
  ```

> **注意服务名**：Ubuntu / Debian 是 `ssh`；CentOS / RHEL / Fedora 是 `sshd`。装错名字会一直报"服务不存在"。

### 1.2 是否允许登录（首次接入通常需要密码）

```bash
grep -vE '^\s*#|^\s*$' /etc/ssh/sshd_config | grep -i -e PasswordAuthentication -e PubkeyAuthentication
```

判读：

- `PasswordAuthentication yes` → 可密码登录。**该行被注释掉（`#PasswordAuthentication yes`）也等同于 yes**，这是大多数发行版的默认状态。
- `PubkeyAuthentication yes` → 允许公钥登录（默认即为 yes）。

若密码登录被显式关掉（`no`），临时打开：

```bash
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

> **务必再查一眼配置覆盖**——新版发行版会把配置拆到独立目录，优先级高于主文件：
>
> ```bash
> grep -rn -e PasswordAuthentication -e PubkeyAuthentication /etc/ssh/sshd_config.d/ 2>/dev/null
> ```

### 1.3 防火墙是否放行 22 端口

```bash
sudo ufw status
```

- 输出 `Status: inactive` → 无需处理。
- 输出 `Status: active` → 放行：

  ```bash
  sudo ufw allow 22/tcp
  ```

> 若系统用 firewalld（CentOS 系）：`sudo firewall-cmd --permanent --add-service=ssh && sudo firewall-cmd --reload`

### 1.4 拿到虚拟机的 IP

在虚拟机内执行，最快的一条：

```bash
hostname -I
```

输出可能有多段（多个网卡），VMware NAT 下通常是 `192.168.x.x`，取第一段即可。想看得更清楚：

```bash
ip -4 addr show | grep inet
```

**临时救急**：如果暂时进不去虚拟机系统，可以从宿主机侧找 IP：

```bash
# Windows（CMD / PowerShell）
arp -a | findstr 192.168.
# macOS / Linux
arp -a | grep 192.168.
```

或直接看 VMware 的 DHCP 租约文件：

- Windows：`C:\ProgramData\VMware\vmnetdhcp.leases`
- Linux 宿主机：`/var/lib/vmware/vmnet8/dhcpd/dhcpd.leases`
- VirtualBox：虚拟机窗口右下角网络图标悬停即可看到 IP

---

## 2. 第一步：密码登录（验证通路）

打开**宿主机**的终端（Windows 用 PowerShell 或 CMD，macOS/Linux 用 Terminal），三个平台命令完全相同：

```bash
ssh VM_USER@VM_IP
# 例： ssh xuanyue@192.168.17.128
```

首次连接会出现：

```
The authenticity of host '192.168.17.128' can't be established.
ED25519 key fingerprint is SHA256:xxxxxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

输入 `yes` 回车（这一步是把主机指纹写入 `known_hosts`，仅第一次需要）。

**判读结果：**

| 结果 | 结论 | 下一步 |
|---|---|---|
| 出现 `VM_USER@hostname:~$` 提示符 | ✅ 通路正常 | 继续第 3 节 |
| `Connection timed out` | 虚拟机没开机 / IP 变了 / 网段不对 | 见第 9 节第 1 行 |
| `Connection refused` | 虚拟机在跑，但 22 端口没监听 | 回 1.1 |
| `Permission denied, please try again` | 用户名或密码错 | 回 1.2 |

---

## 3. 第二步：改用密钥登录（免密）

密码登录在自动化场景下不可用（无法交互输入密码），所以必须换成密钥。

### 3.1 在**宿主机**上生成密钥（只做一次）

Windows / macOS / Linux 命令相同：

```bash
ssh-keygen -t ed25519 -C "你的备注@机器名"
```

- 连续回车三次即可：使用默认路径、不设口令、确认。
- 生成两个文件：
  - `id_ed25519` —— **私钥**，绝不外传、绝不提交到 git。
  - `id_ed25519.pub` —— **公钥**，要被安装到虚拟机里。

默认存放位置：

| 平台 | 私钥路径 |
|---|---|
| Windows | `C:\Users\<你的用户名>\.ssh\id_ed25519` |
| macOS / Linux | `~/.ssh/id_ed25519` |

> 已经有密钥的就**不要重复生成**，直接复用现有的。

### 3.2 把公钥安装到虚拟机

**方式 A：`ssh-copy-id`（macOS / Linux 自带，最省事）**

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub VM_USER@VM_IP
```

中途需要输一次虚拟机密码，成功会输出 `Number of key(s) added: 1`。

**方式 B：手工追加（Windows 无此命令，或想完全掌控时）**

Windows PowerShell 一行完成：

```powershell
$pub = (Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub" -Raw).Trim() -replace "`r",""
ssh VM_USER@VM_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$pub' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo INSTALLED"
```

Linux / macOS 等价写法：

```bash
cat ~/.ssh/id_ed25519.pub | ssh VM_USER@VM_IP \
  "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

也可以最原始的方式：把公钥内容复制到剪贴板，在虚拟机里手工粘贴到 `~/.ssh/authorized_keys`。

> ⚠️ **最常见的坑**：公钥里**不能带回车符 `\r`**。从 Windows 复制粘贴、或经某些编辑器保存时极易带上，结果是**登录静默失败、只报 `Permission denied`**，没有任何其他提示。方式 B 中的 `-replace "`r",""` 就是在处理这个问题。

### 3.3 验证

```bash
ssh VM_USER@VM_IP
```

**不再询问密码**即表示成功。

### 3.4 若仍要求密码 —— 按此顺序排查

```bash
# ① 虚拟机内的权限（最常见）
ls -ld ~ ~/.ssh; ls -l ~/.ssh/authorized_keys
#   期望：~ 不带组/其他写权限；~/.ssh = 700；authorized_keys = 600
chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys

# ② 公钥是否混入了 \r
cat -A ~/.ssh/authorized_keys | head -1
#   行尾出现 ^M$ 就是带 \r，执行下一行清除：
sed -i 's/\r$//' ~/.ssh/authorized_keys

# ③ 服务端是否允许公钥登录
grep -i PubkeyAuthentication /etc/ssh/sshd_config   # 应为 yes 或被注释

# ④ 客户端到底用了哪个密钥（在宿主机执行）
ssh -v VM_USER@VM_IP 2>&1 | grep -i -e "identity file" -e offering
#   确认列出了你的 id_ed25519，而不是别的 key

# ⑤ 看服务端日志（在虚拟机执行，信息最直接）
sudo tail -50 /var/log/auth.log
```

---

## 4. 第三步：写 SSH 别名（以后一条 `ssh 别名` 直接进）

### 4.1 配置文件位置

| 平台 | 路径 | 权限要求 |
|---|---|---|
| Windows | `C:\Users\<你的用户名>\.ssh\config` | 无特殊要求 |
| macOS / Linux | `~/.ssh/config` | **必须 600**（`chmod 600 ~/.ssh/config`） |

### 4.2 配置模板

```
Host myvm
  HostName 192.168.17.128
  User xuanyue
  Port 22
  IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

字段说明：

- `Host myvm` —— 自己起的别名，随意命名，之后所有命令都用它。
- `HostName` —— 填 IP 最稳；也可填能解析的虚拟机主机名。
- `IdentityFile` —— Windows 上同样写 `~/.ssh/id_ed25519`，OpenSSH 能正确展开。
- `ServerAliveInterval / ServerAliveCountMax` —— 心跳保活，防止长时间无操作被静默断开。

### 4.3 生效后的用法

```bash
ssh myvm                 # 登录
ssh myvm "uname -a"      # 在虚拟机里执行单条命令
scp file.txt myvm:~/     # 传文件
```

---

## 5. 让脚本与自动化工具稳定接入

自动化场景（CI 流水线、运维脚本、AI 助手等）必须满足三个条件：**无交互、有超时、失败可控**。

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 myvm "命令"
```

- `BatchMode=yes` —— 禁止一切交互提示。密码提示、指纹确认都会**直接失败**而不是挂起等待，从而强制走密钥认证。这是自动化能跑通的关键参数。
- `ConnectTimeout=10` —— 10 秒连不上即报错返回，避免脚本无限等待。

两条配套要求：

1. **首次连接必须先手动 `ssh myvm` 一次**，把主机指纹写进 `known_hosts`。否则 `BatchMode` 下会因无法交互确认指纹而直接失败。
2. **Windows 上调用时写绝对路径更稳**：`"C:\Windows\System32\OpenSSH\ssh.exe"`，避免 PATH 里混入其他 ssh 实现（如 Git 自带的）。

> **编码提示（Windows 特有）**：经管道读取远端输出时，Windows 端可能按 GBK 解码 UTF-8 文本，导致中文变成乱码（如 `公共的` → `鍏叡鐨`）。可靠做法有两种：让远端先把结果 base64 编码、本地再解码；或让远端只输出 ASCII（英文 + 数字 + 路径）。

---

## 6. 文件互传

```bash
# 上行：宿主机 → 虚拟机
scp ./app.tar.gz myvm:~/
scp -r ./src myvm:~/work/

# 下行：虚拟机 → 宿主机
scp myvm:~/build/firmware.bin ./

# 双向增量同步（需两端都装 rsync，大目录推荐）
rsync -avz --progress ./src/ myvm:~/work/src/
```

- 路径含空格或中文时必须加引号。
- 图形化工具：Windows 用 **WinSCP / FileZilla**；macOS 用 **Cyberduck / Transmit**；Linux 文件管理器直接输入 `sftp://myvm`。

**VMware 共享文件夹**（可选通道）：

虚拟机设置 → Options → Shared Folders → 添加宿主机目录，虚拟机内出现在 `/mnt/hgfs/<共享名>`。需要装 `open-vm-tools`（`sudo apt install open-vm-tools open-vm-tools-desktop`）。

> ⚠️ **不要把 git 仓库或编译目录放在共享文件夹里**。共享目录基于 HGFS/FUSE，会丢失文件权限位（产生虚假的 mode 变更）、文件锁不可靠（残留 `.git/index.lock`）、海量小文件性能差。共享目录适合放素材和一次性文件。

---

## 7. 把动态 IP 固定下来（强烈建议）

DHCP 分配的 IP 每次重启或续租都可能变化，别名里的 IP 一失效就得重新查。三种解决方案：

### 方式 A：虚拟机软件侧按 MAC 绑定 IP（推荐，不动虚拟机内部配置）

- **VMware**：`虚拟机 → 设置 → 网络适配器 → 高级` 记下 MAC，然后在
  编辑 → 虚拟网络编辑器 → VMnet8 → DHCP 设置 → **添加保留地址**，把 MAC 与固定 IP 绑定。
  也可直接编辑 `C:\ProgramData\VMware\vmnetdhcp.conf`。
- **VirtualBox**：`VBoxManage dhcp-host add --net hostonly --mac ... --ip ...`

### 方式 B：虚拟机内配置静态 IP（Ubuntu netplan）

```bash
ls /etc/netplan/          # 通常只有一个 yaml
ip -br link               # 确认网卡名（常见 ens33 / ens160）
ip route                  # 确认网关（VMware NAT 通常是 192.168.x.2）
```

然后新建配置（把网卡名、地址、网关换成上面查到的实际值）：

```bash
sudo tee /etc/netplan/99-static.yaml > /dev/null <<'EOF'
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: no
      addresses: [192.168.17.128/24]
      gateway4: 192.168.17.2
      nameservers:
        addresses: [192.168.17.2]
EOF
sudo netplan apply
```

> ⚠️ 改静态 IP 有断网风险。**改之前先确认虚拟机的图形控制台可以操作**（不要只靠 SSH 连着改），配错了才能回滚。

### 方式 C：宿主机 hosts 别名（治标）

在宿主机 hosts 文件里加 `192.168.17.128 myserver`，配置里 `HostName myserver`。IP 变了仍需改 hosts，所以不如 A / B 彻底。

---

## 8. 网络模式：为什么"别人的电脑连不上我的虚拟机"

这是"宿主机连自己的虚拟机"和"别人连你的虚拟机"的分水岭。

| 模式 | 谁能访问虚拟机 | 虚拟机能否访问外网 | 适用场景 |
|---|---|---|---|
| **NAT**（VMnet8，默认） | **只有宿主机** | 全通 | ① 宿主机 → 自己的虚拟机（本文主场景） |
| **桥接**（Bridged） | **同一局域网内的所有设备** | 全通 | ② 想让同事的电脑 / 手机也连你的虚拟机 |
| **仅主机**（Host-only，VMnet1） | 只有宿主机 | 不通 | 隔离实验环境 |

**结论：只给自己用，保持 NAT 即可，无需任何改动。**

若要让**别人**（另一台电脑）连你的虚拟机：

1. 虚拟机关机 → 设置 → 网络适配器 → 选 **桥接模式（Bridged）** → 开机；
2. 虚拟机内重新取 IP：`hostname -I` —— 地址会变成你所在局域网的网段（如 `192.168.x.x`）；
3. 把新 IP 告诉对方，对方按本文第 2~4 节操作即可；
4. 宿主机若有防火墙，需放行 22 端口入站。

---

## 9. 常见故障速查表

| 现象 | 最可能的原因 | 处理 |
|---|---|---|
| `Connection timed out` | 虚拟机没开机 / IP 变了 / 不在同一网段 | 开机；`hostname -I` 重查；确认网络模式（第 8 节） |
| `Connection refused` | 虚拟机在运行但未监听 22 | `sudo systemctl start ssh`；`ss -tlnp \| grep :22` |
| `Permission denied (publickey)` | 公钥未装成功 / 带 `\r` / 权限过松 | 见 3.4 的完整排查流程 |
| `Permission denied, please try again` | 密码错误 / 密码登录被禁用 | 重输密码；或临时开 `PasswordAuthentication yes` |
| 首次连接卡在 `yes/no` 等待 | 主机指纹未确认 | 输 `yes`；自动化场景需先手动连一次 |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` | 虚拟机重装过，或 IP 被另一台机器占用 | `ssh-keygen -R VM_IP` 删除旧指纹后重连 |
| 输出中文乱码 | Windows 端按 GBK 解码 UTF-8 | 远端 base64 编码回传（见第 5 节） |
| 挂机一段时间后被断开 | 无心跳保活 | config 里加 `ServerAliveInterval 30` |
| `Permissions for 'id_ed25519' are too open` | 私钥权限过松（macOS/Linux） | `chmod 600 ~/.ssh/id_ed25519`；`chmod 700 ~/.ssh` |
| `Bad owner or permissions on .ssh/config` | config 文件权限过松 | `chmod 600 ~/.ssh/config` |

---

## 10. 安全须知

1. **私钥 `id_ed25519` 是凭证**。不要提交到 git、不要发到群里、不要放进共享文件夹。公钥（`.pub`）可以随意分发。
2. **建议给密钥设口令**（`ssh-keygen` 时输入 passphrase），配合 `ssh-agent` 避免重复输入；只有在需要全自动执行的场景才使用空口令密钥。
3. **不要把 22 端口直接暴露到公网**。确有远程访问需求时，使用 VPN 或内网穿透方案（frp / Tailscale / ZeroTier），并配置 `fail2ban` 限制暴力破解。
4. `authorized_keys` 中**删除不再使用的公钥，等价于回收访问权限**。人员变动时记得清理。
5. 虚拟机内避免使用弱密码，或干脆关闭密码登录（`PasswordAuthentication no`）——前提是公钥登录已确认可用。

---

## 附 A：一页纸 TL;DR

替换开头三个变量后，从第 1 步开始逐条执行。

```bash
# ================= 只改这三个 =================
VM_USER=xuanyue
VM_IP=192.168.17.128
VM_ALIAS=myvm
# ==============================================

# ── 步骤 1：在【虚拟机内】执行 ──
sudo systemctl enable --now ssh
hostname -I                     # 记下输出的 IP，填回 VM_IP

# ── 步骤 2：在【宿主机】生成密钥（已有可跳过）──
ssh-keygen -t ed25519 -C "$(whoami)@$(hostname)"

# ── 步骤 3：安装公钥 ──
# macOS / Linux：
ssh-copy-id -i ~/.ssh/id_ed25519.pub $VM_USER@$VM_IP
# Windows（PowerShell）：见正文 3.2 方式 B

# ── 步骤 4：验证免密登录 ──
ssh $VM_USER@$VM_IP

# ── 步骤 5：写别名 ──
#   macOS / Linux 配置文件： ~/.ssh/config
#   Windows 配置文件：       %USERPROFILE%\.ssh\config
cat >> ~/.ssh/config <<EOF
Host $VM_ALIAS
  HostName $VM_IP
  User $VM_USER
  IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 30
  ServerAliveCountMax 3
EOF
chmod 600 ~/.ssh/config

# ── 步骤 6：日常使用 ──
ssh $VM_ALIAS
ssh $VM_ALIAS "uname -a"
scp ./file $VM_ALIAS:~/
ssh -o BatchMode=yes -o ConnectTimeout=10 $VM_ALIAS "命令"   # 自动化调用
```

---

## 附 B：一个已跑通的参考实例

供对照参考，可直接删除。

| 项 | 值 |
|---|---|
| 虚拟化平台 | VMware Workstation，NAT 模式（VMnet8） |
| 操作系统 | Ubuntu 20.04 LTS，主机名 `xuanyue-virtual-machine` |
| 登录用户 | `xuanyue` |
| 虚拟机 IP | `192.168.17.128`（DHCP 动态，地址池 .128–.254） |
| 宿主机 VMnet8 地址 | `192.168.17.1` |
| NAT 网关 / DNS | `192.168.17.2` |
| SSH 别名 | `xuanyue-vm` |
| 私钥 | `C:\Users\<用户名>\.ssh\id_ed25519`（无口令） |
| 共享文件夹 | 宿主机 `E:\Desktop\Echo` ↔ 虚拟机 `/mnt/hgfs/Echo` |

**该实例暴露的真实问题**：DHCP 租期仅 30 分钟（默认 `default-lease-time 1800`），虚拟机重启或长时间关机后续租可能分配到**不同 IP**，导致按 IP 写死的别名失效。这正是第 7 节建议固定 IP 的原因。
