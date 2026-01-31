# KContext Markdown

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

**KContext Markdown** is a lightweight and efficient Python utility designed to manage and optimize context for Large Language Models (LLMs) using Markdown structures. It ensures your prompts stay within context windows while preserving the semantic structure of your documents.

## 🚀 Features

- **Markdown-Aware**: Native support for headers, lists, and code blocks.
- **Context Optimization**: Smart truncation algorithms that respect document structure.
- **Token Estimation**: Efficient heuristic for token counting.
- **Zero Dependencies**: Pure Python implementation for easy integration.

## 📦 Installation

```bash
pip install git+https://github.com/Tatine13/kcontext-markdown.git
```

## 💻 Usage

```python
from kcontext import KContext

# Initialize with a markdown file
ctx = KContext("docs/technical_manual.md")

# Get optimized content fitting 2000 tokens
optimized_text = ctx.get_optimized_content(max_tokens=2000)

print(optimized_text)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
