"""创建 transformers 版本的 sentiment analysis notebook"""
import json

nb = {
    'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}},
    'nbformat': 4,
    'nbformat_minor': 4,
    'cells': []
}

cells = []

def add_md(text):
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': [text + '\n']})

def add_code(lines):
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': [l + '\n' for l in lines[:-1]] + ([lines[-1]] if lines[-1] else [])})

add_md('# 使用 Transformers 进行文本分类\n\n本 Notebook 使用 HuggingFace transformers 库实现文本分类任务（以 SNLI 自然语言推断为例）。')

add_code([
    'import torch',
    'from torch import nn',
    'from torch.utils.data import DataLoader',
    'from transformers import BertTokenizer, BertForSequenceClassification, AdamW',
    'from datasets import load_dataset',
    'import numpy as np',
    'from tqdm import tqdm'
])

add_md('## 1. 加载 SNLI 数据集\n\n使用 `datasets` 库直接加载 SNLI 数据集，无需手动下载和预处理。')

add_code([
    '# 加载 SNLI 数据集',
    'dataset = load_dataset("snli")',
    '',
    '# 查看数据集结构',
    'print(dataset)',
    'print("训练集样本数:", len(dataset["train"]))',
    'print("验证集样本数:", len(dataset["validation"]))',
    'print("测试集样本数:", len(dataset["test"]))'
])

add_md('## 2. 使用 BERT Tokenizer\n\nTransformers 提供了预训练的 BERT Tokenizer，可以直接对文本进行编码。')

add_code([
    '# 加载预训练的 BERT tokenizer',
    'tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")',
    '',
    '# 测试编码',
    'premise = "Two women are embracing while holding to go packages."',
    'hypothesis = "The sisters are hugging goodbye while holding to go packages after just eating lunch."',
    'encoded = tokenizer(premise, hypothesis, padding="max_length", truncation=True, max_length=128, return_tensors="pt")',
    'print("Input IDs shape:", encoded["input_ids"].shape)',
    'print("Attention mask shape:", encoded["attention_mask"].shape)',
    'print("Token type IDs shape:", encoded["token_type_ids"].shape)'
])

add_md('## 3. 数据预处理\n\n将数据集编码为模型可接受的格式。')

add_code([
    'def preprocess_function(examples):',
    '    """对批量样本进行编码"""',
    '    return tokenizer(',
    '        examples["premise"],',
    '        examples["hypothesis"],',
    '        padding="max_length",',
    '        truncation=True,',
    '        max_length=128',
    '    )',
    '',
    '# 过滤掉标签为 -1 的无效样本',
    'dataset = dataset.filter(lambda x: x["label"] != -1)',
    '',
    '# 对数据集进行编码',
    'encoded_dataset = dataset.map(preprocess_function, batched=True)',
    '',
    '# 设置格式为 PyTorch tensors',
    'encoded_dataset = encoded_dataset.remove_columns(["premise", "hypothesis"])',
    'encoded_dataset = encoded_dataset.rename_column("label", "labels")',
    'encoded_dataset.set_format("torch")',
    '',
    '# 创建 DataLoader',
    'train_dataloader = DataLoader(encoded_dataset["train"].shuffle(seed=42).select(range(10000)), batch_size=32)',
    'val_dataloader = DataLoader(encoded_dataset["validation"].select(range(2000)), batch_size=32)',
    '',
    'print("数据加载完成!")'
])

add_md('## 4. 加载预训练 BERT 模型\n\n使用 `BertForSequenceClassification` 进行三分类（蕴含/矛盾/中立）。')

add_code([
    '# 加载预训练的 BERT 分类模型',
    'device = torch.device("cuda" if torch.cuda.is_available() else "cpu")',
    'model = BertForSequenceClassification.from_pretrained(',
    '    "bert-base-uncased",',
    '    num_labels=3',
    ').to(device)',
    '',
    'print(f"模型已加载到 {device}")',
    'print(f"可训练参数数量: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")'
])

add_md('## 5. 微调模型\n\n使用 AdamW 优化器进行微调。')

add_code([
    'optimizer = AdamW(model.parameters(), lr=5e-5)',
    'num_epochs = 3',
    '',
    'for epoch in range(num_epochs):',
    '    # 训练',
    '    model.train()',
    '    total_loss = 0',
    '    for batch in tqdm(train_dataloader, desc=f"Epoch {epoch+1}/{num_epochs}"):',
    '        batch = {k: v.to(device) for k, v in batch.items()}',
    '        outputs = model(**batch)',
    '        loss = outputs.loss',
    '        loss.backward()',
    '        optimizer.step()',
    '        optimizer.zero_grad()',
    '        total_loss += loss.item()',
    '    ',
    '    avg_loss = total_loss / len(train_dataloader)',
    '    print(f"Epoch {epoch+1}, Average Loss: {avg_loss:.4f}")',
    '    ',
    '    # 验证',
    '    model.eval()',
    '    correct = 0',
    '    total = 0',
    '    with torch.no_grad():',
    '        for batch in val_dataloader:',
    '            batch = {k: v.to(device) for k, v in batch.items()}',
    '            outputs = model(**batch)',
    '            predictions = torch.argmax(outputs.logits, dim=-1)',
    '            correct += (predictions == batch["labels"]).sum().item()',
    '            total += batch["labels"].size(0)',
    '    acc = correct / total',
    '    print(f"Validation Accuracy: {acc:.4f}")'
])

add_md('## 6. 预测\n\n使用微调后的模型进行推理。')

add_code([
    'def predict_nli(premise, hypothesis):',
    '    """预测前提和假设之间的逻辑关系"""',
    '    model.eval()',
    '    encoded = tokenizer(premise, hypothesis, return_tensors="pt", padding=True, truncation=True, max_length=128)',
    '    encoded = {k: v.to(device) for k, v in encoded.items()}',
    '    with torch.no_grad():',
    '        outputs = model(**encoded)',
    '    logits = outputs.logits',
    '    prediction = torch.argmax(logits, dim=-1).item()',
    '    labels = ["entailment", "neutral", "contradiction"]',
    '    return labels[prediction]',
    '',
    '# 测试',
    'print(predict_nli("A man is walking a dog.", "A person is outdoors with an animal."))',
    'print(predict_nli("A man is walking a dog.", "A cat is sleeping."))',
    'print(predict_nli("A man is walking a dog.", "No person is present."))'
])

nb['cells'] = cells

with open('notebooks/nlp/sentiment-analysis-transformers.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print('Created sentiment-analysis-transformers.ipynb')
