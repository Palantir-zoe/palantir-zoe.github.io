# Diffusion Models 预览与发布

当前内容已审核并发布至 <https://palantir-zoe.github.io/posts/diffusion-models/>。本目录保留编辑工作副本：`preview.html` 可直接在本地浏览器打开，`index.html` 保留文章网址的相对路径。两者均位于 GitHub Pages 发布目录之外。

可编辑正文保存在 `tools/content/diffusion-models.html`。修改后，在仓库根目录运行：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_diffusion_draft.py
```

此命令使用本机已有的 Playwright 环境和 Edge，将公式预先渲染为 HTML，更新本地 `index.html` 和 `preview.html`，标记为待审核，不修改已经上线的 `docs/`。源文件和渲染页面需要一起保留。

`images/` 保存原文 Figure 3 和 Summary 7 的 300 DPI 截图，两张图均可点击打开原尺寸。来源页码、裁切坐标和文件哈希记录在 `images/lecture-original-figures.json`；复现脚本为 `tools/extract_diffusion_figures.py`。发布时会将图片复制到文章目录。

内容核查完成后，在仓库根目录运行：

```powershell
& '.runtime/qa-venv/Scripts/python.exe' tools/render_diffusion_draft.py --publish
```

此命令生成不含“待审核”和 `noindex` 标记的文章，将正文及图片写入 `docs/posts/diffusion-models/`，同步 `post.json` 的目录信息并重建文章导航。随后检查本地页面，提交变更并推送 GitHub。不要将本地 `preview.html` 当成公开页面发布。
