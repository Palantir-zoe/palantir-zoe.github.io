# Score Functions and Score Matching 维护说明

本篇按第 4 章的 4.1–4.3 节展开，已完成审核并发布至 <https://palantir-zoe.github.io/posts/score-matching/>。

在浏览器中打开本目录的 `preview.html` 阅读。`index.html` 保留文章发布位置使用的相对路径；编辑正文请修改 `tools/content/score-matching.html`，文章信息保存在本目录的 `post.json`。

修改正文后，在仓库根目录运行：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_score_matching_draft.py
```

该命令预先渲染公式，生成本地预览，页面标有“待审核”并设置 `noindex, nofollow`。它不会写入 `docs/`、更新公开目录或执行发布。

审核后，使用下面的命令将正文及引用的图片同步到 `docs/posts/score-matching/`，加入首页目录并重建前后篇导航：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_score_matching_draft.py --publish
```

发布版本移除“待审核”和 `noindex` 标记，保留已审核正文、公式与图片顺序。此命令只准备仓库内的静态网站；提交并推送到 `main` 后，由 GitHub Pages 部署。后续只想检查本地修改时，继续使用不带 `--publish` 的命令。

`images/` 保存原文截图，正文图片支持点击查看原尺寸，配有对应页码与来源。发布时只复制正文引用的图片，并保留完整跨页内容。`images/lecture-original-figures.json` 记录截图的裁剪位置和文件校验信息。原图提取脚本为 `tools/extract_score_matching_figures.py`，读取工作区根目录的 `lecture_notes.pdf`。
