# 更新日志

## 2026-10-10 — 修复屏幕黑屏（板级配置修正）

### 问题
整机外设（屏幕 / 背光 / 功放 / 状态灯）全部不工作，屏幕全程纯黑，
但内核 fb_st7789v 驱动 probe 正常、SPI 通信 20MHz 无报错。

### 根因
构建固件时 lunch 选错板级配置 —— 误用 RV1106_Luckfox_Pico_Pro_Max
（Luckfox Pico Pro Max 的配方），而非 Echo-Mate 自身的板级配置：
- LCD 的 D/C、Reset 落在未被 pinmux 接管的引脚上；
- 背光挂在板上一颗未走线的 GPIO 上，永远得不到电；
- 功放使能 pa-ctl 与状态 LED 同样引脚/极性不符。

### 修复
lunch 改选 RV1106_Echo_Mate-DeskMate（SPI_NAND + Buildroot），
对应 BoardConfig-SPI_NAND-Buildroot-RV1106_Echo_Mate-DeskMate.mk
（DTS = rv1106g-echo-mate.dts），重新编译烧录后屏幕正常出图。

### 引脚修正对照
| 功能 | 修正前（Pro Max） | 修正后（Echo-Mate） |
|---|---|---|
| 背光 | gpio-72（GPIO2_B0，低有效） | pwm9 / GPIO1_C5(53)，高有效 |
| LCD D/C | gpio-73（GPIO2_B1） | GPIO1_D0(56) |
| LCD Reset | gpio-51（GPIO1_C3） | GPIO1_C4(52) |
| 功放使能 pa-ctl | gpio-33（GPIO1_A1，高有效） | GPIO0_A2(2)，低有效 |
| 状态 LED | gpio-118 | GPIO0_A3(3) |

### 备注
- 本次修复不涉及源码改动，仅修正构建配置。
- 验收：cat /proc/device-tree/model → Echo Mate；背光 max_brightness = 255（PWM）。
