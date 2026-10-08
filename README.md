# 学习笔记

保留 Notion 导出网页的阅读排版，用 GitHub Pages 分享学习笔记。公开网站入口是 `docs/index.html`，图片、公式字体等资源随网页一起保存。

- 仓库：<https://github.com/Palantir-zoe/palantir-zoe.github.io>
- 目标网址：<https://palantir-zoe.github.io/>，首次发布完成后可访问。

## 更新内容

1. 在 Notion 中修改笔记，然后重新导出为 HTML。
2. 解压导出包，保留 HTML 文件及其配套资源文件夹。
3. 在 `learning-notes` 目录运行，替换为实际 HTML 文件路径：

```powershell
python tools/import_html.py 'C:\笔记导出\学习笔记.html'
```

导入工具更新 `docs/index.html`，收集图片和公式资源，并保留手机阅读优化。也可以直接编辑 `docs/index.html`；再次导入时，页面内容会以新的导出文件为准。

页末参考文献保存在 `tools/reference.html`，重新导入 HTML 时会自动保留。

## 本地预览

双击 `start-notes.cmd`，或运行：

```powershell
python serve.py start --open
```

默认地址为 <http://127.0.0.1:3000>。端口被占用时，服务会显示实际地址。关闭时双击 `stop-notes.cmd`，或运行 `python serve.py stop`。

## 发布更新

检查本地页面后，在 `learning-notes` 目录提交并推送：

```powershell
git status
git add docs
git commit -m "更新学习笔记"
git push origin main
```

GitHub Pages 从 `main` 分支的 `/docs` 目录发布。推送后的发布进度可在仓库 **Actions** 页面查看；完成后刷新公开网页即可。保留 `docs/.nojekyll`。

本地预览和 HTML 导入需要 Python 3。详细操作见 [使用方法](docs/guide.md)。
