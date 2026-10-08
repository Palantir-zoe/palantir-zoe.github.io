# 使用方法

在 VS Code 中编辑 Markdown 文件，保存后刷新本地浏览器即可阅读。提交并推送到 GitHub 后，公开网站会自动更新。

## 打开与关闭

在 `learning-notes` 文件夹中双击 `start-notes.cmd`，浏览器会打开笔记站。双击 `stop-notes.cmd` 可以关闭本地服务。

也可以在该文件夹的终端中运行：

```powershell
python serve.py start --open
python serve.py stop
```

## 新增一篇笔记

1. 复制 `docs/templates/note-template.md` 到相应主题目录，例如 `docs/generative-models/02-flow-diffusion.md`。
2. 修改标题，填写概念、推导与例子。
3. 在 `docs/_sidebar.md` 中添加一个入口：

```markdown
- [02 流模型与扩散模型](/generative-models/02-flow-diffusion.md)
```

4. 保存并刷新网页。搜索索引最多可能需要约一分钟更新。

`docs/README.md` 是首页，`docs/assets/config.js` 保存站点配置，`docs/assets/notes.css` 控制阅读样式。

## 公式

行内公式使用一对美元符号，独立公式使用两对美元符号。数学源码直接写在 Markdown 中，不要放在代码块里；代码块用于展示写法。

```markdown
样本满足 $Z\sim P_{\mathrm{data}}$。

$$
\Pr(Z\in A)=\int_A p_{\mathrm{data}}(z)\,\mathrm dz
$$
```

实际效果：样本满足 $Z\sim P_{\mathrm{data}}$。

$$
\Pr(Z\in A)=\int_A p_{\mathrm{data}}(z)\,\mathrm dz
$$

多步推导可以使用 `aligned`：

$$
\begin{aligned}
\operatorname{Var}\!\left(\frac1N\sum_{i=1}^N f(Z_i)\right)
&=\frac1{N^2}\sum_{i=1}^N\operatorname{Var}(f(Z_i))\\
&=\frac{\sigma_f^2}{N}.
\end{aligned}
$$

## 配图与链接

图片保存在 `docs/assets/images/`。在 `generative-models` 子目录的笔记中这样引用：

```markdown
![数据表示](../assets/images/intro-01.png)
```

点击图片可以放大。使用文件的相对路径，不要写电脑上的 `C:\...` 路径。

链接到另一篇笔记可以使用站点根路径：

```markdown
[生成建模基础](/generative-models/01-introduction.md)
```

## 保存修改并更新网站

项目已准备好 Git 忽略规则。站点的源文件、配图与本地依赖可以一起保存，运行日志和检查环境位于 `.runtime/`，不会纳入版本管理。

在项目终端中查看变动：

```powershell
git status
git diff
```

确认要保存的内容后提交并推送：

```powershell
git add docs README.md .gitignore
git commit -m "整理生成建模学习笔记"
git push origin main
```

首次发布需在 GitHub 仓库的 **Settings → Pages** 中选择 **Deploy from a branch → main → /docs** 并保存。预期公开地址为 `https://palantir-zoe.github.io/`，其中 `Palantir-zoe` 是用于发布的 GitHub 用户名，首次发布完成后可访问。

以后每次推送都会触发网站更新，通常需要几分钟。可以在仓库的 **Actions** 页面查看发布进度；发布完成后刷新公开网页即可。保留 `docs/.nojekyll`，让 GitHub Pages 正确提供侧栏文件。

## 本地阅读

服务只监听本机地址。Docsify、公式引擎和字体已经保存在 `docs/assets/vendor/`，阅读不依赖在线 CDN；参考资料的外部链接仍需要网络。

本地阅读与 GitHub Pages 使用同一份 Markdown 和配图，无需另行导出网页。
