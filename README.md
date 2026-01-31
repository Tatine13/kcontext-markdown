# KContext Markdown

A lightweight and efficient utility designed to manage and optimize context for Large Language Models (LLMs) using Markdown structures.

## Overview

KContext Markdown helps in organizing, truncating, and formatting text data to ensure it fits within LLM context windows while maintaining semantic relevance.

## Features

- **Markdown-based**: Native support for markdown headers and structures.
- **Context Optimization**: Smart truncation and summarization capabilities.
- **Lightweight**: Minimal dependencies, pure Python implementation.

## Usage

```python
from kcontext import KContext

ctx = KContext("path/to/markdown/file.md")
print(ctx.get_optimized_content())
```

## License

MIT
