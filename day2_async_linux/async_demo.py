import asyncio

'''
async def:定义协程函数，调用不会执行，只是生成协程对象
await:只能写在 async def 内部；等待 IO 任务(网络、sleep)，等待期间可以切换执行其他任务
asyncio.run()：事件入口，启动异步循环
'''
async def task(name, delay):
    print(f"任务{name}开始")
    await asyncio.sleep(delay) # 非阻塞等待（不会卡住整个程序）
    print(f"任务{name}结束")

async def main():
    # 创建并发任务
    t1 = asyncio.create_task(task("新闻1", 3))
    t2 = asyncio.create_task(task("新闻2", 2))
    t3 = asyncio.create_task(task("新闻3", 7))
    await t1
    await t2
    await t3

if __name__ == "__main__":
    asyncio.run(main())