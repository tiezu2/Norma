# Echo-Mate 硬件说明

> 本文档描述 Echo-Mate 桌面 AI 助手所用核心板的硬件配置与完整引脚定义。
> 固件编译 / 烧录见 [`BUILD.md`](./BUILD.md)；软件架构与运行见 [`README.md`](./README.md)。

---

## 1. 板卡概述

| 项目 | 参数 |
|---|---|
| 名称 | Echo-Mate 核心板（自研） |
| 主控 | Rockchip **RV1106G2**（Cortex-A7 + RISC-V MCU + NPU 0.5 TOPS） |
| 内存 | DDR3L **128 MB**（Linux 可用约 87 MB） |
| 存储 | **SPI NAND 256 MB**（`sfc`，75 MHz，4-bit 读） |
| 无线 | **RTL8723BS**：WiFi 走 SDIO（`sdmmc1m0`），蓝牙走 UART0（`uart0m1`） |
| 音频 | 片内 `acodec` + I2S0，外置功放（使能脚见 §5） |
| 显示 | 2.4 英寸 SPI 屏（见 §2） |
| USB | USB 2.0 Device（`dr_mode = peripheral`），用于烧录与 RNDIS 网络 |
| 以太网 | 未使用（`&gmac` disabled） |

**默认网络**：开发板 `172.32.0.93`（root / `root`），主机 `172.32.0.100`（USB RNDIS 网卡）。

> ⚠️ 原理图 U1 位号标注为 `G3`，实物主控丝印为 **RV1106G2**。G2 与 G3 引脚兼容、GPIO 编号一致，区别主要在内存容量（128 MB vs 256 MB）。因此**不要按 G3 / Pro Max 的默认参数构建固件**（详见 §8）。

---

## 2. 显示屏与触摸

| 项目 | 参数 |
|---|---|
| 屏型号 | POLCD **P024C128-CTP** |
| 尺寸 / 分辨率 | 2.4 英寸 / **240 × 320** |
| 显示驱动 IC | **ST7789V** |
| 显示接口 | 4 线 SPI（`SPI0_M0`），独立 D/C、RST，PWM 背光 |
| 触摸 IC | **FT6336U**（FocalTech） |
| 触摸接口 | `I2C3_M1`，从机地址 `0x38` |
| 连接器 | 16 pin FPC（板上丝印 `LCD+TP`，位号 FPC4） |

设备树关键参数（摘自 `rv1106g-echo-mate.dts` 与 `rv1106-echo-mate-ipc.dtsi`）：

```dts
fbtft@0 {
    compatible = "sitronix,st7789v";
    spi-max-frequency = <60000000>;
    fps = <60>;
    buswidth = <8>;
    rotate = <270>;
    dc-gpios    = <&gpio1 RK_PD0 GPIO_ACTIVE_HIGH>;   /* D/C */
    reset-gpios = <&gpio1 RK_PC4 GPIO_ACTIVE_LOW>;    /* RES */
};
```

```dts
focaltech@38 {
    compatible = "focaltech,fts";
    reg = <0x38>;
    focaltech,reset-gpio = <&gpio1 RK_PC6 GPIO_ACTIVE_LOW>;
    focaltech,irq-gpio   = <&gpio1 RK_PC7 IRQ_TYPE_LEVEL_LOW>;
    focaltech,max-touch-number = <5>;
    focaltech,display-coords = <0 0 240 320>;
    focaltech,rotate = <270>;
};
```

注意：显示节点里的 `led-gpios`（背光）在设备树中是**注释掉的** —— 背光不由 fbtft 驱动，而走独立的 `pwm-backlight`（见 §4）。

---

## 3. FPC4 引脚定义（16 pin）

| Pin | 信号 | 说明 |
|---|---|---|
| 1 | GND | |
| 2 | 3V3 | 屏逻辑电源 |
| 3 | I2C3_SCL | 触摸时钟 |
| 4 | I2C3_SDA | 触摸数据 |
| 5 | CTP_INT | 触摸中断 |
| 6 | CTP_RST | 触摸复位 |
| 7 | LCD_DC | 数据 / 命令选择 |
| 8 | NC | 空脚 |
| 9 | LEDK | 背光 LED 阴极（经 MOS 管到地） |
| 10 | 3V3 (LEDA) | 背光 LED 阳极供电 |
| 11 | LCD_RST | 屏复位 |
| 12 | SPI0_CS | 片选 |
| 13 | SPI0_CLK | 时钟 |
| 14 | SPI0_SDA | 数据（MOSI） |
| 15 | 3V3 | |
| 16 | GND | |

**插接方向**：金手指朝下（朝 PCB 方向），插入 `LCD+TP` 翻盖座。排线为单面金手指，插反会同时导致无显示与触摸失效。

---

## 4. GPIO 映射（权威表）

