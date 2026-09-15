from volcenginesdkarkruntime import Ark

from app.core.config import ARK_API_KEY, ARK_MODEL

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ARK_API_KEY,
)


response = client.responses.create(
    model=ARK_MODEL,
    input="请只回答：你好",
)

for item in response.output:

    if item.type != "message":
        continue

    for content in item.content:

        if content.type == "output_text":
            print(content.text)
