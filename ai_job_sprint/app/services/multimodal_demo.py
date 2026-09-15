import base64

from volcenginesdkarkruntime import Ark

from app.core.config import (
    ARK_API_KEY,
    ARK_MODEL,
)

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ARK_API_KEY,
)


def image_to_data_url(file_path: str) -> str:

    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:image/jpeg;base64,{image_data}"


def main():

    image_url = image_to_data_url("test.jpg")

    response = client.responses.create(
        model=ARK_MODEL,
        input=[
            {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "请描述这张图片中的主要内容。",
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url,
                    },
                ],
            }
        ],
    )

    for item in response.output:

        if item.type != "message":
            continue

        for content in item.content:

            if content.type == "output_text":
                print(content.text)


if __name__ == "__main__":
    main()
