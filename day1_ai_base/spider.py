#资讯爬虫独立文件 → 爬虫逻辑单独拆分，和接口解耦
import requests#用来模拟浏览器发送网络请求，获取网页 HTML 源码,同步
from bs4 import BeautifulSoup#网页解析工具，可以从一大段网页文本里提取标题、链接等内容
import time#提供延时休眠功能
import random

# ---------------- 反爬配置 ---------------
# UA池（多个浏览器标识，随机切换）
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"
]

# 随机获取UA，主动告诉服务器：「我是谁，我是什么设备、什么浏览器、系统版本」
def get_random_ua():
    return random.choice(UA_POOL)

# 代理IP（有可用代理再打开使用）
PROXIES = {
    # "http": "http://127.0.0.1:7890",
    # "https": "http://127.0.0.1:7890"
}


def get_news():
    # Session 自动保持Cookie、会话保持
    #什么是cookie：在你电脑上的小型文本数据，网站用来「认出你」
    session = requests.Session()
    url = "https://news.baidu.com/"
    news_list = []

# 请求头，模拟浏览器访问
    headers = {
        "User-Agent": get_random_ua(),
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    try:
        # PROXIES：代理IP配置；timeout=10 请求10秒没响应就超时断开
        resp = session.get(url, headers=headers, proxies=PROXIES, timeout=10)
        # 指定网页编码为utf-8，防止中文乱码
        resp.encoding = "utf-8"
        # 将网页html文本交给BeautifulSoup，使用html解析器，方便提取内容
        soup = BeautifulSoup(resp.text, "html.parser")
        # CSS选择器：筛选热点新闻对应的a标签
        items = soup.select(".hotnews ul li strong a")

        for item in items:
            title = item.get_text(strip=True)
            link = item["href"]
            news_list.append({"title": title, "link": link})
            # 随机延时 0.1~0.4s，代替固定0.2
            time.sleep(random.uniform(0.1, 0.4))

    except Exception as e:
        print("爬虫抓取异常：", e)
    return news_list


if __name__ == "__main__":
    data = get_news()
    print("抓取资讯：", data)