## DeskBot demo

Echo-Mate 桌面 AI 助手主程序（LVGL 界面 + 各子 APP 的融合）。

> 硬件与引脚说明：[`../HARDWARE.md`](../HARDWARE.md)
> 固件编译与烧录：[`../BUILD.md`](../BUILD.md)

### 0. 准备配置文件（**首次运行前必做**）

运行时读取的是 `./bin/system_para.conf`，但 `bin/` 是构建产物目录（已被 `.gitignore` 忽略），**仓库里不含该文件**。请先从模板复制一份再修改：

```sh
cd ./DeskBot_demo
cp utils/system_para.conf.example bin/system_para.conf
```

需要改的几项：

| 键 | 说明 |
|---|---|
| `gaode_api_key` | 高德开放平台 API Key，用于天气等数据获取 |
| `aliyun_api_key` | 阿里云百炼（DashScope）API Key，用于语音对话 |
| `AIChat_server_url` | 服务端所在主机 IP（默认 `172.32.0.100`） |
| `AIChat_server_port` / `AIChat_server_token` | 服务端端口与访问令牌，需与 Server 端启动参数一致 |

### 1. 编译

1. **在电脑上运行 SDL 仿真**

   修改 `conf/dev_conf.h`，将 `LV_USE_SIMULATOR` 置 `1`：

    ```sh
    cd ./DeskBot_demo
    mkdir -p ./build
    cd ./build
    cmake ..
    make
    ```

    然后在 Ubuntu 上运行：

    ```sh
    cd ../bin
    ./main
    ```

2. **编译到开发板上运行**

   修改 `conf/dev_conf.h`，将 `LV_USE_SIMULATOR` 置 `0`，并**先把交叉工具链路径改成自己的**（`toolchain.cmake` 里的 `SDK_PATH` 默认指向作者本机路径）：

    ```sh
    cd ./build
    cmake .. -DTARGET_ARM=ON
    make
    ```

    然后把 `bin/` 整个目录（含可执行文件与 `system_para.conf`、模型、字体等资源）拷到开发板，在开发板上运行：

    ```sh
    cd ../bin
    ./main
    ```

### 2. Server 运行

Python 环境搭建详见 [AI 语言助手 demo（Server 端）](../AIChat_demo/Server/README.md)，然后进入你搭好的虚拟环境运行：

```sh
python ./main.py --access_token="123456"
```

### 3. 注意

1. **使用前务必先改 `./bin/system_para.conf`**（见 §0），里面需要填入你自己的高德 / 阿里云 API Key。
2. 每个 page 可视为一个 APP，想自行添加可参考模板添加。
3. 个人电脑运行服务端 `server` 时，需与开发板 `Client` 端连接到同一网络，AI chat 才能正常访问。也可以使用电脑做网络共享（**默认开发板是 `172.32.0.93`，电脑是 `172.32.0.100`**）。
4. 开发板侧的音频 / 屏幕引脚定义见 [`../HARDWARE.md`](../HARDWARE.md)；固件必须使用 Echo-Mate 的板级配置构建，否则会出现黑屏 / 无声。
