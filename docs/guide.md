# 更新学习笔记网页

网站首页是文章目录，每节有独立网址，保留 Notion 导出网页的排版。图片、公式样式及字体随网页一起发布。

| 文章 | 正文文件 | 公开网址 |
| --- | --- | --- |
| Introduction | `docs/posts/introduction/index.html` | <https://palantir-zoe.github.io/posts/introduction/> |
| Flow Models | `docs/posts/flow-models/index.html` | <https://palantir-zoe.github.io/posts/flow-models/> |

Diffusion Models 暂时隐藏，待审核内容保存在发布目录之外的 `drafts/diffusion-models/`。审核通过后的恢复步骤见仓库 README。

## 从 Notion 导入

1. 在 Notion 中编辑对应的一篇笔记，使用页面菜单单独导出该篇，格式选择 **HTML**。
2. 解压导出文件，保持 HTML 与配套图片文件夹的相对位置。
3. 在 `learning-notes` 文件夹的终端中执行：

```powershell
python tools/import_html.py 'C:\笔记导出\Flow Models.html' --slug flow-models
```

把示例路径替换为实际 HTML 文件路径。`--slug` 决定更新哪一篇，当前公开文章分别是 `introduction`、`flow-models`。工具更新该篇正文与资源，并同步首页目录和文章导航。已有标题、章节标签和简介默认保留，可通过 `--title`、`--section`、`--description` 更新。未审核的草稿先在 `drafts/` 中编辑，审核完成后再导入发布。

必须提供 `--slug`，避免将整篇笔记覆盖到网站首页。英文短名称只允许小写字母、数字和中间的连字符，例如 `flow-models`。

再次从 Notion 导入时，该篇正文以新导出文件为准；持续维护的正文建议在 Notion 中修改。MIT 三篇笔记缺少参考文献时，工具会根据章节补上官方 PDF 与课程链接；其他文章不自动添加 MIT 文献。

## 新增文章、调整目录

新增文章时，使用尚不存在的短名称，同时填写标题与章节标签：

```powershell
python tools/import_html.py 'C:\笔记导出\新笔记.html' --slug probability-paths --title 'Probability Paths' --section '第 3 节' --description '概率路径的定义与直观理解。'
```

新文章默认放在最后。打开 `docs/posts.json` 可以调整条目的顺序、标题、章节标签和简介。不要随意改已有文章的 `slug`，它决定已分享的网址。

也可以直接编辑对应的 `docs/posts/<slug>/index.html`。改完目录信息或 HTML 后运行：

```powershell
python tools/blog.py
```

这会重建首页和上一篇／下一篇链接。首页样式结构在 `tools/home-template.html`，不要将正文写进自动生成的 `docs/index.html`。共享的文章导航样式在 `docs/assets/blog.css`。

## 本地检查

双击 `start-notes.cmd`，或在终端中运行：

```powershell
python serve.py start --open
```

浏览器会打开本地页面。检查文字、公式和配图，保存修改后刷新即可。关闭服务时，双击 `stop-notes.cmd`，或执行 `python serve.py stop`。

## 发布到 GitHub Pages

仓库：<https://github.com/Palantir-zoe/palantir-zoe.github.io>

公开网址：<https://palantir-zoe.github.io/>。

仓库已配置从 `main` 分支的 `/docs` 发布，无需重复设置。保留 `docs/.nojekyll`。

以后每次导入并检查完成，在 `learning-notes` 目录提交并推送：

```powershell
git status
git add docs
git commit -m "更新学习笔记"
git push origin main
```

仓库的 **Actions** 页面可以查看发布进度。发布完成后，读者通过首页选择文章，也可以直接打开某篇的网址。Notion 中的新修改需要重新导出、导入并推送后，才会出现在网站上。

若修改了导入脚本或首页模板，提交时还要包含对应的 `tools` 文件；普通笔记更新提交 `docs` 即可。
