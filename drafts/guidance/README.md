# Guidance: How to Condition on a Prompt 维护说明

本篇按第 5 章的 5.1–5.2 节展开，已完成审核并发布至 <https://palantir-zoe.github.io/posts/guidance/>。

在浏览器中打开本目录的 `preview.html` 阅读。`index.html` 保留文章最终位置使用的相对路径；编辑正文请修改 `tools/content/guidance.html`，文章信息保存在本目录的 `post.json`。

修改正文后，在仓库根目录运行：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_guidance_draft.py
& '.runtime/qa-venv/Scripts/python.exe' .runtime/guidance-draft-qa.py
```

不带参数的渲染命令预先渲染公式，生成可直接打开的本地预览，页面标注“待审核”并设置 `noindex, nofollow`，不会修改公开 `docs/`。

内容审核后，执行以下命令，将正文与引用的原文图片同步到 `docs/posts/guidance/`，更新首页目录和前后篇导航：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_guidance_draft.py --publish
```

发布版本移除“待审核”和 `noindex` 标记。此命令只准备仓库内的静态网站；提交并推送到 `main` 后，GitHub Pages 才会部署。

`images/` 保存原文截图，支持点击查看原尺寸，并附对应页码与来源。`images/lecture-original-figures.json` 记录截图的裁剪位置和文件校验信息。原文为 Peter Holderrieth 与 Ezra Erives 的 *An Introduction to Flow Matching and Diffusion Models*（MIT 6.S184，2026），本章位于第 34–40 页。

QA 核对正文公式、图片原尺寸、目录及本地链接，并检查桌面与手机视窗下的展开阅读和公式横向滚动。结果保存在 `.runtime/guidance-draft-qa/report.json`，渲染前后的公开文件哈希保存在 `.runtime/guidance-render-audit.json`。
