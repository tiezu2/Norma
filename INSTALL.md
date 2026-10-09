# Echo-Mate 软件安装文档（PC 端 · 无需开发板）

> **适用对象**：只有 PC、没有硬件的软件开发者
> **目标**：在 PC 上完整跑通 Echo-Mate 的 AI 对话功能（UI 预览 + 语音识别 + 大模型对话 + 语音合成）
> **适用环境**：Windows 宿主机 + VMware Workstation + Ubuntu 20.04 LTS
> **不需要**：开发板、屏幕、麦克风、喇叭等硬件（PC 端用虚拟机自带的声卡即可）
> **仓库**：`https://github.com/tiezu2/Norma`　分支：`main`

---

## 目录

1. 准备工作
2. 安装 VMware 虚拟机
3. 安装 Ubuntu 20.04
4. 配置 Ubuntu 基础环境
5. 安装 Miniconda 与 Python 3.10
6. 安装 Python 依赖
7. 获取项目源码
8. 配置服务端
9. 配置客户端
10. PC 预览编译与运行
11. 音频设备配置
12. 启动服务端
13. 完整验证流程

---

## 一、准备工作

### 1.1 硬件要求

| 项目 | 最低配置 | 推荐配置 |
|---|---|---|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| 硬盘 | 100 GB 空闲 | 200 GB 空闲 |
| 网络 | 能访问 GitHub | 能访问外网 |

### 1.2 软件下载

| 软件 | 下载地址 |
|---|---|
| VMware Workstation Player | https://www.vmware.com/products/workstation-player.html |
| Ubuntu 20.04 ISO | https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/20.04/ubuntu-20.04.6-desktop-amd64.iso |
| Miniconda | https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh |

### 1.3 账号准备

- **阿里云百炼（DashScope）API Key**：https://bailian.console.aliyun.com/ （服务端跑对话与语音合成要用）
- （可选）**高德地图 Key**：https://lbs.amap.com/ （PC 预览里的天气功能要用）

---

## 二、安装 VMware 虚拟机

### 2.1 安装 VMware Workstation

1. 双击下载的 `VMware-workstation-full-xxx.exe`。
2. 按提示下一步，接受许可协议。
3. 安装路径建议改为 D 盘。
4. 取消"启动时检查产品更新"和"加入客户体验提升计划"。
5. 完成后重启电脑。

### 2.2 创建新虚拟机

1. 打开 VMware，点击"创建新的虚拟机"。
2. 配置类型选"典型（推荐）"，下一步。
3. 安装来源选"稍后安装操作系统"。
4. 客户机操作系统：**Linux**，版本：**Ubuntu 64-bit**。
5. 虚拟机名称：`Echo-Mate`；位置：建议 `D:\VM\Echo-Mate`。
6. 磁盘大小：**60 GB**，选择"将虚拟磁盘拆分成多个文件"。
7. 点击"自定义硬件"：

| 硬件 | 设置 |
|---|---|
| 内存 | 4 GB（可后续调到 8 GB） |
| 处理器 | 处理器数量 2，每个处理器内核 2（总 4 核） |
| 网络适配器 | **NAT 模式** |
| USB 控制器 | 存在（兼容 USB 3.0） |
| 声卡 | —— |
| 显示器 | 1 个监视器 |
| CD/DVD | 连接自动检测，ISO 文件指向 Ubuntu 20.04 |

8. 点击"关闭" → "完成"。

### 2.3 常见问题

- 若提示"Intel VT-x 未启用"：进 BIOS 开启虚拟化技术。
- 若磁盘空间不足：先分配 60 GB，后续用 gparted 扩容。

---

## 三、安装 Ubuntu 20.04

### 3.1 启动安装

1. 点击"开启此虚拟机"。
2. 出现 GRUB 菜单时，选"Ubuntu"或直接等待。
3. 进入安装界面，选择语言"中文（简体）"，点击"安装 Ubuntu"。

### 3.2 安装步骤

