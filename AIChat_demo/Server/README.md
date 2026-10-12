## AI语言助手demo(Server端)

### 环境搭建

这里默认大家都是用的自己的电脑搭建服务，默认同学们都没有GPU（有就更好）

首先创建虚拟环境, 不然容易污染你的系统环境, 作者使用的python3.10。环境名字就起名`AIChatServerEnv`好了，环境名可自定义。

``` sh
cd ./your-path
conda create --prefix ./AIChatServerEnv python=3.10
```

然后启动虚拟环境，并安装所需要的包，如果下载不了需要科学上网

``` sh
conda activate ./AIChatServerEnv
pip install -r ./requirements.txt
```

### 启动

搭建完毕，直接运行即可：

``` sh
python ./main.py
```

**注意：服务端不解析任何命令行参数。** 下面两项都不通过命令行传入：

| 配置 | 实际位置 | 默认值 |
|---|---|---|
| 访问令牌 `access_token` | `main.py` 中硬编码（第 24 行） | `123456` |
| 阿里云 API Key | `config/local_secrets.py` 的 `DASHSCOPE_API_KEY` | 无，**必填** |

因此 `python ./main.py --access_token="..." --aliyun_api_key="..."` 这种写法**是无效的** ——
Python 会静默忽略这两个参数，鉴权仍按 `123456` 通过，直到真正发起对话才报 `apikey is required`。
密钥配置步骤见仓库根目录 [`../../INSTALL.md`](../../INSTALL.md) 第八章。

### 文件目录介绍

```sh
Server/
├── config/                # 全局设置
├── handle/                # ws接收内容的处理
|   ├── audio_handle.py    # 音频数据处理
|   ├── auth_handle.py     # 鉴权
│   └── text_handle.py     # 文本数据处理
├── models/                # 
├── services/              # 
├── test/                  # 单功能测试
├── threads/               # 多线程相关
├── tools/                 # 工具
|   ├── audio_processor.py # 音频处理
|   ├── logger.py          # log
│   └── registry.py        # 意图注册
├── ws_server.py           # websocket server 业务
├── service_manager.py     # services 全局管理
└── main.py
```

### WebSockets协议说明

以下是Server端会向Client端发送的信息:

1. 鉴权信息：

   ```json
   {
      "type": "auth",
      "message": "Authentication failed" 
   }
   ```
   "message"还包括: "Client authenticated"

2. VAD检测到说话的活跃状态

   ```json
   {
      "type": "vad",
      "state": "no_speech" 
   }
   ```
   "state"还包括: "end", "too_long"

3. ASR识别到说话的文字

   ```json
   {
       "type": "asr",
       "text": "speech的内容"
   }
   ```

4. tts生成语音完毕

   ```json
   {
      "type": "tts",
      "state": "end"
   }
   ```
   "state"还包括: "continue"

5. 对话结束

   ```json
   {
      "type": "chat",
      "dialogue": "end"
   }
   ```
   "state"还包括: "continue"


6. 打包发送的音频数据

   ```python
    version: 协议版本 (2 字节)
    type: 消息类型 (2 字节)
    payload: opus格式消息负载 (字节)
   ```