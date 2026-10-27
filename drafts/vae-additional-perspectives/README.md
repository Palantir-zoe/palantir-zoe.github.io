# Additional Perspectives on VAEs 笔记维护说明

本篇为审阅稿，对照 Peter Holderrieth 与 Ezra Erives 的 *An Introduction to Flow Matching and Diffusion Models*（MIT 6.S184，2026）附录 D，覆盖原文第 77–81 页及第 82 页 Figure 22。

正文源文件为 `tools/content/vae-additional-perspectives.html`。`post.json` 保存文章标题、简介和“附录 D · 审阅稿”标记。直接打开 `preview.html` 可以阅读；预览使用仓库已有字体、KaTeX 和文章样式。`index.html` 使用最终文章目录下的相对路径，供生成工具使用。

在 `learning-notes` 仓库根目录运行：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_vae_perspectives_draft.py
& '.runtime/qa-venv/Scripts/python.exe' tools/qa_vae_perspectives_draft.py
```

默认渲染生成静态公式、图片尺寸、正文目录和本地预览，保留 `noindex, nofollow`，并比对 `docs/` 全部文件哈希，确保公开站点不受影响。

以下命令准备 GitHub Pages 静态文件：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_vae_perspectives_draft.py --publish
& '.runtime/qa-venv/Scripts/python.exe' tools/qa_vae_perspectives_draft.py --published
```

`--publish` 将文章、四张原文截图及图片元数据写入 `docs/posts/vae-additional-perspectives/`，在站点目录的 Discrete Diffusion Models 后插入本篇，并重建首页与前后篇导航。公开页面与目录继续标为“审阅稿”；公开页面移除“本地预览”和 `noindex`。此命令只准备仓库静态文件，不提交、不推送，也不执行远程部署。第 6 章本地稿不受影响。

`images/` 保存 Proposition 3（第 78 页）、Remark 42/43（第 80 页）和 Figure 22（第 82 页）的完整原文框或图及图注。截图使用 Poppler 直接以 300 DPI 渲染原 PDF 区域，没有重绘、OCR 替换或缩放。元数据 `images/lecture-original-figures.json` 记录来源 PDF SHA256、页码、裁剪坐标、图片尺寸与校验值。可运行 `tools/extract_vae_perspectives_figures.py` 复现。

原文 Remark 42/43 的理论与排版问题，以及 Figure 22 图注左右标记笔误，在正文单独说明；截图保留原样，避免把修订误认为讲义原文。原文地址：<https://diffusion.csail.mit.edu/2026/docs/lecture_notes.pdf>。

QA 检查公式数量与顺序、目录锚点、表头 scope、原图尺寸与哈希、图片打开行为、本地链接、资源请求，以及 390/768/1440 像素宽度下展开全部折叠内容后的排版。公开模式另外检查目录只有一条记录且位于第 7 章后、保留审阅稿标记、没有本地预览及 `noindex`。渲染审计位于 `.runtime/vae-perspectives-render-audit.json`；截图与 QA 报告位于 `.runtime/vae-perspectives-draft-qa/` 或 `.runtime/vae-perspectives-published-qa/`。
