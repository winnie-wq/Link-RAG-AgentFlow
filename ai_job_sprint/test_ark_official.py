import os
from volcenginesdkarkruntime import Ark


api_key = os.getenv("ARK_API_KEY", "").strip()

print("是否读取到 API Key：", bool(api_key))
print("API Key 长度：", len(api_key))


client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3", # 去掉多余k volces
    api_key=api_key,
)



response = client.responses.create(
    model="doubao-seed-2-1-pro-260628",
    input="hello",
)


for item in response.output:

    if item.type == "reasoning":

        for summary in item.summary:

            if summary.type == "summary_text":
                print(f"思考：{summary.text}")

    elif item.type == "message":

        for content in item.content:

            if content.type == "output_text":
                print(f"回答：{content.text}")