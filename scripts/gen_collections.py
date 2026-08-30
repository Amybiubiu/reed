#!/usr/bin/env python3
"""根据 collections/*.md 的 frontmatter 生成 readme.md 中的「文章合集」表格。

用法: python3 scripts/gen_collections.py

每个 collection 文件需要在头部声明 frontmatter:

    ---
    title: 文章标题
    description: 一句话简介(可选)
    tags: [标签1, 标签2](可选)
    date: 2026-08-28
    ---

脚本以表格自身的表头行与分隔行定位「文章合集」表格,只替换表格内容,
其余部分不动。这样 readme.md 中不需要残留任何注释标记。
新增文章后运行一次即可。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLLECTIONS_DIR = ROOT / "collections"
README = ROOT / "README.md"

TABLE_HEADER = "| 文章 | 一句话简介 | 发布时间 |"
TABLE_SEPARATOR = "|------|-----------|---------|"


def parse_frontmatter(text):
    """解析文件头部的 YAML frontmatter,返回 (meta, body)。仅支持 key: value 形式。"""
    if not text.startswith("---"):
        return {}, text
    _, fm, body = text.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value or value.startswith("#"):
            continue
        if value.startswith("[") and value.endswith("]"):
            meta[key] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[key] = value.strip("\"'")
    return meta, body


def escape_cell(text):
    """转义 markdown 表格单元格中的竖线,避免破坏表格。"""
    return str(text).replace("|", "\\|")


def collect_articles():
    articles = []
    for path in sorted(COLLECTIONS_DIR.glob("*.md")):
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        title = meta.get("title")
        if not title:
            print(f"[跳过] {path.name}: 缺少 frontmatter title", file=sys.stderr)
            continue
        articles.append(
            {
                "name": path.name,
                "title": title,
                "description": meta.get("description", ""),
                "date": meta.get("date", ""),
            }
        )
    # 按 date 倒序,无日期的排在最后
    articles.sort(key=lambda a: a["date"] or "0000-00-00", reverse=True)
    return articles


def render_table(articles):
    lines = [TABLE_HEADER, TABLE_SEPARATOR]
    for a in articles:
        link = f"[{escape_cell(a['title'])}](collections/{a['name']})"
        desc = escape_cell(a["description"]) or "—"
        date = escape_cell(a["date"]) or "—"
        lines.append(f"| {link} | {desc} | {date} |")
    return "\n".join(lines)


# 匹配整张表格:表头行 + 分隔行 + 若干以 | 开头的行
TABLE_PATTERN = re.compile(
    re.escape(TABLE_HEADER) + r"\n" + re.escape(TABLE_SEPARATOR) + r"(?:\n\|[^\n]*)*"
)

# 找不到表格时,插入到这段引言之后
ANCHOR = "*以下为芦苇团队整理发布的精选文章。*"


def main():
    articles = collect_articles()
    block = render_table(articles)

    text = README.read_text(encoding="utf-8")
    if TABLE_PATTERN.search(text):
        README.write_text(TABLE_PATTERN.sub(block, text), encoding="utf-8")
        print(f"已更新 {README.name}:{len(articles)} 篇文章")
        return

    if ANCHOR in text:
        README.write_text(text.replace(ANCHOR, f"{ANCHOR}\n\n{block}", 1), encoding="utf-8")
        print(f"已插入 {README.name}:{len(articles)} 篇文章")
        return

    print(
        f"{README.name}: 未找到文章合集表格,请检查 readme.md 是否包含 {ANCHOR}",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