| 功能 | GPIO | 全局编号 | 方向 / 有效电平 | 设备树出处 |
|---|---|---|---|---|
| LCD SPI0_CS | GPIO1_C0 | 48 | — | `spi0m0_cs0` |
| LCD SPI0_CLK | GPIO1_C1 | 49 | — | `spi0m0_clk` |
| LCD SPI0_MOSI | GPIO1_C2 | 50 | — | `spi0m0_mosi` |
| LCD SPI0_MISO | GPIO1_C3 | 51 | — | `spi0m0_miso` |
| **LCD 复位** | GPIO1_C4 | **52** | 输出，低有效 | `reset-gpios` |
| **背光** | GPIO1_C5 | **53** | PWM9_M1 输出 | `pwms = <&pwm9 ...>` |
| 触摸复位 | GPIO1_C6 | 54 | 输出，低有效 | `focaltech,reset-gpio` |
| 触摸中断 | GPIO1_C7 | 55 | 输入 | `focaltech,irq-gpio` |
| **LCD D/C** | GPIO1_D0 | **56** | 输出，高有效 | `dc-gpios` |
| 触摸 I2C3_SDA | GPIO1_D2 | 58 | — | `i2c3m1_xfer` |
| 触摸 I2C3_SCL | GPIO1_D3 | 59 | — | `i2c3m1_xfer` |
| **功放使能 PA_CTL** | GPIO0_A2 | **2** | 输出，**低电平使能** | `pa-ctl-gpios` |
| **状态灯 WORK_LED** | GPIO0_A3 | **3** | 输出，高电平点亮 | `gpio-leds / work` |

> 全局编号换算：`bank × 32 + port × 8 + index`（A=0, B=1, C=2, D=3）。
> 例：GPIO1_C4 = 1×32 + 2×8 + 4 = **52**；GPIO0_A2 = 0×32 + 0×8 + 2 = **2**。

**背光电路**：`LCD_BL`（GPIO1_C5 / PWM9_M1）驱动 U12（2N7002 N-MOS）低边开关，拉低 LEDK 形成回路 —— 因此**高电平点亮**，亮度由 PWM 占空比控制。

设备树背光节点：

```dts
backlight: backlight {
    compatible = "pwm-backlight";
    pwms = <&pwm9 0 300000 0>;                 /* 周期 300000ns ≈ 3.33 kHz */
    brightness-levels = <0 ... 255>;
    default-brightness-level = <50>;
};
```

系统侧节点 `/sys/class/backlight/*/max_brightness` = **255**。

---

## 5. 音频

| 项目 | 参数 |
|---|---|
| 声卡 | `rv-acodec`（`simple-audio-card`，I2S0 8ch + 片内 acodec） |
| 功放使能 | `pa-ctl-gpios = <&gpio0 RK_PA2 GPIO_ACTIVE_LOW>` → **GPIO0_A2（gpio 2），低电平使能** |
| 采样率约定 | 16 kHz / 单声道（见 `DeskBot_demo` 的 `system_para.conf`） |

> ⚠️ **极性**：`GPIO_ACTIVE_LOW` 表示**拉低**才打开功放。若极性配反，会出现"声卡枚举正常、播放无报错、但喇叭无声"。

---

## 6. 其他引脚

| 功能 | 引脚 | 全局编号 | 说明 |
|---|---|---|---|
| 蓝牙复位 | GPIO1_A2 | 34 | `BT,reset_gpio`，高有效 |
| 蓝牙唤醒（host → BT） | GPIO1_B0 | 40 | 高有效 |
| 蓝牙唤醒（BT → host 中断） | GPIO1_B1 | 41 | 高有效 |
| 蓝牙 UART RTS | GPIO2_A6 | 70 | 低有效（复用为 GPIO） |

---

## 7. 原理图

- 核心板原理图（PDF）：<https://no-chicken.com/resources/Echo-Mate/Core_Sch_2026-08-15.pdf>
  - p2 = GPIO 分配，p7 = Audio，p10 = LCD & TP

> 本仓库**不包含** PCB 源文件、Gerber、BOM 与 3D 模型。

---

## 8. 常见故障 → 症状对照

**最重要的一条**：必须用 Echo-Mate 自己的板级配置构建固件。若误用 Luckfox Pico Pro Max 的配置，会出现"驱动全部 probe 成功、SPI 通信无报错，但**屏幕纯黑、无声、状态灯不亮**"：

| 功能 | Pro Max 配置（错误） | Echo-Mate 配置（正确） |
|---|---|---|
| 背光 | gpio-72（GPIO2_B0，低有效） | **PWM9 / GPIO1_C5(53)**，高电平点亮 |
| LCD D/C | gpio-73（GPIO2_B1） | **GPIO1_D0(56)** |
| LCD 复位 | gpio-51（GPIO1_C3） | **GPIO1_C4(52)** |
| 功放使能 | gpio-33（GPIO1_A1，高有效） | **GPIO0_A2(2)**，低电平使能 |
| 状态灯 | gpio-118 | **GPIO0_A3(3)** |

（"错误"一列为 `/sys/kernel/debug/gpio` 实测值。）

排障速查：

| 现象 | 可能原因 |
|---|---|
| 屏全黑，`dmesg` 无 st7789v 报错 | 板级配置错了（D/C、复位、背光走错脚） |
| 屏全白 | 背光通了，但 D/C 或 SPI 数据未生效 |
| 触摸无反应，`i2cdetect -y 3` 看不到 `0x38` | 触摸复位 / 中断脚配置错，或排线插反 |
| 播放无报错但无声 | 功放使能脚极性反（应为**低**有效） |
| 状态灯不亮 | LED 脚不是 GPIO0_A3 |

---

## 9. 相关文档

- 固件编译与烧录：[`BUILD.md`](./BUILD.md)
- 软件架构与运行：[`README.md`](./README.md)、[`DeskBot_demo/README.md`](./DeskBot_demo/README.md)
- PC 端安装（无需硬件）：[`INSTALL.md`](./INSTALL.md)
- 变更记录：[`CHANGELOG.md`](./CHANGELOG.md)
