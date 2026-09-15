import base64
import time

from app.services.llm_client import LLMClient


class MultimodalService:

    def __init__(self):

        self.llm = LLMClient()

    # =====================================================
    # 图片 → Base64 Data URL
    # =====================================================

    def _image_to_data_url(
        self,
        image_bytes: bytes,
        content_type: str,
    ) -> str:

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        return f"data:{content_type};base64," f"{image_base64}"

    # =====================================================
    # 图片分析
    # =====================================================

    async def analyze(
        self,
        *,
        text: str,
        image_bytes: bytes | None = None,
        content_type: str | None = None,
    ):

        start = time.perf_counter()

        try:

            # 有图片
            if image_bytes:

                image_url = self._image_to_data_url(
                    image_bytes,
                    content_type or "image/jpeg",
                )

                response = await self.llm.multimodal_chat(
                    text=text,
                    image_url=image_url,
                )

            # 没有图片
            else:

                response = await self.llm.chat(text)

            latency = time.perf_counter() - start

            return {
                "status": "success",
                "answer": response,
                "latency": round(latency, 3),
            }

        except Exception as exc:

            latency = time.perf_counter() - start

            return {
                "status": "error",
                "answer": "",
                "error": str(exc),
                "latency": round(latency, 3),
            }
