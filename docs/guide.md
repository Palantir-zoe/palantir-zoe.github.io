# 更新学习笔记网页

网站入口是 `docs/index.html`，保留 Notion 导出网页的排版。图片、公式样式及字体保存在本地资源目录中，随网页一起发布。

## 从 Notion 导入

1. 在 Notion 中编辑笔记，使用页面菜单导出，格式选择 **HTML**。
2. 解压导出文件，保持 HTML 与配套图片文件夹的相对位置。
3. 在 `learning-notes` 文件夹的终端中执行：

```powershell
python tools/import_html.py 'C:\笔记导出\学习笔记.html'
```

把示例路径替换为实际 HTML 文件路径。导入工具会更新公开入口、收集配套资源，并保留手机阅读优化。

也可以直接修改 `docs/index.html`。再次从 Notion 导入时，页面以新导出文件为准；持续维护的正文建议在 Notion 中修改。

## 本地检查

双击 `start-notes.cmd`，或在终端中运行：

```powershell
python serve.py start --open
```

浏览器会打开本地页面。检查文字、公式和配图，保存修改后刷新即可。关闭服务时，双击 `stop-notes.cmd`，或执行 `python serve.py stop`。

## 发布到 GitHub Pages

仓库：<https://github.com/Palantir-zoe/palantir-zoe.github.io>

目标网址：<https://palantir-zoe.github.io/>，首次发布完成后可访问。

首次配置时，在仓库 **Settings → Pages** 中选择 **Deploy from a branch**，分支为 `main`，目录为 `/docs`，然后保存。保留 `docs/.nojekyll`。

以后每次导入并检查完成，在 `learning-notes` 目录提交并推送：

```powershell
git status
git add docs
git commit -m "更新学习笔记"
git push origin main
```

仓库的 **Actions** 页面可以查看发布进度。发布完成后，读者通过同一个网址查看更新。Notion 中的新修改需要重新导出、导入并推送后，才会出现在网站上。
