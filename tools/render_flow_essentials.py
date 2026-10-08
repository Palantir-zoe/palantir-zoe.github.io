"""Four concise scientific whiteboards for lecture notes section 2.1.

Requires numpy, matplotlib and a Chinese font. Produces PNG/SVG/PDF/ZIP.
"""
from pathlib import Path
import math
import shutil
import zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/assets/images/flow-models-essentials'
DEST.mkdir(parents=True,exist_ok=True)
font_path=Path('C:/Windows/Fonts/msyh.ttc')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    font_name=fm.FontProperties(fname=str(font_path)).get_name()
else:font_name='Noto Sans CJK SC'
plt.rcParams.update({'font.family':font_name,'font.size':18,'mathtext.fontset':'stix',
 'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False,
 'axes.labelsize':18,'xtick.labelsize':13,'ytick.labelsize':13,
 'pdf.fonttype':42,'svg.fonttype':'path','savefig.facecolor':'white'})
INK='#20252c';BLUE='#285f9b';ORANGE='#ad5626';GRAY='#697580';LIGHT='#dbe2e8'

def txt(f,x,y,s,size=21,color=INK,**kw):
    return f.text(x,y,s,fontsize=size,color=color,va='center',**kw)

def base(n,title,section):
    f=plt.figure(figsize=(14,9),facecolor='white')
    txt(f,.05,.945,section,14,GRAY)
    txt(f,.05,.875,f'{n:02d}  {title}',29,weight='bold')
    f.add_artist(Line2D([.05,.95],[.816,.816],color=LIGHT,lw=1))
    txt(f,.05,.03,'2.1 FLOW MODELS  ·  核心定义与推导',12,GRAY)
    txt(f,.95,.03,f'{n} / 4',12,GRAY,ha='right')
    return f

def style(ax,xlabel,ylabel):
    ax.set_xlabel(xlabel,labelpad=8);ax.set_ylabel(ylabel,rotation=0,labelpad=13)
    ax.tick_params(colors=GRAY,length=3)
    for sp in ax.spines.values():sp.set_color('#abb4bd')

def arrow(f,a,b):
    f.add_artist(FancyArrowPatch(a,b,transform=f.transFigure,arrowstyle='->',mutation_scale=19,color=GRAY,lw=1.8))

def board1():
    f=base(1,'从速度场到流映射','Trajectory · Vector field · ODE · Flow · Theorem 3')
    ax=f.add_axes([.08,.35,.35,.41])
    q=np.linspace(-1.65,1.65,7);xx,yy=np.meshgrid(q,q)
    ax.quiver(xx,yy,-xx,-yy,color='#adb7c1',angles='xy',scale_units='xy',scale=6,width=.004)
    start=np.array([1.5,1.0]);end=np.exp(-.65)*start
    ax.plot([start[0],end[0]],[start[1],end[1]],color=BLUE,lw=3)
    ax.scatter(*start,color=BLUE,s=45,zorder=5)
    ax.scatter(*end,color=ORANGE,s=50,zorder=5)
    ax.annotate('',end-.35*end,end,arrowprops=dict(arrowstyle='->',color=ORANGE,lw=2.5))
    ax.annotate(r'$x_0$',start,xytext=(5,9),textcoords='offset points',fontsize=22,color=BLUE)
    ax.annotate(r'$X_t$',end,xytext=(6,7),textcoords='offset points',fontsize=22,color=ORANGE)
    ax.annotate(r'$u_t(X_t)$',end-.35*end,xytext=(-72,-22),textcoords='offset points',fontsize=21,color=ORANGE)
    ax.set(xlim=(-1.9,1.9),ylim=(-1.9,1.9),aspect='equal',xticks=[-1,0,1],yticks=[-1,0,1])
    style(ax,r'$x_1$',r'$x_2$')
    txt(f,.08,.257,r'示意场 $u(x)=-x$：箭头给速度，线段给轨迹。',16,GRAY)
    txt(f,.51,.737,r'轨迹：$X:[0,1]\to\mathbb{R}^d,\quad t\mapsto X_t$',23)
    txt(f,.51,.641,r'向量场：$(x,t)\mapsto u_t(x)\in\mathbb{R}^d$',23)
    txt(f,.51,.533,r'$\dot X_t=u_t(X_t),\qquad X_0=x_0$',29,BLUE)
    txt(f,.51,.437,r'流映射：$X_t=\psi_t(x_0)$',27)
    txt(f,.51,.34,'速度场规定局部运动，流记录累计结果。',18)
    txt(f,.08,.209,r'$\partial_t\psi_t(x_0)=u_t(\psi_t(x_0)),\qquad\psi_0(x_0)=x_0$',27,BLUE)
    txt(f,.08,.12,'Theorem 3：u 连续可微且导数有界时，流存在且唯一；',18)
    txt(f,.08,.076,r'每个 $\psi_t$ 都是微分同胚，即映射及其逆均连续可微。',18)
    return f

