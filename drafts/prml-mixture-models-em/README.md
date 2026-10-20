# PRML 第九章笔记：维护说明

审阅地址：<https://palantir-zoe.github.io/posts/prml-mixture-models-em/>

## 来源与范围

依据本地 `Pattern Recognition and Machine Learning.pdf` 第九章，印刷页 423–455。页面是原创中文学习解读，含推导、四点数值例子、原创图解和 EM 互动演示。原书 PDF 不属于站点资源，也没有添加到此仓库。

作者官方书籍页面：<https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/>。

正文在 `tools/content/prml-ch09/` 按阅读顺序拆为六个 HTML 片段，目录与标题信息在同目录 `post.json`。修改内容后，在仓库根目录运行：

```powershell
python tools/render_prml_ch09.py
```

它使用仓库现有的 KaTeX 静态资源编译公式，生成 `docs/posts/prml-mixture-models-em/index.html`，并更新 `docs/posts.json`、网站首页和上一篇／下一篇导航。构建依赖本地 `.runtime/qa-venv/Lib/site-packages/playwright/driver/node.exe` 与 `.runtime/katex-0.16.25.min.js`。发布后，网页本身不依赖这些本地构建工具。

## 审阅重点

- 第 9.2 节：责任度与均值、协方差、混合比例更新是否足够清楚。
- 四点例子：E 步与 M 步的数字和互动曲线是否能帮助理解。
- 第 9.3.4 节：贝叶斯线性回归中的权重后验、二阶矩与超参数更新是否有需补充的前置知识。
- 第 9.4 节：下界、KL 间隙与单调性证明是否容易跟上。

可直接反馈网址中的小节锚点及需要修改的段落。页面标记“审阅稿 v1”，审阅意见可继续进入相应的正文片段。
