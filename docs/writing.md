# 芦苇 Reed 博客 · 文章维护说明

本站是 Jekyll 站点,部署在 GitHub Pages(custom domain:guide.reeddaily.com)。
文章、目录、上一篇/下一篇、sitemap 均由 Jekyll 自动处理,日常只需要做两件事:
**写文章** 和 **跑一次生成脚本**。

---

## 一、新增一篇文章

1. **创建文件**:在 `_posts/` 下新建文件,命名必须遵循 Jekyll 规范:

   ```
   YYYY-MM-DD-slug.md
   ```

   - `slug` 用 ASCII(英文/数字/连字符),它决定文章 URL:`https://guide.reeddaily.com/posts/<slug>/`
   - 示例:`2026-08-28-best-rss-feeds-for-tech-ai-startups-investing-design.md`

2. **写 frontmatter**(文件头部的 YAML):

   ```yaml
   ---
   title: 文章标题
   description: 一句话简介(可选)
   tags: [标签1, 标签2](可选)
   date: 2026-08-28
   ---
   ```

   `date` 建议与文件名中的日期保持一致。

3. **写正文**(Markdown):

   - 不需要手动写目录——h2/h3 标题会自动生成页内目录;
   - 上一篇/下一篇链接自动生成,不需要手动配置;
   - 注意:正文会被 Jekyll 按 Liquid 解析,如果内容里要出现 `{{` 或 `{%`,
     必须用 `{% raw %}...{% endraw %}` 包住,否则构建会报错或内容丢失。

4. **同步文章合集表格**(README.md 和首页 index.md):

   ```bash
   python3 scripts/gen_collections.py
   ```

   脚本读取 `_posts/*.md` 的 frontmatter,自动更新两个文件中的「文章合集」表格,
   并把链接指向文章页 URL。**每新增/修改一篇文章后跑一次即可。**

---

## 二、修改文章

- 直接编辑 `_posts/<文件名>.md`;
- 改了 **标题 / 简介 / 日期** → 重跑一次 `python3 scripts/gen_collections.py`,
  让 README 和首页的表格同步;
- 想**改文件名**(换 slug 或日期)→ 用 `git mv` 保留历史:

  ```bash
  git mv _posts/2026-08-28-old-slug.md _posts/2026-08-28-new-slug.md
  ```

  ⚠️ 换文件名会改变文章 URL,旧链接会失效(不会自动跳转)。

---

## 三、本地预览

```bash
/opt/homebrew/opt/ruby/bin/bundle exec jekyll serve
```

- 访问 http://127.0.0.1:4000/
- 保存文件后站点会自动重新构建,刷新浏览器即可看到效果
- 注:本机必须用 Homebrew 的 Ruby(系统自带 Ruby 2.6 装不了 Pages 依赖)

---

## 四、发布上线

改完、commit 后推送到 GitHub `main` 分支即可:

```bash
git add -A && git commit -m "..." && git push
```

GitHub Pages 检测到推送会自动构建并部署(通常 1~2 分钟),**不需要手动执行任何构建命令**。
可到仓库 Settings → Pages 查看构建状态。

---

## 五、Sitemap 会自动更新吗?

**会,完全自动。**

- `sitemap.xml` 由 `jekyll-sitemap` 插件在**每次构建时自动生成**,不需要手动维护;
- 新增、修改、删除文章后,只要推送到 GitHub,Pages 重新构建,`sitemap.xml` 就会自动反映最新内容;
- 本地预览地址:http://127.0.0.1:4000/sitemap.xml
  (本地显示 localhost 地址,线上部署后自动使用 `https://guide.reeddaily.com/...`);
- 某篇页面不想被搜索引擎收录,可在该文件 frontmatter 加:

  ```yaml
  sitemap: false
  ```

---

## 常见问题

| 问题 | 答案 |
|------|------|
| 加了文章但 README 表格没变? | 没跑 `python3 scripts/gen_collections.py` |
| 文章页没有目录? | 正文没有 h2 标题;有 h2 就会自动出现 |
| 上一篇/下一篇不显示? | 只有一篇文章时不会显示,第二篇起自动出现 |
| 页面构建报错? | 检查正文是否含未转义的 `{{` / `{%` |
