import os
from dotenv import load_dotenv

load_dotenv()

ARK_API_KEY = os.getenv("ARK_API_KEY")
ARK_MODEL = os.getenv("ARK_MODEL")

LLM_TIMEOUT = 60
LLM_MAX_RETRIES = 3
