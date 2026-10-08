"""Fifteen whiteboards following lecture_notes.pdf section 2.1 in source order.

Run with Python + numpy + matplotlib. Fonts: Microsoft YaHei or Noto Sans CJK SC.
The numerical-method boards are in flow_walkthrough_numerics.py.
"""
from flow_walkthrough_common import *
from matplotlib.backends.backend_pdf import PdfPages
import json
import math
import shutil
import zipfile


def board01():
    f=base(1,'先看清状态 x 表示什么','Trajectory · 轨迹的状态空间','把一个完整样本写成一个向量，才能谈论它在空间中的位置。')
    ax=f.add_axes([.085,.425,.255,.235])
    ax.imshow([[.2,.8]],cmap='gray',vmin=0,vmax=1,interpolation='nearest')
    ax.set_xticks([0,1],['第 1 个像素','第 2 个像素'],fontsize=15)
    ax.set_yticks([])
    ax.text(0,0,'0.2',ha='center',va='center',color='white',fontsize=26)
    ax.text(1,0,'0.8',ha='center',va='center',color=INK,fontsize=26)
    txt(f,.08,.735,'一个只有两个灰度值的样本',20)
    txt(f,.08,.343,r'$x=(x_1,x_2)=(0.2,0.8)$',25,BLUE)
    arrow(f,(.36,.54),(.52,.54),BLUE)
    txt(f,.435,.607,'整体对应一个点',17,BLUE,ha='center')
    ax=f.add_axes([.585,.385,.30,.36])
    ax.scatter([.2],[.8],s=90,color=BLUE,zorder=5)
    ax.plot([.2,.2,0],[0,.8,.8],ls='--',lw=1.2,color=GRAY)
    ax.annotate(r'$x=(0.2,0.8)$',(.2,.8),xytext=(15,9),textcoords='offset points',fontsize=21,color=BLUE)
    ax.set(xlim=(0,1),ylim=(0,1),xticks=[0,.2,1],yticks=[0,.8,1])
    style(ax,r'$x_1$  第一个数值',r'$x_2$')
    txt(f,.56,.275,'坐标轴表示数值分量，不是像素的几何坐标。',16,GRAY)
    txt(f,.08,.218,r'一般样本：$x\in\mathbb{R}^d$',24)
    txt(f,.51,.218,'图片的 d 可以很大；后面先用 d = 1 看清运动。',17)
    footer(f,'样本的数值改变，等价于表示这个样本的点在状态空间中移动。')
    return f


def board02():
    f=base(2,'轨迹是时间到状态的函数','Trajectory · 轨迹','先描述一条路径；此时还没有规定它必须遵循哪种运动规则。')
    ax=f.add_axes([.085,.345,.40,.39])
    ts=np.linspace(0,1,100)
    ax.plot(ts,2-ts,lw=3,color=BLUE)
    ax.scatter([0,.5,1],[2,1.5,1],s=55,color=[BLUE,ORANGE,BLUE],zorder=5)
    ax.plot([.5,.5,0],[0,1.5,1.5],ls='--',color=ORANGE,lw=1.3)
    ax.set(xlim=(0,1.06),ylim=(0,2.2),xticks=[0,.5,1],yticks=[0,1,1.5,2])
    style(ax,r'$t$  时间',r'$X_t$')
    ax.annotate(r'$X_{0.5}=1.5$',(.5,1.5),xytext=(15,24),textcoords='offset points',fontsize=23,color=ORANGE)
    txt(f,.085,.758,r'示例路径：$X_t=2-t$',20)
    txt(f,.56,.71,r'$X:[0,1]\longrightarrow\mathbb{R}^d$',27)
    txt(f,.56,.62,r'$t\longmapsto X_t$',29,BLUE)
    txt(f,.56,.517,'输入一个时刻，返回当时的状态。',21)
    txt(f,.56,.419,r'$X_0=2,\quad X_{0.5}=1.5,\quad X_1=1$',23)
    txt(f,.56,.319,'这里 t 连续变化，不只是整数编号。',18)
    txt(f,.085,.235,'横轴是时间，纵轴是一维状态；这张图不是二维样本空间。',19,GRAY)
    txt(f,.085,.175,r'下标 $t$ 标记时间；$x_1,x_2$ 的下标标记向量分量。',19)
    footer(f,'接下来要问：什么样的路径才符合我们指定的运动规则？')
    return f