| 步骤 | 操作 |
|---|---|
| 键盘布局 | 默认"汉语"，继续 |
| 更新和其他软件 | 选"正常安装"，取消"安装 Ubuntu 时下载更新" |
| 安装类型 | "清除整个磁盘并安装 Ubuntu" |
| 磁盘分区 | 默认，直接"现在安装" |
| 时区 | 点击地图上的"上海" |
| 用户信息 | 姓名/计算机名/用户名自定，密码自定（记得住） |
| 安装完成 | 点击"现在重启" |

### 3.3 首次启动

1. 输入密码登录。
2. 跳过在线账号、Livepatch 等向导。
3. 打开终端：`Ctrl + Alt + T`。

### 3.4 更换软件源（可选，国内加速）

```bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
sudo sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list
sudo sed -i 's|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list
sudo apt update
```

### 3.5 安装 VMware Tools

```bash
sudo apt update
sudo apt install -y open-vm-tools open-vm-tools-desktop
sudo reboot
```

重启后支持：Windows 与 Ubuntu 之间复制粘贴、拖拽文件、分辨率自动适配。

---

## 四、配置 Ubuntu 基础环境

### 4.1 确认系统版本

```bash
lsb_release -a
```

应显示 Ubuntu 20.04 LTS。

### 4.2 安装基础工具

```bash
sudo apt update
sudo apt install -y git curl wget unzip vim build-essential cmake
sudo apt install -y python3-pip python3-venv pkg-config bc rsync cpio
```

### 4.3 安装系统音频 / 图形 / 网络库

```bash
sudo apt install -y ffmpeg portaudio19-dev libogg-dev libsndfile1 \
  libsdl2-dev libsdl2-image-dev libjson-c-dev libjsoncpp-dev \
  libboost-dev libdrm-dev libopus-dev libasound2-dev \
  libopenblas0 libopenblas-dev
```

### 4.4 常用清理

```bash
sudo apt clean
sudo apt autoremove --purge -y
```

---

## 五、安装 Miniconda 与 Python 3.10

### 5.1 下载 Miniconda

```bash
cd ~
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

### 5.2 安装 Miniconda

```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

交互过程：
1. 按回车阅读协议
2. 输入 `yes` 同意
3. 安装路径直接回车（默认 `~/miniconda3`）
4. 问是否 `conda init`，输入 `yes`

### 5.3 激活 conda

```bash
source ~/.bashrc
conda --version
```

### 5.4 接受服务条款

```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

### 5.5 创建 Python 3.10 环境

```bash
conda create -n echo_env python=3.10 -y
conda activate echo_env
python --version
```

常见问题：
- `EnvironmentNameNotFound` → 重新 `conda create`
- `CondaToSNonInteractiveError` → 执行 `conda tos accept`
- `conda: command not found` → 执行 `source ~/miniconda3/bin/activate`

---

## 六、安装 Python 依赖

### 6.1 确保在 echo_env 环境

```bash
conda activate echo_env
```

### 6.2 安装 CPU 版 PyTorch

```bash
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cpu
```

若官方源太慢，改用阿里云镜像：

```bash
pip install torch torchvision torchaudio \
  -f https://mirrors.aliyun.com/pytorch-wheels/cpu/ \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

验证：

```bash
python -c "import torch; print('torch', torch.__version__)"
```

### 6.3 安装 PyOgg（源码编译）

PyPI 上的 `pyogg` 不含 `OpusEncoder`，需要从源码编译。

```bash
cd ~
git clone https://ghproxy.net/https://github.com/TeamPyOgg/PyOgg.git
cd PyOgg
pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

验证：

```bash
python -c "from pyogg import OpusEncoder, OpusDecoder; print('PyOgg OK')"
```

常见问题：
- `git clone` 卡住 → 换 `https://gitclone.com/github.com/TeamPyOgg/PyOgg.git`
- 编译报错缺 `libopusenc-dev` → Ubuntu 20.04 源里没有，跳过即可

### 6.4 安装项目 requirements.txt

```bash
cd ~/Echo-Mate/Demo/AIChat_demo/Server
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 本仓库的 `requirements.txt` **已经是 UTF-8**，且里面容易冲突的 `torch` / `torchaudio` / `git+https://…PyOgg.git` 三行**已经预先注释好**，直接安装即可，不需要再手工改文件。

### 6.5 安装 ffmpeg

```bash
sudo apt install -y ffmpeg
```

