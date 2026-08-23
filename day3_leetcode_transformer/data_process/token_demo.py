from transformers import AutoTokenizer

# 使用开源中文分词器
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

if __name__ == "__main__":
    sentence = "我正在学习Transformer和大模型,准备搭建RAG系统"
    tokens = tokenizer.tokenize(sentence)
    token_ids = tokenizer.encode(sentence)
    print("分词tokens:", tokens)
    print("token数字id:", token_ids)
    print("token数量:", len(tokens))
    # 上下文窗口：如果句子token数量超过模型上限，就会截断！
    