def board03():
    f=base(3,'向量场为每个位置指定速度','Vector field · 向量场','固定一个时刻，询问每个位置现在应朝哪里走、走多快。')
    txt(f,.075,.735,r'$u:\mathbb{R}^d\times[0,1]\to\mathbb{R}^d,\qquad (x,t)\mapsto u_t(x)$',28)
    ax=f.add_axes([.08,.49,.415,.14])
    for x in [-2,-1,0,1,2]:
        ax.scatter([x],[0],s=40,color=INK,zorder=5)
        if x:
            ax.annotate('',(x-.3*x,0),(x,0),arrowprops=dict(arrowstyle='->',lw=2.4,color=BLUE))
    ax.axhline(0,color=LIGHT,zorder=0);ax.set(xlim=(-2.6,2.6),ylim=(-.35,.35),yticks=[],xticks=[-2,-1,0,1,2])
    style(ax,r'$x$  当前位置','')
    txt(f,.08,.393,r'示例：$u_t(x)=-x$',25,BLUE)
    txt(f,.08,.31,'正位置上的负速度：向左移动。',19)
    txt(f,.08,.242,'负位置上的正速度：向右移动。',19)
    txt(f,.08,.174,'箭头按同一比例缩放，长度表示速度大小。',16,GRAY)
    tabax=f.add_axes([.56,.32,.36,.31]);tabax.axis('off')
    tab=tabax.table(cellText=[['−2','+2','向右'],['−1','+1','向右'],['0','0','静止'],['1','−1','向左'],['2','−2','向左']],
                    colLabels=['位置 x',r'速度 $u_t(x)$','方向'],cellLoc='center',loc='center')
    tab.auto_set_font_size(False);tab.set_fontsize(17);tab.scale(1,2.05)
    for (r,c),cell in tab.get_celld().items():
        cell.set_edgecolor(LIGHT)
        if r==0:cell.set_facecolor('#f3f5f7')
    txt(f,.56,.18,'此例恰好不随 t 变化；一般速度场可以随 t 变化。',15.5,GRAY)
    footer(f,'位置和速度是不同的量：速度乘以一小段时间，才得到近似位移。')
    return f


def board04():
    f=base(4,'ODE 要求轨迹的斜率等于指定速度','ODE and initial conditions · 式 1a 与式 1b','轨迹描述怎么走；ODE 检查这条轨迹是否遵守向量场。')
    ax=f.add_axes([.085,.355,.40,.365])
    ts=np.linspace(0,.8,100)
    ax.plot(ts,2*np.exp(-ts),lw=2.8,color=BLUE,label='满足速度条件的轨迹')
    ax.plot(ts,2-ts,lw=1.8,ls='--',color=GRAY,label='另一条同起点路径')
    ax.plot([0,.25],[2,1.5],lw=2.3,color=ORANGE)
    ax.scatter([0],[2],s=65,color=INK,zorder=5)
    ax.annotate('起点要求斜率 −2',(.16,1.68),xytext=(.27,1.84),fontsize=16,color=ORANGE,
                arrowprops=dict(arrowstyle='-',color=ORANGE))
    ax.set(xlim=(-.02,.85),ylim=(.8,2.15),xticks=[0,.4,.8],yticks=[1,1.5,2])
    style(ax,r'$t$  时间',r'$X_t$')
    ax.legend(frameon=False,loc='upper right',fontsize=12)
    txt(f,.085,.755,r'固定规则 $u_t(x)=-x$，初始位置 $x_0=2$',18)
    txt(f,.55,.71,r'$\frac{\mathrm{d}X_t}{\mathrm{d}t}=u_t(X_t)$',32,BLUE)
    txt(f,.55,.616,'左边：轨迹实际的瞬时变化率。',19)
    txt(f,.55,.55,'右边：在当前状态查询到的速度。',19)
    txt(f,.55,.453,r'$X_0=x_0$',29,ORANGE)
    txt(f,.55,.373,'初始条件规定从哪里开始。',19)
    txt(f,.55,.288,r'$\dot X_0=u_0(2)=-2$',27)
    txt(f,.085,.197,r'$\lim_{h\to0}\frac{X_{t+h}-X_t}{h}=u_t(X_t)$',26)
    txt(f,.55,.195,'瞬时速度是平均变化率的极限。',17,GRAY)
    footer(f,'只给起点不够，只给速度规则也不够；两者一起确定运动问题。')
    return f


