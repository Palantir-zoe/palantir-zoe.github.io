# 2.1 Flow Models 逐句注解

英文引用按第 2.1 节正文顺序排列，随后是中文注解；公式保留原编号，补充推导单独标明。阅读时可以先看一句英文，再看下面的解释。

## Trajectory Vector field ODE and Flow

> We start by defining ordinary differential equations (ODEs).

先认识**常微分方程**，简称 ODE。“微分方程”包含未知函数及其导数：我们已知某个量怎样变化，希望求出这个量本身怎样随时间变化。这里“常”表示未知函数只依赖一个自变量 $t$；状态可以有很多维，并不要求只描述一个数。

> A solution to an ODE is defined by a trajectory, i.e. a function of the form
>
> $X:[0,1]\to\mathbb R^d,\quad t\mapsto X_t,$
>
> that maps from time $t$ to some location in space $\mathbb R^d$.

ODE 的解是一条**轨迹**，也就是“输入时间，输出这个时刻的状态”的函数。$X_t$ 和 $X(t)$ 是同一个意思，下标 $t$ 用来标记时间。$[0,1]$ 是时间范围，$\mathbb R^d$ 表示状态由 $d$ 个实数组成：$d=1$ 时是直线上的位置，$d=2$ 时可以是平面上的坐标，高维时也可以表示图像。求解的目标是得到整个函数 $t\mapsto X_t$，而不仅是一个数。

> Every ODE is defined by a vector field $u$, i.e. a function of the form
>
> $u:\mathbb R^d\times[0,1]\to\mathbb R^d,\quad (x,t)\mapsto u_t(x),$
>
> i.e. for every time $t$ and location $x$ we get a vector $u_t(x)\in\mathbb R^d$ specifying a velocity in space (see Figure 1).

这里讨论的 ODE 由一个**向量场**规定。它输入“位置 $x$ 和时间 $t$”，输出此时此地的速度 $u_t(x)$。速度既有方向，也有大小。例如二维速度 $(2,-1)$ 表示第一坐标增加、第二坐标减小；在很短的时间 $\Delta t$ 内，位置大约变化 $(2\Delta t,-\Delta t)$。$\times$ 表示把位置和时间作为一对输入，不是将它们相乘。

> An ODE imposes a condition on a trajectory: we want a trajectory $X$ that “follows along the lines” of the vector field $u_t$, starting at the point $x_0$.

向量场提供了运动规则，轨迹必须遵循这个规则：从 $x_0$ 出发，每到一个位置，就按**当前时间、当前位置**的速度继续运动。不是任意画一条曲线都算作解。

> We may formalize such a trajectory as being the solution to the equation:

把上述要求写成数学式，就是同时满足：

$$
\frac{\mathrm d}{\mathrm dt}X_t=u_t(X_t).
\tag{1a}
$$

$$
X_0=x_0.
\tag{1b}
$$

> Equation (1a) requires that the derivative of $X_t$ is specified by the direction given by $u_t$.

导数 $\mathrm dX_t/\mathrm dt$ 表示状态在时刻 $t$ 的**瞬时变化率**。可以从平均变化率理解它：

$$
\frac{X_{t+\Delta t}-X_t}{\Delta t}
\quad\xrightarrow{\ \Delta t\to0\ }\quad
\frac{\mathrm dX_t}{\mathrm dt}.
$$

分子是位置变化，分母是经过的时间。时间间隔越来越短，就得到瞬时速度。式 (1a) 要求这个速度等于 $u_t(X_t)$；虽然英文用了 direction，等式实际约束的是完整速度向量，包括方向和大小。右边必须代入 $X_t$，因为它才是此刻真正所在的位置。

> Equation (1b) requires that we start at $x_0$ at time $t=0$.

式 (1b) 是**初始条件**，指定开始时在哪里。仅知道速度还不够：例如 $\mathrm dX_t/\mathrm dt=2$ 时，$X_t=2t+1$ 和 $X_t=2t+5$ 都满足方程，因为它们的导数都是 $2$。再给定 $X_0=1$，就选出了 $X_t=1+2t$。这就是“运动规律 + 初始条件”确定运动过程。

> We may now ask: if we start at $X_0=x_0$ at $t=0$, where are we at time $t$ (what is $X_t$)?

现在的问题是：已知起点和速度规则，经过时间 $t$ 以后会到哪里？上面的恒定速度例子给出了答案 $X_t=x_0+2t$，更复杂的速度场需要其他求解方法。

> This question is answered by a function called the flow, which is a solution to the ODE