def board2():
    f=base(2,'线性速度场的解析解','Example 4 · Linear Vector Fields')
    txt(f,.075,.742,r'$u_t(x)=-\theta x,\quad\theta>0,\qquad\dot X_t=-\theta X_t$',29)
    txt(f,.075,.631,r'$\frac{\mathrm{d}}{\mathrm{d}t}(e^{\theta t}X_t)=e^{\theta t}(\theta X_t+\dot X_t)=0$',29)
    txt(f,.075,.515,r'$e^{\theta t}X_t=x_0\quad\Longrightarrow\quad\psi_t(x_0)=e^{-\theta t}x_0$',31,BLUE)
    ax=f.add_axes([.09,.178,.34,.25]);ts=np.linspace(0,1,180)
    ax.plot(ts,2*np.exp(-ts),color=BLUE,lw=2.7)
    ax.scatter([0,1],[2,2/math.e],s=45,color=ORANGE)
    ax.annotate(r'$2e^{-1}\approx0.7358$',(1,2/math.e),xytext=(.57,1.38),fontsize=19,color=ORANGE,
                arrowprops=dict(arrowstyle='-',color=ORANGE,lw=.8))
    ax.set(xlim=(0,1.05),ylim=(0,2.2),xticks=[0,.5,1],yticks=[0,1,2]);style(ax,r'$t$',r'$X_t$')
    ax.set_title(r'$\theta=1,\quad x_0=2$',fontsize=20,pad=8)
    txt(f,.52,.405,'验证初值与 ODE',20)
    txt(f,.54,.329,r'$\psi_0(x_0)=e^0x_0=x_0$',26)
    txt(f,.54,.24,r'$\partial_t\psi_t(x_0)=-\theta e^{-\theta t}x_0$',25)
    txt(f,.54,.17,r'$=u_t(\psi_t(x_0))$',27,BLUE)
    txt(f,.075,.084,'速度大小随到原点的距离一起减小；有限时间内收缩比例仍大于零。',18)
    return f