def board05():
    f=base(5,'Flow 回答从某个起点最终走到哪里','Flow · 式 2a 至式 2c','把初值和终止时刻作为输入，把求解 ODE 得到的位置作为输出。')
    box(f,.075,.63,.18,.105,r'$(x_0,t)$',BLUE,27)
    arrow(f,(.27,.682),(.375,.682))
    box(f,.39,.63,.22,.105,'求解同一个 ODE',INK,21)
    arrow(f,(.625,.682),(.73,.682))
    box(f,.745,.63,.20,.105,r'$\psi_t(x_0)=X_t$',BLUE,25)
    txt(f,.085,.542,r'固定起点 $x_0$，改变 t：看一条轨迹',19)
    ax=f.add_axes([.09,.28,.34,.205]);ts=np.linspace(0,1,100)
    ax.plot(ts,2*np.exp(-ts),color=BLUE,lw=2.6)
    ax.scatter([.5],[2*np.exp(-.5)],s=45,color=ORANGE)
    ax.set(xlim=(0,1),ylim=(0,2.2),xticks=[0,1],yticks=[])
    style(ax,r'$t$',r'$\psi_t(x_0)$')
    txt(f,.54,.542,r'固定时刻 t，改变 $x_0$：看一个映射',19)
    ax=f.add_axes([.60,.28,.29,.205]);xs=np.linspace(-2,2,50)
    ax.plot(xs,np.exp(-.5)*xs,color=BLUE,lw=2.6)
    ax.set(xlim=(-2.1,2.1),ylim=(-1.4,1.4),xticks=[0],yticks=[0])
    style(ax,r'$x_0$',r'$\psi_t(x_0)$')
    txt(f,.08,.186,r'$\partial_t\psi_t(x_0)=u_t(\psi_t(x_0)),\qquad\psi_0(x_0)=x_0$',27)
    footer(f,'两幅示意图只是观察角度不同；具体的流映射将在 Example 4 中算出。',18)
    return f


def board06():
    f=base(6,'这样的解存在吗，会不会有两种答案','Theorem 3 · Flow existence and uniqueness','在定理的正则性条件下，解存在且唯一，流映射还是微分同胚。')
    q=np.linspace(-1.65,1.65,6)
    for j,t in enumerate([0,.5,1]):
        ax=f.add_axes([.08+j*.30,.405,.23,.31]);a=np.exp(-t)
        for level in q:
            ax.plot(q*a,np.full_like(q,level*a),color=BLUE,lw=1)
            ax.plot(np.full_like(q,level*a),q*a,color=BLUE,lw=1)
        pts=np.array([[1,.4],[1.55,.8]])*a
        ax.scatter(pts[:,0],pts[:,1],s=30,color=ORANGE,zorder=5)
        ax.set(xlim=(-2,2),ylim=(-2,2),aspect='equal',xticks=[-2,0,2],yticks=[-2,0,2])
        style(ax,r'$x_1$',r'$x_2$');ax.set_title(f'$t={t:g}$',fontsize=21,pad=8)
    txt(f,.08,.308,'同一张网格连续变形；两个橙色点靠近，但仍能分别找回各自的起点。',18)
    txt(f,.08,.229,'一个充分条件：u 连续可微，且导数有界。',21)
    txt(f,.08,.16,r'唯一解 $\psi_t$；$\psi_t$ 与逆映射 $\psi_t^{-1}$ 均连续可微。',22,BLUE)
    footer(f,'定理说明何时可以放心求解；这些条件需具体检查，不能对任意网络自动断言。',17)
    return f


def board07():
    f=base(7,'线性速度场为什么得到指数解','Example 4 · Linear Vector Fields · 式 3','现在真正求一次 ODE：速度与当前位置成正比，并指向原点。')
    txt(f,.075,.737,r'$u_t(x)=-\theta x,\quad\theta>0,\qquad\dot X_t=-\theta X_t$',29,BLUE)
    txt(f,.075,.64,'① 乘上积分因子，使乘积的导数恰好抵消',20)
    txt(f,.10,.554,r'$\frac{\mathrm{d}}{\mathrm{d}t}(e^{\theta t}X_t)=\theta e^{\theta t}X_t+e^{\theta t}(-\theta X_t)=0$',27)
    txt(f,.075,.455,'② 导数为零，所以乘积保持初始值',20)
    txt(f,.10,.38,r'$e^{\theta t}X_t=e^0X_0=x_0$',29)
    txt(f,.075,.284,'③ 除以指数因子，得到任意初值对应的解',20)
    txt(f,.10,.194,r'$X_t=e^{-\theta t}x_0\quad\Longrightarrow\quad\psi_t(x_0)=e^{-\theta t}x_0$',31,BLUE)
    footer(f,'这里 θ 是一个正标量：它控制收缩速度，θ 越大，同样时间内收缩越快。',18)
    return f