### 6.6 验证所有 Python 依赖

```bash
python -c "import torch, funasr, dashscope, websockets, pyogg; print('Python deps OK')"
python -c "from pyogg import OpusEncoder; print('OpusEncoder OK')"
```

全部输出 OK 即安装成功。

---

## 七、获取项目源码

### 7.1 安装 git-lfs

```bash
sudo apt install -y git-lfs
git lfs install
```

### 7.2 克隆仓库

> ⚠️ **目标目录必须写成 `~/Echo-Mate/Demo`** —— 本文档后续所有路径都基于它。

```bash
git clone https://github.com/tiezu2/Norma.git ~/Echo-Mate/Demo
cd ~/Echo-Mate/Demo
```

### 7.3 拉取子模块

```bash
git submodule update --init --recursive
```

5 个子模块（自动从官方源拉取，约 900 MB）：

| 路径 | 来源 |
|---|---|
| `AIChat_demo/Server/models/FunAudioLLM/SenseVoice` | github.com/FunAudioLLM/SenseVoice |
| `.../iic/speech_fsmn_vad_zh-cn-16k-common-pytorch` | modelscope.cn |
| `.../iic/SenseVoiceSmall` | modelscope.cn |
| `DeskBot_demo/lvgl` | github.com/lvgl/lvgl（`release/v9.2`） |
| `rkmpi_demos` | github.com/LuckfoxTECH/luckfox_pico_rkmpi_example |

### 7.4 拉取 LFS 大文件

```bash
git lfs pull
git submodule foreach --recursive 'git lfs pull'
```

### 7.5 验证项目结构

```bash
ls ~/Echo-Mate/Demo/
ls ~/Echo-Mate/Demo/AIChat_demo/
```

应看到 `AIChat_demo/`、`DeskBot_demo/`、`yolov5_demo/`、`rkmpi_demos/` 等。

---

## 八、配置服务端

服务端用**阿里云百炼（DashScope）**做对话与语音合成。**密钥不随仓库分发**，需要自己填。

### 8.1 创建密钥文件

```bash
cd ~/Echo-Mate/Demo/AIChat_demo/Server
cp config/local_secrets.py.example config/local_secrets.py
vim config/local_secrets.py
```

填入自己的值：

| 变量 | 说明 |
|---|---|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key，**必填** |
| `DASHSCOPE_BASE_URL` | 保持默认 `https://dashscope.aliyuncs.com/api/v1` 即可 |
| `DASHSCOPE_WORKSPACE` | **仅**使用阿里云 MaaS 专属网关时才填；普通 Key 留空 `""` |

> `config/local_secrets.py` 已被 `.gitignore` 忽略，不会也不应该被提交。

### 8.2 验证密钥加载

```bash
python -c "from config.settings import global_settings, DASHSCOPE_API_KEY; print('key len =', len(DASHSCOPE_API_KEY)); print('model =', global_settings.CHAT_MODEL)"
```

`key len` 应为一个较大的数字（不是占位符那串），`model` 应输出 `qwen-turbo`。

---

## 九、配置客户端

### 9.1 修改 system_para.conf

```bash
cd ~/Echo-Mate/Demo/DeskBot_demo/utils
cp system_para.conf.example system_para.conf
vim system_para.conf
```

PC 端预览的关键项：

```ini
AIChat_server_url=127.0.0.1          # PC 端跑服务端就用本机回环地址
AIChat_server_port=8000
AIChat_server_token=123456
AIChat_Client_ID=00:11:22:33:44:55
city=东城区                            # 天气功能用
adcode=110101
gaode_api_key=你的高德Key               # 天气功能用，可留占位符
aliyun_api_key=你的阿里云Key             # 按需
```

> `system_para.conf` 含密钥，已退出 git 跟踪并被忽略，本地怎么改都不会污染仓库。

### 9.2 同步到 bin/

PC 预览运行时读取的是 `bin/` 下的配置副本：

```bash
sed -i 's|AIChat_server_url=.*|AIChat_server_url=127.0.0.1|' \
  ~/Echo-Mate/Demo/DeskBot_demo/bin/system_para.conf
```

### 9.3 验证

