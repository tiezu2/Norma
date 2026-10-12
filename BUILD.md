# 固件编译与烧录（RV1106 / Echo-Mate）

> 本文档面向 **板端固件**：从 SDK 编译出 `update.img` 并烧录到 Echo-Mate 核心板。
> 只想在 PC 上跑软件（不需要开发板）：见 [`INSTALL.md`](./INSTALL.md)。
> 硬件引脚定义：见 [`HARDWARE.md`](./HARDWARE.md)。

---

## 0. 前置条件

| 项目 | 要求 |
|---|---|
| 主机系统 | Ubuntu 20.04 LTS（推荐，已验证；其他 64 位 Linux 亦可） |
| 磁盘 | **≥ 40 GB** 空闲（首次全量含 buildroot 源码，占用约 25 ~ 30 GB） |
| 网络 | **必须能访问外网** —— buildroot 源码（约 5 GB）在编译时下载 |
| 内存 | 4 GB 以上 |
| 参考耗时 | 4 核 / 8 GB：**约 3 小时 20 分**（首次全量，含 uboot + kernel + buildroot） |

---

## 1. SDK 目录

本仓库只包含应用层源码；固件构建需要完整的 **Echo-Mate SDK** 树（基于 Luckfox Pico SDK V1.3，Linux 内核 5.10.110），约定放置在仓库内的：

```
<仓库根>/SDK/rv1106-sdk/
```

> ⚠️ **该 SDK 目录并不包含在本仓库中**（体积达数十 GB，未纳入版本管理）。
> 首次编译前必须先自行获取，否则 §3 起的步骤无法执行。

获取方式：从 Luckfox 官方 SDK（`LuckfoxTECH/luckfox-pico`）拉取，再把 Echo-Mate 的板级文件（见 §2）加入对应位置（`<仓库根>/SDK/rv1106-sdk/`）。

---

## 2. 板级配置（**最容易出错的一步**）

Echo-Mate 的板级配置由下列文件组成，均位于 SDK 内：

| 文件 | 路径 |
|---|---|
| BoardConfig | `project/cfg/BoardConfig_IPC/BoardConfig-SPI_NAND-Buildroot-RV1106_Echo_Mate-DeskMate.mk` |
| 板级 dts | `sysdrv/source/kernel/arch/arm/boot/dts/rv1106g-echo-mate.dts` |
| 板级 dtsi | `sysdrv/source/kernel/arch/arm/boot/dts/rv1106-echo-mate-ipc.dtsi` |
| 内核 defconfig | `sysdrv/source/kernel/arch/arm/configs/echo_rv1106_linux_defconfig` |
| uboot defconfig | `sysdrv/source/uboot/u-boot/configs/echo_rv1106_uboot_defconfig` |
| buildroot defconfig | `sysdrv/tools/board/buildroot/echo_mate_defconfig` |

BoardConfig 关键项：

```make
export RK_CHIP=rv1106
export RK_KERNEL_DTS=rv1106g-echo-mate.dts
export RK_BOOT_MEDIUM=spi_nand
export RK_PARTITION_CMD_IN_ENV="256K(env),256K@256K(idblock),512K(uboot),4M(boot),30M(oem),10M(userdata),210M(rootfs)"
export LF_TARGET_ROOTFS=buildroot
export RK_BUILDROOT_DEFCONFIG=echo_mate_defconfig
export RK_UBOOT_DEFCONFIG=echo_rv1106_uboot_defconfig
export RK_KERNEL_DEFCONFIG=echo_rv1106_linux_defconfig
export RK_TOOLCHAIN_CROSS=arm-rockchip830-linux-uclibcgnueabihf
export RK_BOOTARGS_CMA_SIZE="66M"
export RK_ENABLE_WIFI=y
export RK_ENABLE_WIFI_CHIP=RTL8723BS
```

---

## 3. 选择板级配置（lunch）

```bash
cd <仓库根>/SDK/rv1106-sdk
./build.sh lunch
```

在交互菜单里选择 **`RV1106_Echo_Mate-DeskMate`**、启动介质 **`SPI_NAND`**、rootfs 为 **`Buildroot`** 的那一项。

**选完必须校验**（这一步能提前拦掉最常见的错误）：

```bash
readlink -f .BoardConfig.mk
grep -E "RK_BOOT_MEDIUM=|RK_KERNEL_DTS=|LF_TARGET_ROOTFS=|RK_BUILDROOT_DEFCONFIG=" .BoardConfig.mk
```

期望输出：

```
.../BoardConfig-SPI_NAND-Buildroot-RV1106_Echo_Mate-DeskMate.mk
export RK_KERNEL_DTS=rv1106g-echo-mate.dts
export RK_BOOT_MEDIUM=spi_nand
export LF_TARGET_ROOTFS=buildroot
export RK_BUILDROOT_DEFCONFIG=echo_mate_defconfig
```

> 🔴 **不要选 `RV1106_Luckfox_Pico_Pro_Max`。** 那套配置的屏 / 音频 / LED 引脚与 Echo-Mate 不同，编译烧录后会得到"驱动正常但屏幕全黑、无声、状态灯不亮"的结果。原理与对照表见 [`HARDWARE.md` §8](./HARDWARE.md)。

---

## 4. 编译

```bash
cd <仓库根>/SDK/rv1106-sdk
nohup ./build.sh > ~/build_$(date +%m%d_%H%M).log 2>&1 &
echo "PID = $!"
```

跟进日志（`Ctrl-C` 只退出 tail，不影响编译）：

```bash
tail -f ~/build_*.log
```

阶段性体检（尤其盯磁盘）：

