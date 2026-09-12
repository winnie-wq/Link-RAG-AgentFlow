MOCK_WEATHER = {
    "广州": {
        "temperature": 30,
        "weather": "多云",
        "humidity": 75,
    },
    "北京": {
        "temperature": 24,
        "weather": "晴",
        "humidity": 40,
    },
    "上海": {
        "temperature": 28,
        "weather": "小雨",
        "humidity": 80,
    },
}


def weather(city: str):

    city = city.strip()

    if not city:
        raise ValueError("city 不能为空")

    data = MOCK_WEATHER.get(city)

    if data is None:

        return {
            "city": city,
            "found": False,
            "message": "暂无该城市的模拟天气数据",
        }

    return {
        "city": city,
        "found": True,
        **data,
    }