```bash
grep AIChat_server_url ~/Echo-Mate/Demo/DeskBot_demo/bin/system_para.conf
```

应输出 `AIChat_server_url=127.0.0.1`。

---

## 十、PC 预览编译与运行

### 10.1 修改 lv_conf.h 启用 SDL

PC 上没有 framebuffer，要把 LVGL 的显示后端从 `fbdev` 切到 `SDL`：

```bash
cd ~/Echo-Mate/Demo/DeskBot_demo

# 先看当前状态
grep -nE "LV_USE_SDL|LV_USE_LINUX_FBDEV|LV_USE_EVDEV" lv_conf.h

# 三行改成下面这样（若已经是就跳过）
sed -i 's|^// *#define LV_USE_SDL.*|#define LV_USE_SDL 1|' lv_conf.h
sed -i 's|^// *#define LV_USE_LINUX_FBDEV.*|#define LV_USE_LINUX_FBDEV 0|' lv_conf.h
sed -i 's|^// *#define LV_USE_EVDEV.*|#define LV_USE_EVDEV 0|' lv_conf.h
```

验证：

```bash
grep -nE "^#define LV_USE_SDL|^#define LV_USE_LINUX_FBDEV|^#define LV_USE_EVDEV" lv_conf.h
```

应输出：

```
#define LV_USE_SDL 1
#define LV_USE_LINUX_FBDEV 0
#define LV_USE_EVDEV 0
```

### 10.2 编译 PC 预览

```bash
cd ~/Echo-Mate/Demo/DeskBot_demo
rm -rf build && mkdir build && cd build
cmake ..
make -j$(nproc)
```

> 本仓库**已内置**官方流程中点名的 4 个修补文件，正常情况直接编过，**不需要手写任何补丁**：
>
> | 文件 | 作用 |
> |---|---|
> | `DeskBot_demo/cmake/Findjson-c.cmake` | 让 cmake 找到 json-c |
> | `DeskBot_demo/cmake/FindWEBSOCKETPP.cmake` | 让 cmake 找到 websocketpp |
> | `DeskBot_demo/cmake/FindSDL2_image.cmake` | 让 cmake 找到 SDL2_image |
> | `DeskBot_demo/gui_app/pages/ui_YOLOPage/yolo_stub.c` | YOLO 桩，避免依赖 yolov5 |
>
> 若编译报 `Could NOT find json-c / WEBSOCKETPP / SDL2_image` 或 `undefined reference to start_ai_camera`，**先确认上面 4 个文件确实存在**（`ls DeskBot_demo/cmake/`），存在则先 `rm -rf build` 再重编。

### 10.3 运行 PC 预览

```bash
cd ~/Echo-Mate/Demo/DeskBot_demo/bin
LV_SDL_VIDEO_WIDTH=800 LV_SDL_VIDEO_HEIGHT=480 ./main
```

注意：
- **必须在 VMware 桌面里的终端运行，不能通过 SSH**
- 若报 `cannot open display`：说明是在 SSH 会话里跑的，请到 VMware 虚拟机的图形桌面里打开终端再执行

---

## 十一、音频设备配置

### 11.1 检查音频设备

```bash
arecord -l
pactl list sources short
pactl list sinks short
```

### 11.2 方案 A：使用 USB 声卡（推荐）

如果内置声卡驱动有问题，USB 声卡即插即用。

```bash
pactl list sources short | grep usb
pactl list sinks short | grep usb
pactl set-default-source <USB声卡的source名>
pactl set-default-sink <USB声卡的sink名>
```

### 11.3 方案 B：使用蓝牙耳机

```bash
pactl list sinks short | grep bluez
pactl set-default-sink <蓝牙sink名>
```

注意：A2DP 模式只有输出、没有麦克风。要用麦克风需切到 HSP/HFP 模式：

```bash
pactl set-card-profile <bluez_card名> headset-head-unit
```

### 11.4 方案 C：使用内置麦克风

部分机型（如戴尔 Inspiron 3511）在 Ubuntu 20.04 下内置麦克风有驱动问题，表现为录音振幅全 0。

```bash
alsamixer -c 0
# 按 F4 切到 Capture 视图
# 所有通道调到 100，取消 [MM] 静音
sudo alsactl store
```