def board08():
    f=base(8,'把解析解代回方程，再读出具体数值','Example 4 · 初值检验与链式法则','先确认它真的满足要求，再把公式变成可以读懂的运动。')
    ax=f.add_axes([.085,.395,.39,.32]);ts=np.linspace(0,1,160)
    ax.plot(ts,2*np.exp(-ts),color=BLUE,lw=2.8)
    vals=2*np.exp(-np.array([0,.5,1.]));ax.scatter([0,.5,1],vals,color=ORANGE,s=45,zorder=4)
    for t,y,label,offset in zip([0,.5,1],vals,['2','1.2131','0.7358'],[(8,9),(10,12),(-68,15)]):
        ax.annotate(label,(t,y),xytext=offset,textcoords='offset points',fontsize=18,color=ORANGE)
    ax.set(xlim=(0,1.04),ylim=(0,2.25),xticks=[0,.5,1],yticks=[0,1,2]);style(ax,r'$t$',r'$X_t$')
    txt(f,.085,.755,r'取 $\theta=1,\ x_0=2$：$X_t=2e^{-t}$',21)
    txt(f,.55,.711,'检验 1：初始条件',20)
    txt(f,.57,.643,r'$\psi_0(x_0)=e^0x_0=x_0$',26)
    txt(f,.55,.541,'检验 2：时间导数等于当前位置的速度',18)
    txt(f,.57,.468,r'$\partial_t\psi_t(x_0)=-\theta e^{-\theta t}x_0$',25)
    txt(f,.57,.39,r'$=-\theta\psi_t(x_0)=u_t(\psi_t(x_0))$',25,BLUE)
    txt(f,.085,.267,'有限时间内比例因子仍大于零，所以可以反向恢复：',19)
    txt(f,.10,.18,r'$\psi_t^{-1}(x)=e^{\theta t}x,\qquad e^1\times(2e^{-1})=2$',28)
    footer(f,'先求出解析式，再代回验证；下一步才讨论没有解析式时怎样计算。',18)
    return f


def board13():
    f=base(13,'用神经网络表示刚才的速度场','Flow models · Neural network vector field','ODE 和求解器已经准备好，现在为速度规则引入可学习的参数。')
    box(f,.075,.535,.20,.16,r'$(x,t)$',BLUE,32)
    arrow(f,(.29,.615),(.385,.615))
    box(f,.40,.535,.20,.16,r'$\mathrm{NN}_{\theta}$',INK,32)
    arrow(f,(.615,.615),(.715,.615))
    box(f,.73,.535,.215,.16,r'$u_t^{\theta}(x)$',ORANGE,32)
    txt(f,.085,.458,'当前状态 + 当前时间',18)
    txt(f,.418,.458,'同一个参数集合',18)
    txt(f,.742,.458,'d 维瞬时速度',18)
    txt(f,.075,.345,r'$u_t^\theta(x)=\mathrm{NN}_\theta(x,t)\in\mathbb{R}^d$',28)
    txt(f,.075,.25,r'$\dot X_t=u_t^\theta(X_t)\quad\longrightarrow\quad X_t=\psi_t^\theta(x_0)$',28,BLUE)
    txt(f,.075,.16,'这里 θ 表示全部网络参数；与线性例子中单个收缩系数的角色不同。',17,GRAY)
    footer(f,'网络直接输出速度；流映射需要把这些速度沿轨迹积分后才得到。')
    return f


