# 学习笔记

使用 Docsify 5 整理与分享 Markdown 学习笔记，包含中文搜索、KaTeX 公式和图片放大。本地与公开网站使用同一份 `docs/` 内容。

预期公开地址：`https://palantir-zoe.github.io/`，其中 `Palantir-zoe` 是用于发布的 GitHub 用户名，首次发布完成后可访问。

## 启动

双击 `start-notes.cmd`，或在此目录运行 `python serve.py start --open`。默认地址为 http://127.0.0.1:3000 ，端口被占用时会选择可用端口并显示实际地址。

双击 `stop-notes.cmd`，或运行 `python serve.py stop` 可以关闭服务。

## 编辑

- 第一章：`docs/generative-models/01-introduction.md`
- 首页：`docs/README.md`
- 目录：`docs/_sidebar.md`
- 模板：`docs/templates/note-template.md`
- 配图：`docs/assets/images/`
- 使用说明：`docs/guide.md`

编辑后保存并刷新网页。数学公式采用 `$...$` 和 `$$...$$` 写法。

## 发布与更新

GitHub 仓库名使用 `palantir-zoe.github.io`。首次发布时，在仓库的 **Settings → Pages** 中选择 **Deploy from a branch**，分支选择 `main`，目录选择 `/docs`，然后保存。保留 `docs/.nojekyll`。

配置完成后，在本地修改 Markdown、配图或目录，检查阅读效果，再在 `learning-notes` 目录提交并推送：

```powershell
git status
git add docs README.md .gitignore
git commit -m "更新学习笔记"
git push origin main
```

GitHub Pages 会自动发布更新，通常需要几分钟。发布进度可在仓库的 **Actions** 页面查看。新增笔记和公式写法见 [使用方法](docs/guide.md)。

## 依赖

本地预览只需要 Python 3，无需 Node.js。浏览器依赖均已下载到 `docs/assets/vendor/`，版本和来源见该目录中的 `manifest.json`，各包许可证随文件保存。

服务仅提供 `docs/` 中的内容，仅监听 `127.0.0.1`。本地运行信息存放在被 Git 忽略的 `.runtime/`。
