import time

import requests
from bs4 import BeautifulSoup

# =====================================================
# API 获取
#
# 支持：
# pagination
# timeout
# retry
# =====================================================


def fetch_api_posts(
    *,
    base_url: str,
    pages: int = 2,
    page_size: int = 10,
    max_retries: int = 3,
):

    results = []

    for page in range(
        1,
        pages + 1,
    ):

        # 构造请求参数字典，传给API
        params = {
            "_page": page,
            "_limit": page_size,
        }

        for attempt in range(max_retries):

            try:

                response = requests.get(
                    base_url,
                    params=params,
                    timeout=10,
                )

                response.raise_for_status()

                data = response.json()

                """
                区别 append：extend 是把列表里面元素一个个加进去；
                append 是直接把整个列表当成一个元素塞进去"""

                results.extend(data)

                break

            except requests.RequestException:

                if attempt == max_retries - 1:
                    raise

                time.sleep(2**attempt)

        # 简单限速
        time.sleep(0.5)

    return results


# =====================================================
# HTML Demo
# =====================================================


def fetch_page_title(
    url: str,
):

    response = requests.get(
        url,
        timeout=10,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    if soup.title:
        return soup.title.text.strip()

    return ""