```bash
tail -25 ~/build_*.log; echo "--- 磁盘 ---"; df -h / | tail -1
```

关键节点判读：

| 日志内容 | 含义 |
|---|---|
| `switch to DTS: .../rv1106g-echo-mate.dts` | ✅ dts 选对了 |
| `==sysdrv== build kernel` / `build buildroot` | 阶段推进（内核 → rootfs） |
| `>>> <包名> <版本>` 不断变化 | 正在编译某个包 |
| `Error 1 (ignored)` | 可忽略（buildroot 有意跳过） |
| `Running build_updateimg succeeded.` / `build_all succeeded` | ✅ 编译完成 |
| `No space left on device` | ❌ 磁盘不足，需清理后重来 |

**产物**：

```
output/image/update.img                                        # 整包固件（约 113 MB）
IMAGE/SPI_NAND_RV1106G-ECHO-MATE.DTS_<日期时间>_RELEASE_TEST/  # 发布副本目录
```

> `output/` 与 `.BoardConfig.mk` 已在 `.gitignore` 中，编译产物不会污染仓库状态。

---

## 5. 烧录

### 5.1 让板子进入 MASKROM

1. 拔掉 USB 线；
2. **按住 BOOT 键不放**；
3. 插上 USB 线；
4. 松开 BOOT。

工具中应能看到 `Maskrom <N>` 设备。

> RV1106 走 MASKROM 下载模式，此时 Linux 尚未启动 —— **屏幕不亮是正常现象**，不代表固件有问题。

### 5.2 方式 A：SocToolKit（Windows GUI，推荐）

1. 先用 Rockchip 驱动助手（`DriverAssitant_v5.13`）安装 USB 驱动；
2. 打开 `SocToolKit.exe`，确认设备区显示 `Maskrom N`；
3. 切到 **`Firmware`** 页 → 点 **`Firmware...`** 选择 `update.img`；
4. 点 **`Upgrade`**，等待进度条走完。

> ⚠️ **不要点 `Download`** —— 那是烧写裸 `DownloadBin` 引导分区，会让板子起不来。整包固件一律走 `Upgrade`。
> ⚠️ 烧录过程中不要断电、不要拔线。

### 5.3 方式 B：upgrade_tool（命令行）

```bash
# 1) 列出设备，记下 LocationID
upgrade_tool ld

# 2) 烧写整包（-s 后填上一步的 LocationID）
upgrade_tool -s <N> uf update.img
```

同时只能有一个程序占用 USB —— 用命令行时**请先关闭 SocToolKit**（它约每 0.9 秒轮询一次设备，会与手动操作冲突）。

### 5.4 烧录失败排查

典型报错：`Error:action=ActionType.ACTION_UPDATE_FW,ret=-3`，且**几秒内即失败**（说明还没开始写数据）。按顺序排查：

1. **换 USB 线** —— 用短的、能传数据的线，不要用充电线 / 长线 / 延长线；
2. **换 USB 口** —— 优先主板后置 USB 2.0 口，避免前置面板与 Hub；
3. 关闭 GUI 工具，改用命令行重试，看是否输出更具体的中文错误；
4. 重新进一次 MASKROM 再试；
5. 确认固件完整（文件大小、MD5 与编译产物一致）；
6. 确认分区放得下镜像（`oem` 30 M、`rootfs` 210 M）。

> 该报错属于"通讯异常"，**重试即可能成功** —— 实测这块板对 USB 线材 / 端口比较挑。

---

## 6. 上板验收

```bash
ping -c 3 172.32.0.93
ssh root@172.32.0.93
```

```bash
cat /proc/device-tree/model                   # 期望：Echo Mate
uname -r                                      # 期望：5.10.110
cat /sys/class/backlight/*/max_brightness     # 期望：255
ls /dev/fb0
i2cdetect -y 3                                # 期望看到 0x38（触摸）
```

| 检查项 | 期望值 | 说明 |
|---|---|---|
| `/proc/device-tree/model` | `Echo Mate` | 设备树正确（用错配置时会显示 Luckfox 相关名称） |
| `max_brightness` | `255` | 背光由 PWM 驱动（错误配置下为 1，即 GPIO 开关型） |
| 屏幕 | **有画面** | 背光 + D/C + 复位 + SPI 全链路通 |
| 触摸 | `i2cdetect -y 3` 可见 `0x38` | 触摸 IC 在线 |

---

## 7. 板端应用编译（可选）

应用层（`DeskBot_demo`、`AIChat_demo/Client`）用交叉工具链单独编译。**使用前必须修改 toolchain 文件中的绝对路径**（这两个文件里写的是作者本机路径，直接编译会失败）：

| 文件 | 需修改的行 |
|---|---|
| `DeskBot_demo/toolchain.cmake` | `set(SDK_PATH "...")` |
| `AIChat_demo/Client/toolchain.cmake` | `set(SDK_PATH "...")` |

改成自己的 SDK 实际路径，例如：

```cmake
set(SDK_PATH "/home/<你的用户名>/Echo-Mate/SDK/rv1106-sdk")
```

然后：

```bash
cd DeskBot_demo
mkdir -p build && cd build
cmake .. -DTARGET_ARM=ON
make
# 把 build 产出的可执行文件连同 bin/ 目录一起拷到开发板
```

详见 [`DeskBot_demo/README.md`](./DeskBot_demo/README.md)。

---

## 8. 相关文档

- 硬件与引脚：[`HARDWARE.md`](./HARDWARE.md)
- 软件架构与运行：[`README.md`](./README.md)
- 变更记录：[`CHANGELOG.md`](./CHANGELOG.md)
