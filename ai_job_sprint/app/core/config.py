import os
from dotenv import load_dotenv


# 1. 读取 .env 文件
load_dotenv(override=True)


# 2. 从环境变量中读取火山方舟 API Key
ARK_API_KEY = os.getenv("ARK_API_KEY").strip()


# 3. 读取模型名称
ARK_MODEL = os.getenv(
    "ARK_MODEL",
    "doubao-seed-2-1-pro-260628"
).strip()

ARK_FALLBACK_MODEL = os.getenv(
    "ARK_FALLBACK_MODEL",
    "doubao-seed-2-1-turbo-260628"
).strip()


LLM_TIMEOUT = float(
    os.getenv("LLM_TIMEOUT", "60")
)


LLM_MAX_RETRIES = int(
    os.getenv("LLM_MAX_RETRIES", "3")
)

# 4. 临时检查是否读取成功
print("ARK_API_KEY 是否读取成功：", bool(ARK_API_KEY))
print("ARK_MODEL：", ARK_MODEL)