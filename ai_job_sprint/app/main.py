import logging
from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.core.config import ARK_MODEL
from app.tools.database import init_database
from app.api.agent import router as agent_router
from app.api.graph_agent import (
    router as graph_agent_router,
)
from app.api.rag import (
    router as rag_router,
)
from app.api.rag_optimized import (
    router as rag_optimized_router,
)
from app.api.ingest import (
    router as ingest_router,
)

logging.basicConfig(
    level=logging.INFO,
    format=("%(asctime)s | " "%(levelname)s | " "%(name)s | " "%(message)s"),
)

init_database()

app = FastAPI(
    title="AI Job Sprint API",
    version="0.1.0",
)


app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(graph_agent_router)
app.include_router(rag_router)
app.include_router(rag_optimized_router)
app.include_router(ingest_router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "model": ARK_MODEL}


"""
| 需求     | 装饰器             | 常见用途         |
| ------ | --------------- | ------------ |
| 获取数据   | `@app.get()`    | 查询用户、获取聊天记录  |
| 新增数据   | `@app.post()`   | 注册、登录、发送聊天内容 |
| 修改全部数据 | `@app.put()`    | 更新完整的用户信息    |
| 修改部分数据 | `@app.patch()`  | 只修改昵称等部分字段   |
| 删除数据   | `@app.delete()` | 删除用户或聊天记录    |

"""
