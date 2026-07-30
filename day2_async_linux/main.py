#FastAPI 接口主程序 → 用户 CRUD 所有接口写这里
from fastapi import FastAPI #FastAPI：：负责搭建网站、接收浏览器 / 前端发来的 http 请求，提供接口
from pydantic import BaseModel #Pydantic:负责数据校验，是FastAPI底层依赖的库。FastAPI本身就是靠Pydantic实现自动参数校验。
from cache import get_cache, set_cache, del_cache
from spider import get_hot_news  #导入爬虫函数

app = FastAPI(title="用户管理接口")

# 模拟数据库
mock_db = {
    1: {"id": 1, "username": "test", "phone": "13800138000"}
}

class UserModel(BaseModel):
    username: str
    phone: str

#新增
@app.post("/users")
def create_user(user: UserModel):
    new_id = max(mock_db.keys()) + 1
    user_data = {"id": new_id, "username": user.username, "phone": user.phone}
    mock_db[new_id] = user_data
    return {"code": 201, "msg": "创建成功", "data": user_data}

#查询
@app.get("/users/{user_id}")
def get_user(user_id: int):
    cache_key = f"user:{user_id}"
    cache_data = get_cache(cache_key)
    if cache_data:
        return {"code": 200, "msg": "读取缓存", "data": cache_data}
    if user_id not in mock_db:
        return {"code": 404, "msg": "用户不存在", "data": None}
    user_info = mock_db[user_id]
    set_cache(cache_key, user_info, 3600)
    return {"code": 200, "msg": "读取数据库", "data": user_info}

#更新
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserModel):
    if user_id not in mock_db:
        return {"code": 404, "msg": "用户不存在", "data": None}
    mock_db[user_id]["username"] = user.username
    mock_db[user_id]["phone"] = user.phone
    del_cache(f"user:{user_id}")
    return {"code": 200, "msg": "更新完成，缓存已清空", "data": mock_db[user_id]}

#删除
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    mock_db.pop(user_id)
    del_cache(f"user:{user_id}")
    return {"code": 200, "msg": "删除完成"}

# ==========爬虫资讯接口（爬虫+Redis联动）==========
@app.get("/news/hot")
async def get_hot_news_api():
    cache_key = "hot_news"
    cache_data = get_cache(cache_key)
    if cache_data:
        return {"code": 200, "msg": "资讯来自缓存", "data": cache_data}
    
    # 调用异步爬虫
    news_data = await get_hot_news()
    set_cache(cache_key, news_data, expire=3600)
    return {"code": 200, "msg": "实时抓取资讯", "data": news_data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

'''
1.新增用户 POST
修改数据库 → 不操作 Redis
等到第一次查询时，才写入缓存
2.查询用户 GET
优先读 Redis;缓存不存在 → 查询数据库 → 回填缓存
3.更新用户 PUT
更新数据库 → 删除Redis旧缓存（不写入新缓存）
4.删除用户 DELETE
删除数据库数据 → 删除Redis缓存
'''