def board14():
    f=base(14,'确定性的 ODE 为什么能产生随机样本','Flow models · Random initialization and endpoint distribution','抽样之前初值是随机变量；抽到一个具体初值后，这一次运动就确定了。')
    rng=np.random.default_rng(21)
    initial=rng.normal(size=45)
    ax=f.add_axes([.08,.355,.42,.375]);ts=np.linspace(0,1,100)
    for z in initial:
        ax.plot(ts,z*np.exp(-ts),color=BLUE,alpha=.13,lw=.9)
    for z,color in [(1.5,BLUE),(-1.0,ORANGE)]:
        ax.plot(ts,z*np.exp(-ts),color=color,lw=2.5)
        ax.scatter([0,1],[z,z/math.e],s=40,color=color,zorder=5)
    ax.set(xlim=(0,1),ylim=(-2.7,2.7),xticks=[0,.5,1],yticks=[-2,0,2]);style(ax,r'$t$',r'$X_t$')
    txt(f,.08,.754,'示例仍取 u(x) = −x，重复抽取不同初值',18)
    txt(f,.55,.71,r'$X_0\sim\mathcal{N}(0,I_d)$',29,BLUE)
    txt(f,.55,.62,'初始分布必须容易采样。',20)
    txt(f,.55,.524,r'$X_t=\psi_t^\theta(X_0)$',30)
    txt(f,.55,.43,'同一个模型，作用于不同随机起点。',19)
    txt(f,.55,.327,r'$X_1\sim p_{\mathrm{data}}$',29,ORANGE)
    txt(f,.55,.251,'这是希望学到的终点分布目标。',19)
    txt(f,.08,.174,'左图只演示随机初值的机制：线性收缩仍得到高斯，不代表已经学会真实数据。',17,GRAY)
    footer(f,'多样性来自初始抽样；生成过程中不需要每一步重新加入随机数。')
    return f


def board15():
    f=base(15,'一次采样把前面的步骤真正连起来','Algorithm 1 · Sampling from a Flow Model with Euler method','输入训练好的速度场和步数 n，先抽一次初值，再连续更新状态。')
    rows=[('1',r'$t=0,\qquad h=1/n$','设定时间与步长'),
          ('2',r'$\widehat X_0\sim p_{\mathrm{init}}$','抽取一次随机初值'),
          ('3',r'$v_k=u_{t_k}^{\theta}(\widehat X_k)$','在当前状态查询速度'),
          ('4',r'$\widehat X_{k+1}=\widehat X_k+h v_k$','速度乘步长，更新状态'),
          ('5',r'$t_{k+1}=t_k+h$','时间前进，共执行 n 次更新'),
          ('6',r'$\mathrm{return}\ \widehat X_n$','返回 t = 1 时的近似样本')]
    for i,(n,expr,label) in enumerate(rows):
        y=.729-i*.096
        txt(f,.075,y,n,22,GRAY)
        txt(f,.125,y,expr,26,BLUE if i in [2,3] else INK)
        txt(f,.64,y,label,19)
    txt(f,.075,.155,r'仍取 $u=-x,\ n=4,\ x_0=2$：$2\to1.5\to1.125\to0.84375\to0.6328125$',21)
    footer(f,'生成时网络参数 θ 保持固定；如何训练这个速度场，是后续需要解决的问题。',18)
    return f


def render():
    from flow_walkthrough_numerics import board09,board10,board11,board12
    builders=[board01,board02,board03,board04,board05,board06,board07,board08,
              board09,board10,board11,board12,board13,board14,board15]
    path=DEST/'flow-models-walkthrough.pdf'
    with PdfPages(path,metadata={'Title':'Flow Models 2.1 逐步白板笔记','Subject':'Definitions, Theorem 3, Example 4, Simulating an ODE, Flow models, Algorithm 1'}) as pdf:
        for n,builder in enumerate(builders,1):
            fig=builder()
            fig.savefig(DEST/f'board-{n:02d}.png',dpi=180)
            fig.savefig(DEST/f'board-{n:02d}.svg')
            pdf.savefig(fig)
            plt.close(fig)
            print(f'board-{n:02d} saved',flush=True)
    final=ROOT.parent/'output/pdf';final.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,final/path.name)
    with zipfile.ZipFile(DEST/'flow-models-walkthrough.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DEST.glob('board-*')):z.write(p,p.name)
        z.write(path,path.name)
        for name in ['render_flow_walkthrough.py','flow_walkthrough_common.py','flow_walkthrough_numerics.py']:
            z.write(Path(__file__).parent/name,name)
    info={'source':'lecture_notes.pdf, section 2.1, PDF pages 7-9','boards':15,'image_pixels':[2520,1620],
          'exact_at_1':2/math.e,'euler':{},'heun':{}}
    for n in [4,8,16]:
        h=1/n
        info['euler'][n]=2*(1-h)**n
        info['heun'][n]=2*(1-h+h*h/2)**n
    (DEST/'figure-data.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':render()