**流映射** $\psi_t$ 用来统一记录这个答案。它接收起点 $x_0$，输出从该起点运动到时刻 $t$ 的位置：

$$
\psi:\mathbb R^d\times[0,1]\to\mathbb R^d,
\qquad (x_0,t)\mapsto\psi_t(x_0).
\tag{2a}
$$

$$
\frac{\mathrm d}{\mathrm dt}\psi_t(x_0)
=u_t\bigl(\psi_t(x_0)\bigr).
\tag{2b}
$$

$$
\psi_0(x_0)=x_0.
\tag{2c}
$$

这三式依次表示：定义流的输入输出；要求流遵守速度规则；要求尚未运动时仍位于起点。式 (2b) 中，先通过 $\psi_t(x_0)$ 得到当前位置，再把它代入 $u_t$ 计算速度。求时间导数时，起点 $x_0$ 保持固定。

> For a given initial condition $X_0=x_0$, a trajectory of the ODE is recovered via $X_t=\psi_t(X_0)$.

固定一个起点，就从流映射中取出了一条轨迹。例如恒定速度 $2$ 对应的流为 $\psi_t(x_0)=x_0+2t$；选择 $x_0=1$，得到轨迹 $X_t=1+2t$，选择 $x_0=5$，则得到另一条轨迹。

> Therefore, vector fields, ODEs, and flows are, intuitively, three descriptions of the same object: vector fields define ODEs whose solutions are flows.

三者描述了同一个运动过程的不同方面：向量场提供每个位置的速度；ODE 要求轨迹服从这些速度；流映射记录运动后的结果。给出 $u_t$ 后，还需要解 ODE，才能得到 $\psi_t$。

> As with every equation, we should ask ourselves about an ODE: Does a solution exist and if so, is it unique?

写出方程，并不自动保证它有解，也不自动保证只有一个解。我们希望确认：从指定起点出发，是否确实能在整个时间区间内运动，而且不会出现多个互相矛盾的结果。

> A fundamental result in mathematics is "yes!" to both, as long as we impose weak assumptions on $u_t$:

只要速度场满足一定条件，就能保证存在性和唯一性。接下来的定理给出一组足够的条件。

## Theorem 3 Flow existence and uniqueness

> If $u:\mathbb R^d\times[0,1]\to\mathbb R^d$ is continuously differentiable with a bounded derivative, then the ODE in (2) has a unique solution given by a flow $\psi_t$.

“连续可微”表示 $u$ 的一阶导数存在且连续；“导数有界”表示这些导数的大小有统一上界，限制速度场随输入变化的剧烈程度。在这些条件下，从每个起点出发，都有唯一的运动轨迹，并共同组成流 $\psi_t$。这里限制的是**导数**，并不要求速度 $u_t(x)$ 本身在整个空间有界。

> In this case, $\psi_t$ is a diffeomorphism for all $t$, i.e. $\psi_t$ is continuously differentiable with a continuously differentiable inverse $\psi_t^{-1}$.

**微分同胚**表示映射可逆，并且映射与逆映射都连续可微。固定一个时刻，可以从起点计算当前位置，也可以从当前位置恢复起点：

$$
\psi_t^{-1}\bigl(\psi_t(x_0)\bigr)=x_0.
$$

因此，不同起点不会在同一时刻被映到同一个位置。$\psi_t^{-1}$ 中的 $-1$ 表示逆函数，不是数值倒数 $1/\psi_t$。

> Note that the assumptions required for the existence and uniqueness of a flow are almost always fulfilled in machine learning, as we use neural networks to parameterize $u_t(x)$ and they always have bounded derivatives.

这句的用意是将定理与神经网络速度场联系起来，但 “they always have bounded derivatives” 说得过强：一般神经网络不能无条件保证满足这些假设，具体还取决于结构和激活函数。例如 ReLU 在拐点不可微，不能直接套用“连续可微”的这一定理；这也不意味着 ReLU 速度场就一定没有唯一解。

> Therefore, Theorem 3 should not be a concern for you but rather good news: flows exist and are unique solutions to ODEs in our cases of interest.
>
> A proof can be found in [32, 9].

理解这一节时，先把握定理的作用：在满足相应条件的速度场下，“从起点运动到终点”是一个定义明确的过程。最后一句给出了证明的参考文献；这里使用定理的结论，不需要先掌握完整证明。

## Example 4 Linear Vector Fields

> Let us consider a simple example of a vector field $u_t(x)$ that is a simple linear function in $x$, i.e. $u_t(x)=-\theta x$ for $\theta>0$.

