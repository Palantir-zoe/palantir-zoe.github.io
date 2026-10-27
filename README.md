# 泛科研学习笔记

保留 Notion 导出网页的阅读排版，用 GitHub Pages 分享学习笔记。每节对应一篇文章，首页 `docs/index.html` 是文章目录；图片、公式字体等资源随网页一起保存。

- 仓库：<https://github.com/Palantir-zoe/palantir-zoe.github.io>
- 公开网址：<https://palantir-zoe.github.io/>

当前公开文章分别位于 `docs/posts/introduction/`、`docs/posts/flow-models/`、`docs/posts/diffusion-models/`、`docs/posts/flow-matching/`、`docs/posts/score-matching/`、`docs/posts/guidance/`、`docs/posts/discrete-diffusion-models/`、`docs/posts/vae-additional-perspectives/`，各目录内的 `index.html` 是对应正文。

PRML 第九章《混合模型与 EM》中文精读笔记位于 `docs/posts/prml-mixture-models-em/`，已整理 K-means、高斯混合、Bernoulli 混合、贝叶斯线性回归及一般 EM 的推导。可编辑分章节正文在 `tools/content/prml-ch09/`，使用 `python tools/render_prml_ch09.py` 重新生成页面与首页目录。原书 PDF 仅用于本地核对，不作为网站文件发布。

Diffusion Models 已完成审核并发布，包含原文 Figure 3 和 Summary 7。可编辑正文在 `tools/content/diffusion-models.html`，本地预览与原图保存在 `drafts/diffusion-models/`；后续编辑、预览与发布步骤见 [维护说明](drafts/diffusion-models/README.md)。

Flow Matching 已完成审核并发布，覆盖第 3 章的 3.1–3.3 节，包含原文 Figure 4–7、Algorithm 3、关键定理和英文总结。可编辑正文在 `tools/content/flow-matching.html`；后续编辑、预览与发布步骤见 [维护说明](drafts/flow-matching/README.md)。

Score Functions and Score Matching 已完成审核并发布，覆盖第 4 章的 4.1–4.3 节，包含原文 Figure 8–10、Algorithm 4、关键定理和完整 Summary 24。可编辑正文在 `tools/content/score-matching.html`；后续编辑、预览与发布步骤见 [维护说明](drafts/score-matching/README.md)。

Guidance: How to Condition on a Prompt 已完成审核并发布，覆盖第 5 章的 5.1–5.2 节，包含原文 Figure 11–13、Algorithm 5 与 Summary 27。可编辑正文在 `tools/content/guidance.html`；后续编辑、预览与发布步骤见 [维护说明](drafts/guidance/README.md)。

Discrete Diffusion Models 第 7 章笔记覆盖 CTMC、速率矩阵、KFE、离散边缘化、交叉熵训练与掩码扩散语言模型，包含原文 Figure 17–20、Algorithm 7–8 及同一短句的完整手算。核心解释与推导都在同一篇正文内。可编辑正文在 `tools/content/discrete-diffusion-models.html`；后续编辑、预览与发布步骤见 [维护说明](drafts/discrete-diffusion-models/README.md)。第 6 章仍为本地草稿。

Additional Perspectives on VAEs 为附录 D 的理论推导审阅稿，涵盖原文第 77–81 页与第 82 页 Figure 22。正文完整展开联合 KL、两方向链式分解、ELBO 两种证明、线性高斯似然与后验、重参数化梯度、摊销推断以及 rate–distortion，并单独核对原文中的条件与笔误。可编辑正文在 `tools/content/vae-additional-perspectives.html`；维护与验证步骤见 [说明](drafts/vae-additional-perspectives/README.md)。公开页面保留“审阅稿”标记。

## 更新内容

1. 在 Notion 中修改某一篇笔记，然后将这一篇单独导出为 HTML。
2. 解压导出包，保留 HTML 文件及其配套资源文件夹。
3. 在 `learning-notes` 目录运行，替换为实际 HTML 文件路径：

```powershell
python tools/import_html.py 'C:\笔记导出\Flow Models.html' --slug flow-models
```

`--slug` 指定要更新的文章。上述命令更新 `docs/posts/flow-models/index.html`，收集配套资源，保留阅读排版，并自动重建首页目录和上一篇／下一篇链接。其他文章的正文不受影响。

新增一篇笔记时，指定新的英文短名称、标题和章节标签：

```powershell
python tools/import_html.py 'C:\笔记导出\新笔记.html' --slug probability-paths --title 'Probability Paths' --section '第 3 节' --description '概率路径的定义与直观理解。'
```

新文章默认排在目录末尾。`docs/posts.json` 管理文章标题、简介和顺序。修改目录信息后，或直接编辑文章 HTML 后，运行：

```powershell
python tools/blog.py
```

首页由 `tools/home-template.html` 生成，不要在 `docs/index.html` 中手写正文。再次导入某篇文章时，该篇正文会以新导出文件为准。MIT 讲义系列文章会自动补充对应章节的参考文献；其他文章请在正文中维护自己的参考文献。

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
