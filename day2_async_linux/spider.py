import aiohttp#导入异步http请求库
import asyncio#python内置异步核心库，用来实现协程、异步任务调度
from bs4 import BeautifulSoup
import random
from logger import logger

# ---------------- 反爬配置 ---------------
# UA池（多个浏览器标识，随机切换）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/118.0.0.0 Safari/537.36",
]

# 定义异步函数：发起网络请求获取网页源码
async def async_fetch(url: str):
    """封装通用异步请求（后续可抽离成独立工具类）"""
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        '''
        async with:异步上下文管理器，自动释放网络连接
        aiohttp.ClientSession 相当于异步版 requests 会话
        所有网络 IO 操作前面必须加 await
        '''
        # 创建一个异步请求会话session
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # 使用session发起GET请求，带上请求头headers
            async with session.get(url, headers=headers) as resp:
                # await 等待网页响应返回，读取网页文本，编码utf-8
                html = await resp.text(encoding="utf-8")
                return html
    except Exception as e:
        logger.error(f"请求异常：{e}")
        return None


# 异步函数：抓取百度热点新闻
async def get_hot_news():
    """异步抓取百度新闻"""
    url = "https://news.baidu.com/"
    logger.info(f"开始请求页面：{url}")
    # 调用上面封装好的异步请求函数，await等待拿到网页源码
    html = await async_fetch(url)
    if not html:
        logger.warning("页面获取失败，返回空列表")
        return []
    # 使用BeautifulSoup加载网页源码，html.parser是python自带解析器
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".hotnews ul li strong a")
    logger.info(f"解析到新闻条目数量：{len(items)}")
    news_list = []
    for item in items:
        # get_text()提取标签内文字，strip=True去除首尾空格换行
        title = item.get_text(strip=True)
        link = item["href"]
        news_list.append({"title": title, "link": link})
        await asyncio.sleep(random.uniform(0.3, 0.8)) # 随机延时防封禁
    return news_list

# 本地测试入口
if __name__ == "__main__":
    logger.info("爬虫程序启动")
    # asyncio.run() 启动异步事件循环，运行异步主函数get_hot_news()
    data = asyncio.run(get_hot_news())
    logger.info(f"抓取完成，新闻结果：{data}")