先取一个容易计算的速度场：$u_t(x)=-\theta x$。其中 $\theta$ 是固定的正数，决定运动快慢；负号使速度指向原点。例如一维情况下，$x>0$ 时速度为负，往左移动；$x<0$ 时速度为正，往右移动。虽然写着下标 $t$，这个例子的速度并不显式依赖时间，只取决于当前位置。

> Then the function

$$
\psi_t(x_0)=\exp(-\theta t)x_0 \tag{3}
$$

> defines a flow $\psi$ solving the ODE in Equation (2).

$\exp(a)$ 就是 $e^a$。这里直接给出了解：从 $x_0$ 出发，时刻 $t$ 的位置是 $e^{-\theta t}x_0$。**“求解 ODE”就是找到一个随时间变化的函数，使它的导数等于规定的速度，并满足给定初值。** 下面检查这个函数是否符合这两项要求。

> You can check this yourself by checking that $\psi_0(x_0)=x_0$ and computing

$$
\begin{aligned}
\frac{\mathrm d}{\mathrm dt}\psi_t(x_0)
&\overset{(3)}{=}\frac{\mathrm d}{\mathrm dt}\left(\exp(-\theta t)x_0\right)\\
&\overset{(i)}{=}-\theta\exp(-\theta t)x_0\\
&\overset{(3)}{=}-\theta\psi_t(x_0)
=u_t\bigl(\psi_t(x_0)\bigr),
\end{aligned}
$$

> where in (i) we used the chain rule.

初值检查只需要代入 $t=0$：$e^0x_0=x_0$。求导时，$x_0$ 和 $\theta$ 都是常数。链式法则说：对 $e^{g(t)}$ 求导，先对外层指数函数求导，再乘以内层 $g(t)$ 的导数。这里 $g(t)=-\theta t$，因此

$$
\frac{\mathrm d}{\mathrm dt}e^{-\theta t}
=e^{-\theta t}\cdot(-\theta).
$$

所得速度为 $-\theta e^{-\theta t}x_0$，正好等于“当前位置 $e^{-\theta t}x_0$ 乘以 $-\theta$”，也就是速度场要求的速度。于是初值和 ODE 都满足。

**补充：这个解是怎样想到的？** 要解的是 $\dot X_t=-\theta X_t$。乘上一个能抵消衰减的因子 $e^{\theta t}$，再按乘积求导法则计算：

$$
\frac{\mathrm d}{\mathrm dt}\left(e^{\theta t}X_t\right)
=e^{\theta t}\left(\theta X_t+\dot X_t\right)=0.
$$

导数为零，说明乘积 $e^{\theta t}X_t$ 不随时间改变。它在 $t=0$ 时等于 $x_0$，因此始终有 $e^{\theta t}X_t=x_0$，两边乘以 $e^{-\theta t}$ 就得到 $X_t=e^{-\theta t}x_0$。这里的 $e^{\theta t}$ 称为积分因子；这一步也适用于向量 $X_t$。

> In Figure 3, we visualize a flow of this form converging to $0$ exponentially.

“指数趋近于零”来自 $e^{-\theta t}$ 随时间减小。若把这个运动持续下去，位置会越来越接近原点；在有限时间内收缩因子仍然大于零，所以非零起点不会突然变成零。当前生成过程只取 $t\in[0,1]$，终点是 $e^{-\theta}x_0$。

## Simulating an ODE

> In general, it is not possible to compute the flow $\psi_t$ explicitly if $u_t$ is not as simple as in the previous example.

刚才可以把任意时刻的位置直接写成 $e^{-\theta t}x_0$，这种明确的函数表达式称为解析解。复杂速度场通常无法写出这样方便的表达式，但“没有方便的解析表达式”不等于“解不存在”。

> In these cases, one uses numerical methods to simulate ODEs.

数值方法先把时间划分成小步，再根据当前位置的速度算出下一步位置。这样得到一连串近似位置，逐步逼近 ODE 的运动轨迹。

> Fortunately, this is a classical and well researched topic in numerical analysis, and a myriad of powerful methods exist [21].

ODE 数值求解已有成熟的方法。接下来只需要理解 Euler 和 Heun 两种更新规则。

> One of the simplest and most intuitive methods is the Euler method.

Euler（欧拉）方法的想法是：在很短的一步内，把速度暂时当作不变，于是“位移约等于当前速度乘以时间间隔”。

> In the Euler method, we initialize with $X_0=x_0$ and update via

$$
X_{t+h}=X_t+h\,u_t(X_t)
\qquad(t=0,h,2h,3h,\ldots,1-h) \tag{4}
$$

> where $h=n^{-1}>0$ is the step size and $n\in\mathbb N$ is the number of simulation steps.

