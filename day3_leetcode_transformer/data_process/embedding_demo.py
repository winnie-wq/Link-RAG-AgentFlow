from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
model = AutoModel.from_pretrained("bert-base-chinese")

def get_embedding(text:str):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs)
    # 取句子向量
    vec = output.last_hidden_state.mean(dim=1)
    return vec

if __name__ == "__main__":
    vec1 = get_embedding("人工智能")
    vec2 = get_embedding("机器学习")
    vec3 = get_embedding("篮球运动")
    print("向量形状",vec1.shape)
    # 向量越接近，语义越相似