如果还是录不到：直接买 USB 声卡。

### 11.5 测试录音

```bash
arecord -d 5 -f S16_LE -r 16000 -c 1 test.wav
aplay test.wav
```

分析录音内容：

```bash
sudo apt install -y sox
sox test.wav -n stat
```

看 `Maximum amplitude`：
- `> 0.1`：录音正常
- `= 0.000000`：录音全是静音

---

## 十二、启动服务端

```bash
conda activate echo_env
cd ~/Echo-Mate/Demo/AIChat_demo/Server
python main.py
```

预期输出：

```
funasr version: ...
[INFO] Loading ckpt: .../speech_fsmn_vad_zh-cn-16k-common-pytorch/model.pt, status: <All keys matched successfully>
[INFO] Loading ckpt: ./models/FunAudioLLM/iic/SenseVoiceSmall/model.pt, status: <All keys matched successfully>
[INFO] server listening on 0.0.0.0:8000
[INFO] WebSocket server started on 0.0.0.0:8000
```

**这个终端不要关，服务端要一直跑着。**

### 常见问题

| 问题 | 原因 | 解决 |
|---|---|---|
| `ModuleNotFoundError: No module named 'torch'` | 不在 echo_env 环境 | `conda activate echo_env` |
| `InputRequired: apikey is required!` | 密钥没填 / 没生效 | 检查 `config/local_secrets.py` 的 `DASHSCOPE_API_KEY` |
| `OSError: [Errno 98] address already in use` | 8000 端口被旧进程占用 | `fuser -k 8000/tcp` 后重新启动 |
| `Client is idle, resetting services` 循环 | PC 预览没启动 | 按第十章启动 PC 预览 |

---

## 十三、完整验证流程

### 13.1 两个终端同时运行

**终端 1（服务端）：**

```bash
conda activate echo_env
cd ~/Echo-Mate/Demo/AIChat_demo/Server
python main.py
```

**终端 2（PC 预览，必须在 VMware 桌面里）：**

```bash
cd ~/Echo-Mate/Demo/DeskBot_demo/bin
LV_SDL_VIDEO_WIDTH=800 LV_SDL_VIDEO_HEIGHT=480 ./main
```

### 13.2 观察连接

服务端终端应出现：

```
[INFO] Client connected
[INFO] Authentication successful
[INFO] Received hello message with audio params
[INFO] 成功注册函数: robot_move
```

同时 PC 预览窗口应显示出 LVGL 界面。

### 13.3 语音测试

在 PC 预览界面上进入 AIChat 页面，对着麦克风清晰地说：

```
Echo，你好
```

链路应依次完成：**录音 → VAD 切分 → ASR 转文字 → 大模型对话 → TTS 合成 → 播放回答**。

---

## 附：一页纸上手清单（TL;DR）

```bash
# 1. 克隆到指定路径
git clone https://github.com/tiezu2/Norma.git ~/Echo-Mate/Demo
cd ~/Echo-Mate/Demo && git submodule update --init --recursive

# 2. Python 环境
conda create -n echo_env python=3.10 -y && conda activate echo_env
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. 依赖
cd ~/Echo-Mate/Demo/AIChat_demo/Server && pip install -r requirements.txt

# 4. 填密钥
cp config/local_secrets.py.example config/local_secrets.py
vim config/local_secrets.py          # 填 DASHSCOPE_API_KEY

# 5. 客户端配置
cd ~/Echo-Mate/Demo/DeskBot_demo/utils
cp system_para.conf.example system_para.conf
vim system_para.conf                 # AIChat_server_url=127.0.0.1

# 6. PC 预览编译
cd ~/Echo-Mate/Demo/DeskBot_demo && rm -rf build && mkdir build && cd build
cmake .. && make -j$(nproc)

# 7. 启动服务端
conda activate echo_env
cd ~/Echo-Mate/Demo/AIChat_demo/Server && python main.py

# 8. 启动 PC 预览（另开一个桌面终端）
cd ~/Echo-Mate/Demo/DeskBot_demo/bin
LV_SDL_VIDEO_WIDTH=800 LV_SDL_VIDEO_HEIGHT=480 ./main
```
