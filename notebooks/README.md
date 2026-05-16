# PyTorch + Transformers 重构笔记

本项目是《动手学深度学习》学习笔记的 PyTorch + Transformers 重构版本。
原 d2l 库依赖已替换为标准 PyTorch 实现，NLP 部分新增了 HuggingFace Transformers 示例。

## 目录结构

| 目录 | 内容 |
|------|------|
| `fundamentals/` | 深度学习基础 |
| `mlp/` | 多层感知机 |
| `cnn/` | 卷积神经网络 |
| `computer-vision/` | 计算机视觉（使用 torchvision） |
| `rnn/` | 循环神经网络 |
| `nlp/` | 自然语言处理（新增 transformers 版本） |
| `optimization/` | 优化算法 |
| `projects/` | 实战项目 |

## 核心变化

- **移除 d2l 依赖**：所有 `from d2l import torch as d2l` 替换为 `from d2l_compat import *`
- **d2l_compat.py**：公共工具模块，包含训练循环、数据加载、可视化等辅助函数
- **torchvision**：CV 部分的 ResNet 等模型使用 `torchvision.models`
- **transformers**：NLP 部分新增 `sentiment-analysis-transformers.ipynb`，演示 HuggingFace transformers 用法

## 安装依赖

```bash
pip install -r requirements.txt
```

## 说明

- 每个 Notebook 开头已自动添加 `sys.path.insert(0, '..')` 以导入 `d2l_compat.py`
- 核心教学实现（从零实现注意力、RNN、CNN 等）予以保留
- 运行 Notebook 时请确保在项目根目录启动 Jupyter
