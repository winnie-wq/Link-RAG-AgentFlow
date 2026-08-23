import re
import os

'''
re 是 Python 正则表达式模块

re.sub(pattern, repl, string)
pattern:正则匹配规则
repl:替换成什么（空字符串'' = 删除匹配内容）
string:待处理的原始文本
'''
def clean_single_text(raw_text: str) -> str:
    """清洗单条文本"""
    # 1. 去除HTML标签
    raw_text = re.sub(r'<.*?>', '', raw_text)
    # 2. 去除换行、制表符
    raw_text = re.sub(r'[\n\t\r]', ' ', raw_text)
    # 3. 去除多余连续空格
    raw_text = re.sub(r'\s+', ' ', raw_text)
    # 4. 去除特殊无用符号，可以按需增删
    raw_text = re.sub(r'[#@$^&*{}|~]', '', raw_text)
    # 首尾空格去除
    return raw_text.strip()

def filter_short_text(text: str, min_length=10) -> str | None:
    """过滤过短无效文本，太短内容没有价值"""
    if len(text) >= min_length:
        return text
    return None


'''
os 是 Python操作系统内置模块，用来和电脑文件系统、操作系统交互。

可以实现：遍历文件夹、拼接文件路径、创建文件夹、判断文件是否存在等文件操作。

os.listdir()：列出文件夹里面所有文件 / 子文件夹名称
os.path.join()：安全拼接路径

with open(...) as f:安全打开文件写法，读取结束后自动关闭文件，不用手动写 f.close()
'''

def batch_load_txt_files(folder_path: str):
    """批量读取文件夹内所有txt文件,返回清洗后的文本列表"""
    clean_result = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_full_path = os.path.join(folder_path, filename)
            with open(file_full_path, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = clean_single_text(content)
            valid_text = filter_short_text(cleaned)
            if valid_text:
                clean_result.append(valid_text)
    return clean_result

# 本地测试入口
if __name__ == "__main__":
    test_str = """
    <html>
    你好！！！   这是   待清洗   的文本
    
    #无用符号@
    """
    res = clean_single_text(test_str)
    print("清洗结果：", res)

    # 批量读取测试（你创建一个test文件夹放txt即可使用）
    # data = batch_load_txt_files("./txt_data")
    # print(data)