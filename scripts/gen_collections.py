#!/usr/bin/env python3
"""根据 _posts/*.md 的 frontmatter 生成 readme.md 与 index.md 中的「文章合集」表格。

用法: python3 scripts/gen_collections.py

每篇文章文件需放在 _posts/ 下,按 Jekyll 命名规范:
YYYY-MM-DD-slug.md(slug 用 ASCII,生成站点链接),并在头部声明 frontmatter:

    ---
    title: 文章标题
    description: 一句话简介(可选)
    tags: [标签1, 标签2](可选)
    date: 2026-08-28
    ---

index.md(站点首页)与 README.md(GitHub 展示)内容保持一致,
脚本同时更新两处表格,只替换表格内容,其余部分不动。
新增文章后运行一次即可。

注意:文章正文会被 Jekyll 按 Liquid 解析,如含 {{ 或 {% 需用 {% raw %} 包裹。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
README = ROOT / "README.md"
INDEX = ROOT / "index.md"
SITE_URL = "https://guide.reeddaily.com"

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
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        title = meta.get("title")
        if not title:
            print(f"[跳过] {path.name}: 缺少 frontmatter title", file=sys.stderr)
            continue
        # slug 取自文件名 YYYY-MM-DD-slug.md,与站点 permalink /posts/:slug/ 一致
        m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", path.name)
        slug = m.group(1) if m else path.stem
        articles.append(
            {
                "slug": slug,
                "title": title,
                "description": meta.get("description", ""),
                # 优先 frontmatter date,缺失时回退到文件名中的日期
                "date": meta.get("date") or (m.group(0)[:10] if m else ""),
            }
        )
    # 按 date 倒序,无日期的排在最后
    articles.sort(key=lambda a: a["date"] or "0000-00-00", reverse=True)
    return articles


def render_table(articles):
    lines = [TABLE_HEADER, TABLE_SEPARATOR]
    for a in articles:
        link = f"[{escape_cell(a['title'])}]({SITE_URL}/posts/{a['slug']}/)"
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


def update_file(path, block):
    """替换或插入指定文件中的「文章合集」表格,返回是否成功。"""
    text = path.read_text(encoding="utf-8")
    if TABLE_PATTERN.search(text):
        path.write_text(TABLE_PATTERN.sub(block, text), encoding="utf-8")
        return True
    if ANCHOR in text:
        path.write_text(text.replace(ANCHOR, f"{ANCHOR}\n\n{block}", 1), encoding="utf-8")
        return True
    return False


def main():
    articles = collect_articles()
    block = render_table(articles)

    for path in (README, INDEX):
        if update_file(path, block):
            print(f"已更新 {path.name}:{len(articles)} 篇文章")
        else:
            print(
                f"{path.name}: 未找到文章合集表格,请检查是否包含 {ANCHOR}",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
