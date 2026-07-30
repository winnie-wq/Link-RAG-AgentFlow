'''
cache.py不用改动,依然可以正常调用（同步缓存函数在异步接口可以使用，生产建议后续封装异步 redis）
'''

#Redis 缓存工具封装 → 专门放Redis连接、读写删除缓存函数
import redis
import json
from typing import Optional, Any#typing 是 Python 官方内置模块，专门用来做类型注解

# 初始化Redis客户端
try:
    redis_client = redis.Redis(
        #redis.Redis(...) 只是创建对象，不会立刻连接 Redis！仅仅是在内存生成一个客户端，不会检测 Redis 是否存活。
        host="127.0.0.1",
        port=6379,
        db=0,
        decode_responses=True,  # 自动转为字符串
        socket_timeout=3
    )
    redis_client.ping()#只有调用 .ping()，才会真正和 Redis 服务器通信测试连通
except Exception as e:
    print("⚠ Redis连接失败，缓存功能失效:", e)
    redis_client = None


#get_cache：loads 字符串 → Python 数据（读取出来）
def get_cache(key: str) -> Optional[Any]:
    """读取缓存,自动反序列化,Redis异常返回None"""
    if not redis_client:
        return None
    try:
        data_str = redis_client.get(key)
        if not data_str:
            return None
        return json.loads(data_str)
    except Exception as e:
        #f = f-string（格式化字符串），作用：直接在字符串里面嵌入变量
        print(f"读取缓存异常 key={key}: {e}")
        return None


#set_cache：dumps Python 数据 → 字符串（存入 Redis）
def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    写入缓存
    :param key: 缓存键
    :param value: 需要缓存的数据（字典/列表）
    :param ttl: 过期秒数,默认3600
    :return: 是否成功
    """
    if not redis_client:
        return False
    try:
        # ensure_ascii=False 允许保存中文
        #dumps = dump string，作用：序列化；Redis 不能直接存字典，只能存字符串、数字，所以必须先转字符串！
        json_str = json.dumps(value, ensure_ascii=False)
        #setex(key,ttl,data) Redis 原生指令，专门用来带过期时间存储
        redis_client.setex(key, ttl, json_str)
        return True
    except Exception as e:
        print(f"写入缓存异常 key={key}: {e}")
        return False


def del_cache(key: str) -> bool:
    """删除缓存"""
    if not redis_client:
        return False
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"删除缓存异常 key={key}: {e}")
        return False