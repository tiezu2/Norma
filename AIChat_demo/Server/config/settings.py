import dashscope

try:
    from config.local_secrets import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, DASHSCOPE_WORKSPACE
except ImportError:
    DASHSCOPE_API_KEY = "your-dashscope-api-key"
    DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    DASHSCOPE_WORKSPACE = ""

class Settings:
    protocol_version = 2

    # LLM API 密钥
    dashscope.api_key = DASHSCOPE_API_KEY
    dashscope.base_http_api_url = DASHSCOPE_BASE_URL

    # 模型选择
    INTENT_MODEL = "qwen-turbo"       # 专门用于意图识别
    CHAT_MODEL = "qwen-turbo"         # 用于常规对话

    # device
    ASR_DEVICE = "cpu"                # ASR 模型使用的设备
    # ASR_DEVICE = "cuda"             # ASR 模型使用的设备
    VAD_DEVICE = "cpu"                # VAD 模型使用的设备

    # 超时设置
    API_TIMEOUT = 10  # 秒

    def Set_API_Key(self, aliyun_api_key):
        dashscope.api_key = aliyun_api_key


global_settings = Settings()
