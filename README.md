# Dive into Deep Learning Notes

《动手学深度学习》学习笔记，基于 PyTorch 实现。

## 目录结构

| 目录 | 内容 |
|------|------|
| `fundamentals/` | 深度学习基础：参数管理、层与块、文件读写与 GPU |
| `mlp/` | 多层感知机：MLP 实现、过拟合/欠拟合、Dropout、权重衰减 |
| `cnn/` | 卷积神经网络：CNN 基础、AlexNet、BatchNorm、ResNet、DenseNet |
| `computer-vision/` | 计算机视觉：FCN、图像增广、目标检测、锚框、风格迁移、图像分类 |
| `rnn/` | 循环神经网络：RNN 基础、现代 RNN |
| `nlp/` | 自然语言处理：注意力机制、词嵌入、情感分析 |
| `optimization/` | 优化算法：梯度下降、凸优化、优化器、学习率调度器 |
| `projects/` | 实战项目：Kaggle 房价预测、狗种类识别、平衡车算法 |

## 环境要求

- Python >= 3.8
- PyTorch
- d2l

## 安装依赖

```bash
pip install -r requirements.txt
```

## 重构版本

`notebooks/` 目录下是重构后的版本：
- 移除 d2l 依赖，使用标准 PyTorch + d2l_compat 工具模块
- CV 部分使用 torchvision
- NLP 部分新增 HuggingFace Transformers 示例
- 详见 `notebooks/README.md`

## 参考

- [《动手学深度学习》官方教材](https://zh.d2l.ai/)
- [d2l 官方 GitHub](https://github.com/d2l-ai/d2l-zh)
