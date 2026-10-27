# Discrete Diffusion Models 笔记维护说明

本篇对照 Peter Holderrieth 与 Ezra Erives 的 *An Introduction to Flow Matching and Diffusion Models*（MIT 6.S184，2026）第 7 章，涵盖 7.1–7.2 节、原文第 54–66 页及 Remark 40。

本地直接打开 `preview.html` 阅读。它使用仓库已有字体、KaTeX 和文章样式，并标为“本地预览”。`index.html` 保留最终文章目录下使用的相对路径，供生成工具使用。正文源文件为 `tools/content/discrete-diffusion-models.html`，文章标题、简介等信息位于本目录的 `post.json`。

在 `learning-notes` 仓库根目录运行：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_discrete_diffusion_draft.py
& '.runtime/qa-venv/Scripts/python.exe' tools/qa_discrete_diffusion_draft.py
```

默认渲染会预先生成公式、图片尺寸、正文目录和本地预览，保留 `noindex, nofollow`，并记录渲染前后 `docs/` 文件哈希，确保公开站点不受影响。

以下命令准备 GitHub Pages 对应的静态文件：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_discrete_diffusion_draft.py --publish
& '.runtime/qa-venv/Scripts/python.exe' tools/qa_discrete_diffusion_draft.py --published
```

`--publish` 把文章和六张原文截图复制到 `docs/posts/discrete-diffusion-models/`，在站点目录的 Guidance 后插入本章，并重建首页与前后篇导航。公开文章移除本地预览和 `noindex` 标记；`drafts/` 内的预览仍保留本地预览标记。此命令只准备仓库静态文件，不执行提交、推送或远程部署。

第 6 章目前保留为本地稿件，站点上一篇导航指向已存在的 Guidance，不会生成到第 6 章公开页面的失效链接。

`images/` 保存 Figure 17–20、Algorithm 7–8 的原文截图。图片可点击查看原尺寸，并附原文页码及 PDF 来源；`images/lecture-original-figures.json` 记录截图尺寸、裁剪坐标和校验值。原文地址：<https://diffusion.csail.mit.edu/2026/docs/lecture_notes.pdf>。

浏览器 QA 逐项比对公式、图片元数据与原图打开行为，检查本地链接、目录锚点和 390/768/1440 像素下全部折叠内容展开的排版。公开模式另外确认目录只存在一条本章记录、公开文章没有 `noindex`。结果保存在 `.runtime/discrete-diffusion-draft-qa/` 或 `.runtime/discrete-diffusion-published-qa/`，渲染审计保存在 `.runtime/discrete-diffusion-render-audit.json`。
