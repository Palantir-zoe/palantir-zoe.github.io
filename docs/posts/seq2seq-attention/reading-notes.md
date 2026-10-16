# 从 RNN Seq2Seq 到 Attention：中文阅读笔记

> 这是一份基于 Jay Alammar 2018 年可视化文章整理的中文阅读笔记与改编图解说明，不是逐句直译。用于串起经典 RNN 编码器—解码器、Attention 的动机与计算流程，作为继续学习 Transformer 的前置背景。

## 参考原文

Jay Alammar, “Visualizing A Neural Machine Translation Model (Mechanics of Seq2seq Models With Attention)” (2018)：
<https://jalammar.github.io/visualizing-neural-machine-translation-mechanics-of-seq2seq-models-with-attention/>

原文介绍 Seq2Seq 编码器—解码器、词嵌入、RNN 隐藏状态、固定上下文向量的瓶颈，以及 Bahdanau/Luong Attention 的基本想法和可视化。原文页面标注 CC BY-NC-SA 4.0。

## 为什么从 Transformer 回头看 RNN？

Transformer 的核心机制之一是 Attention。理解 Attention 的来由，可以先看它在经典 RNN Seq2Seq 翻译模型里解决了什么问题。

经典编码器按顺序读源句，每一步根据当前词的 embedding 和上一步隐藏状态更新状态。基础 Seq2Seq 通常把编码器最后的状态当作整句的固定长度摘要交给解码器。这个设计简单，但较长的输入要压缩进一个向量，可能造成信息瓶颈：解码某个词时，早先读到的细节不一定容易保留。

Attention 的关键变化是：解码器不只依赖一个最终摘要，而是在每个生成步骤都能访问编码器各个位置的隐藏状态。当前步骤根据已有解码信息与源位置表示的匹配程度计算读取权重，再汇总出与当前输出相关的上下文。

这解释了 Attention 在该类模型中的动机：让解码器可以按需读取输入句子的不同部分。它并不意味着 RNN 隐藏状态不再参与计算；编码器和解码器仍然可以是循环网络，Attention 是增加在解码过程中的读取机制。

## 一次 Attention 读取怎样计算？

对某个解码步骤，可以把过程概括为：

1. **打分**：用当前查询状态与每个源位置的表示计算匹配分数。
2. **归一化**：对分数做 softmax，得到非负且总和为 1 的权重。
3. **加权求和**：按权重汇总编码器各位置的隐藏状态，得到当前步骤的上下文向量。
4. **预测**：把上下文与解码信息交给后续网络，计算下一个目标词的概率分布。

如果源状态记作 \(h_j\)，注意力权重记作 \(\alpha_{t,j}\)，那么上下文可写成：

\[
c_t = \sum_j \alpha_{t,j} h_j
\]

这里的 \(h_j\) 是编码器在源句第 \(j\) 个位置产生的表示，通常已包含该位置周围的上下文；\(c_t\) 是解码器在第 \(t\) 步按权重读出的信息。它们与解码器状态 \(s_t\) 不同：\(h_j\) 表示源句，\(s_t\) 表示目标端生成过程。

## 热力图应该怎样读？

图中的例子把英语源句 “European Economic Area” 译为法语 “zone économique européenne”。两种语言表达同一名称，但词序有所不同。

- 每一列对应一个源句位置，例如 European、Economic、Area。
- 每一行对应一次目标词生成，例如 zone、économique、européenne。
- 一行里的数字表示这一步对各个源位置分配的注意力权重。

因此，某一步可能主要读取 Area 对应的表示来生成 zone；这并不表示 zone 的概率就等于该位置的注意力权重。Attention 权重是读取比例，目标词概率还由后续网络计算。

软对齐也不是严格的一词对一词配对。多个源位置可以共同影响一个目标词；同一源位置也可以在多个生成步骤被再次读取。每一行权重会归一化为 1；各列加起来不必为 1。

本套图中出现的权重、二维向量和算分结果均为教学示意，用来演示读图或算式，并非训练模型的实测值。

## Luong 与 Bahdanau：计算顺序的一个经典区别

两种经典 Attention 做法的一个教学性对照，是本步解码状态更新与读取源句信息的顺序。以已经生成 “I am a”、接下来要预测第 4 个词为例：

- **Luong 的简化顺序**：用旧状态和前一个目标词 embedding 算出本步新状态 \(s_4\)；再用 \(s_4\) 查询源状态，得到上下文 \(c_4\)；结合信息预测下一个词。
- **Bahdanau 的简化顺序**：先用旧状态 \(s_3\) 查询源状态，得到 \(c_4\)；再将旧状态、前一个目标词 embedding 与上下文用于计算新状态 \(s_4\)；之后预测下一个词。

这只是对经典主要计算顺序的简化描述，具体实现可以包含额外连接或变体。这里的状态更新是一次网络前向计算；模型参数则是在训练中通过损失和反向传播学习的。\(s_3\)、\(s_4\) 是向量状态，不是单词，也不是参数。

评分函数和计算顺序是两个不同的设计点。常见评分方式包括 Luong 论文里的 dot/general，以及 Bahdanau 论文里的 additive；不应把某一种评分公式说成所有相应模型的唯一形式。

## 它与 Transformer 的关系

这套笔记解释的是经典 RNN Seq2Seq 语境下的 Attention 动机和读取过程。Transformer 进一步把注意力作为核心构件，并采用自注意力在序列表示之间建立联系，不使用 RNN 式的逐步循环状态更新。因此，这套图适合作为注意力直觉的历史背景，不能当作 Transformer 架构图或其完整公式说明。

## 图包阅读顺序

配套小红书图包的 16 张图按以下顺序阅读：

`01—11 → 12A → 12B → 13A → 13B → 14`

- 01—05：Seq2Seq、embedding、RNN 与固定上下文瓶颈。
- 06—10：Attention 动机、打分、softmax、加权求和与解码流程。
- 11：训练与生成的区别。
- 12A—13B：热力图、权重汇总、Luong/Bahdanau 顺序和评分函数补充。
- 14：回顾主线。

## 来源、改编与许可

- 原文：Jay Alammar, “Visualizing A Neural Machine Translation Model (Mechanics of Seq2seq Models With Attention)” (2018), <https://jalammar.github.io/visualizing-neural-machine-translation-mechanics-of-seq2seq-models-with-attention/>。
- 原文页面标注许可：Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International（CC BY-NC-SA 4.0）：<https://creativecommons.org/licenses/by-nc-sa/4.0/>。
- 本文是中文阅读笔记和改编图解，保留原作者署名、原文链接、改编说明，并采用相同许可。原作者未审阅或背书。若再发布或改编，请遵循许可条款。
- 补充的图示、向量算例与注意力权重为教学示意，不属于原文实测数据。
