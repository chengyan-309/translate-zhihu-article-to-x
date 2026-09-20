# Translate Zhihu Article to X

A Codex skill that reads a specified Zhihu article or answer and rewrites it as a concise English post for an international AI and technology audience.

## What It Does

- Reads only the requested article's title, author name, and body.
- Preserves the author's core argument while removing repetition and low-value detail.
- Leads with the strongest conclusion in the first screen.
- Keeps the main post concise and easy to scan on X.
- Uses the original Zhihu contributor name without translation.
- Produces a separate comment containing source and reference links.
- Avoids emojis, hashtags, Markdown tables, URLs in the main post, and em dashes.

## Output

The skill returns two copy-ready Markdown blocks:

1. `Post`, containing the English title and main text.
2. `Comment`, containing the original article link and any essential reference links.

## Install

Clone the repository into your Codex skills directory:

```bash
git clone https://github.com/chengyan-309/translate-zhihu-article-to-x.git ~/.codex/skills/translate-x-platform-article
```

Then invoke it with a Zhihu URL:

```text
Use $translate-x-platform-article to translate this Zhihu article for X:
https://www.zhihu.com/...
```
