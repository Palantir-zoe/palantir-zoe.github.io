# Flow Matching 维护说明

本篇按第 3 章的 3.1–3.3 节展开，已完成审核并发布至 <https://palantir-zoe.github.io/posts/flow-matching/>。

在浏览器中打开 `preview.html` 阅读；`index.html` 保留文章发布位置使用的相对路径。可编辑正文为 `tools/content/flow-matching.html`，文章信息为本目录的 `post.json`。

修改正文后，在仓库根目录运行：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_flow_matching_draft.py
```

此命令预先渲染公式并生成本地页面，不修改 `docs/` 或公开目录。草稿页面标有“待审核”，并设为 `noindex, nofollow`。

审核后，使用下面的命令将正文及引用的图片同步到 `docs/posts/flow-matching/`，加入首页目录并重建前后篇导航：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_flow_matching_draft.py --publish
```

发布版本移除“待审核”和 `noindex` 标记，保持当前正文、公式与图片顺序。此命令只准备仓库内的静态网站；提交并推送到 `main` 后，由 GitHub Pages 部署。后续只想检查本地修改时，继续使用不带 `--publish` 的命令。

`images/` 保存原文的 300 DPI 截图。当前正文使用 Figure 4–7、Algorithm 3、Theorem 9、11、12 和跨两页的 Summary 14，共 10 张图片；发布时仅复制正文引用的图片。页面中的图片可点击查看原尺寸。来源、页码、裁剪位置与文件哈希保存在 `images/lecture-original-figures.json`。

原图提取脚本为 `tools/extract_flow_matching_figures.py`，读取工作区根目录的 `lecture_notes.pdf`，需要 Poppler 的 `pdftoppm` 和 Pillow。正文引用原文时注明了作者、课程、年份和页码。