def board3():
    f=base(3,'Euler 与 Heun 的更新公式','Simulating an ODE')
    txt(f,.07,.737,r'$X_{t+h}=X_t+\int_t^{t+h}u_s(X_s)\,\mathrm{d}s,\qquad h=1/n,\quad t_k=kh$',26)
    txt(f,.07,.633,'Euler：用起点速度近似积分',21,BLUE)
    txt(f,.075,.55,r'$\widehat X_{k+1}=\widehat X_k+h\,u_{t_k}(\widehat X_k)$',25,BLUE)
    ax=f.add_axes([.09,.26,.35,.205]);ts=np.linspace(0,.25,120)
    ax.plot(ts,2*np.exp(-ts),color=INK,lw=2,label='精确解')
    ax.plot([0,.25],[2,1.5],ls='--',color=BLUE,lw=1.8,label='Euler')
    ax.plot([0,.25],[2,1.5625],ls=':',color=ORANGE,lw=1.9,label='Heun')
    ax.scatter([.25,.25],[1.5,1.5625],color=[BLUE,ORANGE],s=35,zorder=5)
    ax.set(xlim=(0,.28),ylim=(1.4,2.05),xticks=[0,.25],yticks=[1.5,2]);style(ax,r'$t$',r'$X$')
    ax.legend(frameon=False,loc='upper right',fontsize=12)
    txt(f,.085,.172,r'例：$\dot X=-X,\ X_0=2,\ h=0.25$',18,GRAY)
    txt(f,.535,.633,'Heun：先预测，再平均速度',21,ORANGE)
    txt(f,.55,.551,r'$k_1=u_{t_k}(\widehat X_k)$',26)
    txt(f,.55,.463,r'$\widetilde X_{k+1}=\widehat X_k+h k_1$',26)
    txt(f,.55,.375,r'$k_2=u_{t_k+h}(\widetilde X_{k+1})$',26)
    txt(f,.55,.27,r'$\widehat X_{k+1}=\widehat X_k+\frac{h}{2}(k_1+k_2)$',28,ORANGE)
    txt(f,.535,.172,'第二次速度在新时间、预测位置计算。',17,GRAY)
    txt(f,.07,.087,'带帽状态表示数值近似。Euler 每步查询一次速度，Heun 每步两次。',18)
    return f

def board4():
    f=base(4,'神经速度场与生成采样','Flow models · Algorithm 1')
    txt(f,.075,.743,r'$u_t^\theta(x)=\mathrm{NN}_\theta(x,t)\in\mathbb{R}^d$',30,BLUE)
    items=[(.07,.255,r'$X_0\sim p_{\mathrm{init}}$',25),(.40,.22,r'$\dot X_t=u_t^\theta(X_t)$',26),(.765,.19,r'$X_1$',29)]
    for x,w,label,size in items:
        f.add_artist(Rectangle((x,.558),w,.115,transform=f.transFigure,fill=False,ec=BLUE,lw=1.4))
        txt(f,x+w/2,.615,label,size,BLUE,ha='center')
    arrow(f,(.337,.615),(.386,.615));arrow(f,(.634,.615),(.752,.615))
    txt(f,.075,.482,r'常用初始分布：$p_{\mathrm{init}}=\mathcal{N}(0,I_d)$',22)
    txt(f,.075,.385,'Algorithm 1 · Euler 采样',21)
    code=['x = sample(p_init)','h = 1 / n','for k in range(n):','    x = x + h * model(x, k*h)','return x']
    for j,line in enumerate(code):txt(f,.09,.313-.044*j,line,16,family='Consolas')
    txt(f,.58,.391,'目标：终点分布接近数据分布',19)
    txt(f,.59,.308,r'$X_1=\psi_1^\theta(X_0)$',27)
    txt(f,.59,.231,r'$p_1^\theta\approx p_{\mathrm{data}}$',29,ORANGE)
    txt(f,.58,.155,'生成时参数固定，随机性来自初值。',17,GRAY)
    txt(f,.075,.083,r'网络参数化速度场 $u^\theta$；流映射 $\psi^\theta$ 由求解 ODE 得到。',20)
    return f

def main():
    pdf=DEST/'flow-models-essentials.pdf'
    with PdfPages(pdf,metadata={'Title':'2.1 Flow Models 核心白板推导'}) as out:
        for i,builder in enumerate([board1,board2,board3,board4],1):
            f=builder()
            f.savefig(DEST/f'board-{i:02d}.png',dpi=180)
            f.savefig(DEST/f'board-{i:02d}.svg')
            out.savefig(f);plt.close(f)
            print(f'board-{i:02d} saved',flush=True)
    final=ROOT.parent/'output/pdf';final.mkdir(parents=True,exist_ok=True)
    shutil.copy2(pdf,final/pdf.name)
    with zipfile.ZipFile(DEST/'flow-models-essentials.zip','w',zipfile.ZIP_DEFLATED) as out:
        for p in sorted(DEST.glob('board-*')):out.write(p,p.name)
        out.write(pdf,pdf.name)
        out.write(Path(__file__),Path(__file__).name)

if __name__=='__main__':main()