$h=n^{-1}=1/n$ 是每一步跨过的时间；总时长是 $1$，所以走 $n$ 步就到终点。例如 $n=10$ 时，$h=0.1$，时间依次为 $0,0.1,0.2,\ldots,1$。更新公式可以从导数的近似写法理解：

$$
\frac{X_{t+h}-X_t}{h}
\approx\frac{\mathrm dX_t}{\mathrm dt}
=u_t(X_t)
\quad\Longrightarrow\quad
X_{t+h}\approx X_t+h\,u_t(X_t).
$$

左侧差商表示这一步的平均速度，我们用起点的瞬时速度代替它。**公式 (4) 中的等号定义的是数值更新，不表示它与精确 ODE 解完全相等。** 下面沿用原文的 $X_t$ 记号表示数值状态，每一步都重新计算当前时间、当前位置的速度。

> For this class, the Euler method will be good enough.

这里先掌握 Euler 更新就足以理解后面的生成采样过程。

> To give you a taste of a more complex method, let us consider Heun’s method defined via the update rule

$$
X'_{t+h}=X_t+h\,u_t(X_t)
$$

> initial guess of new state (same as Euler step)

第一步完全照 Euler 做，得到临时预测位置 $X'_{t+h}$。**这里的撇号 $'$ 表示预测值，并不是对 $X$ 求导。** 例如仍取 $u(x)=-x$，当前 $X_0=2$，步长 $h=0.1$，那么预测位置为 $X'_{0.1}=2+0.1\times(-2)=1.8$。

$$
X_{t+h}=X_t+\frac h2\left(u_t(X_t)+u_{t+h}(X'_{t+h})\right)
$$

> update with average $u$ at current and guessed state

第二步在新时间 $t+h$、预测位置 $X'_{t+h}$ 再算一次速度，并取两次速度的平均值。以上面的数字为例，起点速度是 $-2$，预测终点速度是 $-1.8$，平均为 $-1.9$，最终更新得到

$$
X_{0.1}=2+0.1\times\frac{-2+(-1.8)}2=1.81.
$$

注意，最终这一步仍从旧位置 $2$ 出发；预测值 $1.8$ 只是帮助估计终点速度。

> Intuitively, Heun’s method is as follows: it takes a first guess $X'_{t+h}$ of what the next step could be but corrects the direction initially taken via an updated guess.

Heun 的顺序就是“先预测，再用平均速度修正”。在上述例子中，越靠近原点，速度大小越小，所以一直采用起点速度的 Euler 会多走一点；Heun 考虑了这种减速。精确解是 $2e^{-0.1}\approx1.8097$，可与 Euler 的 $1.8$、Heun 的 $1.81$ 对照。Heun 同样是数值近似，每一步需要计算两次速度。

## Flow models

> We can now construct a generative model via an ODE by making the vector field a neural network vector field $u_t^\theta$.

现在把速度场交给神经网络表示：输入当前状态 $x$ 和时间 $t$，输出此刻应该采用的速度 $u_t^\theta(x)$。有了速度场，就能通过求解 ODE 让状态从起点运动到终点。

> For now, we simply mean that $u_t^\theta$ is a parameterized function $u_t^\theta:\mathbb R^d\times[0,1]\to\mathbb R^d$ with parameters $\theta$.

这个记号可以逐项读：输入是一个 $d$ 维状态和一个时间，输出是一个 $d$ 维速度；$\theta$ 是神经网络中全部可调参数。它与线性例子中控制收缩速度的单个标量 $\theta$ 含义不同。这里首先定义模型怎样工作，尚未解释怎样训练这些参数。

> Later, we will discuss particular choices of neural network architectures.

暂时不必知道具体采用哪种网络结构，只需把网络理解成一个可以根据 $(x,t)$ 计算速度的函数。

> Remember that our goal was to generate samples $z\sim p_{\mathrm{data}}$ from a distribution $p_{\mathrm{data}}$.

$p_{\mathrm{data}}$ 表示目标数据分布；$z\sim p_{\mathrm{data}}$ 读作“$z$ 服从数据分布”，也常用来表示从该分布抽取一个样本。生成的目标是让多次生成的样本整体遵循这种分布。

> In particular, these samples must be random.

生成过程需要具有随机性，才能按照目标分布产生不同样本。

> Note though that an ODE itself is not random but fully deterministic.

在前面的存在唯一性条件下，给定速度场和初值，整个运动轨迹已经确定。以完全相同的初值重复求解同一个 ODE，会得到相同的终点。

> To inject some randomness, we simple make the initial condition $X_0$ random.

因此，可以让起点随机：每次生成先抽取一个新的 $X_0$，再让它沿确定的运动规律前进。**起点随机，给定起点之后的运动确定**，两者并不矛盾。

> Specifically, we choose an initial distribution $p_{\mathrm{init}}$.

$p_{\mathrm{init}}$ 就是抽取起点所用的概率分布，称为初始分布。

> In most cases, we set $p_{\mathrm{init}}=\mathcal N(0,I_d)$ to be a simple standard Gaussian.

$\mathcal N(0,I_d)$ 是 $d$ 维标准高斯分布：均值向量为零，协方差矩阵为 $d\times d$ 单位矩阵 $I_d$。具体抽样时，可以独立生成 $d$ 个服从一维标准正态分布 $\mathcal N(0,1)$ 的数，把它们组成向量 $X_0$。

> Most importantly, whatever distribution you choose, it must be one that we can easily sample from at inference-time.

初始分布的关键要求是容易抽样。这里的 inference-time 指模型训练好以后、实际生成样本的时候。我们必须先得到起点，才能开始求解 ODE。

> A flow model is then described by the ODE

$$
X_0\sim p_{\mathrm{init}}
\qquad\text{random initialization}
$$

$$
\frac{\mathrm d}{\mathrm dt}X_t=u_t^\theta(X_t)
\qquad\text{ODE}
$$

两行分别规定“起点怎么来”和“之后怎么走”。随机抽取一次 $X_0$ 后，就按照神经网络给出的速度持续运动，直到 $t=1$。

> Our goal is to make the endpoint $X_1$ of the trajectory have distribution $p_{\mathrm{data}}$, i.e.

$$
X_1\sim p_{\mathrm{data}}
\quad\Longleftrightarrow\quad
\psi_1^\theta(X_0)\sim p_{\mathrm{data}}
$$

$X_1$ 与 $\psi_1^\theta(X_0)$ 是同一个终点的两种写法，因此两边等价。这个等式表达的是理想目标：反复抽取起点并生成样本，终点的整体分布应当等于数据分布；实际训练通常只能使它们接近。它并未规定某一个噪声起点必须对应某一个指定的训练样本。

> where $\psi_t^\theta$ describes the flow induced by $u_t^\theta$.

$\psi_t^\theta$ 是该速度场对应的流映射：给它一个起点，它返回经过时间 $t$ 后的位置。上标 $\theta$ 表示速度场和流映射都取决于同一组网络参数。

> Note however: although it is called flow model, the neural network parameterizes the vector field, not the flow.

需要分清网络直接输出什么：$u_t^\theta(x)$ 输出的是**速度**，而 $\psi_t^\theta(x_0)$ 输出的是**从起点运动一段时间后的位置**。一次调用速度网络，并不能直接得到整个运动的终点。

> In order to compute the flow, we need to simulate the ODE.

因此，计算流映射需要求解 ODE；例如，用 Euler 方法反复执行“查询当前速度、前进一步”。

> In Algorithm 1, we summarize the procedure how to sample from a flow model.

下面把这个生成过程写成算法。它假定速度网络已经给定，执行的是采样过程，网络参数不会在这些步骤中更新。

## Algorithm 1 Sampling from a Flow Model with Euler method

> Require: Neural network vector field $u_t^\theta$, number of steps $n$

准备好速度网络和步数 $n$；算法还使用模型选定的初始分布 $p_{\mathrm{init}}$。

> 1: Set $t=0$

从初始时刻开始。

> 2: Set step size $h=\frac1n$

把长度为 $1$ 的时间区间均分为 $n$ 步，每一步经过时间 $h$。

> 3: Draw a sample $X_0\sim p_{\mathrm{init}}$

随机抽取一个起点。这是一次生成过程中引入随机性的地方。

> 4: for $i=1,\ldots,n$ do

下面的更新重复执行 $n$ 次；$i$ 只是计数器。

> 5: $X_{t+h}=X_t+h\,u_t^\theta(X_t)$

把当前状态和时间输入网络，得到当前速度，再乘以步长，得到这一小步的近似位移。将位移加到当前位置上，就得到下一位置。这里沿用原文记号 $X$；实际计算的是数值近似。

> 6: Update $t\leftarrow t+h$

时间也前进一小步。下一次调用网络时，要使用新时间和新状态。

> 7: end for

完成 $n$ 次更新后，时间到达 $t=1$。

> 8: return $X_1$

输出最终状态作为一个生成样本。由于使用 Euler 方法，它是精确 ODE 终点的近似；重新从第 1 步执行、抽取新的起点，就可以继续生成样本。
