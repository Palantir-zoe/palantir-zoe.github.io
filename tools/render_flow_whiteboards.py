"""Reproduce five mathematical Flow Model whiteboards (PNG, SVG, multipage PDF).

Requires Python, numpy, matplotlib, and Microsoft YaHei (Windows) or a CJK font.
Run from any directory; all plotted coordinates are computed from the equations.
"""
from pathlib import Path
import json
import math
import shutil
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/assets/images/flow-models'
DEST.mkdir(parents=True, exist_ok=True)
font_path = Path('C:/Windows/Fonts/msyh.ttc')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    font_name = fm.FontProperties(fname=str(font_path)).get_name()
else:
    font_name = 'Noto Sans CJK SC'
plt.rcParams.update({
    'font.family': font_name, 'font.size': 17,
    'mathtext.fontset': 'stix', 'axes.unicode_minus': False,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.labelsize': 19, 'xtick.labelsize': 14, 'ytick.labelsize': 14,
    'pdf.fonttype': 42, 'svg.fonttype': 'path',
    'savefig.facecolor': 'white',
})
INK = '#20252c'
BLUE = '#275f9c'
ORANGE = '#b45d25'
GRAY = '#6c7680'
LIGHT = '#dde2e7'


def txt(fig, x, y, text, size=19, color=INK, **kwargs):
    return fig.text(x, y, text, fontsize=size, color=color,
                    va='center', **kwargs)


def base(number, title, subtitle):
    fig = plt.figure(figsize=(14, 9), facecolor='white')
    txt(fig, .05, .935, f'{number:02d}  {title}', 29, weight='bold')
    txt(fig, .05, .878, subtitle, 17, GRAY)
    fig.add_artist(Line2D([.05, .95], [.84, .84], color=LIGHT, lw=1))
    txt(fig, .05, .032, 'FLOW MODELS  ·  2.1  ·  白板推导', 12, GRAY)
    txt(fig, .95, .032, f'{number} / 5', 12, GRAY, ha='right')
    return fig


def ax_style(ax, xlabel, ylabel):
    ax.set_xlabel(xlabel, labelpad=8)
    ax.set_ylabel(ylabel, rotation=0, labelpad=15)
    ax.tick_params(colors=GRAY, length=3)
    for spine in ax.spines.values():
        spine.set_color('#adb5bd')


def board1():
    fig = base(1, '速度场怎样产生一条轨迹', '每个位置有一个速度；沿当前位置的速度连续运动，得到 ODE 的解。')
    ax = fig.add_axes([.08, .25, .41, .51])
    grid = np.linspace(-1.65, 1.65, 9)
    xx, yy = np.meshgrid(grid, grid)
    ax.quiver(xx, yy, -yy, xx, color='#bbc3cb', angles='xy',
              scale_units='xy', scale=6, width=.004)
    angle = np.linspace(0, 2*np.pi, 300)
    radius = 1.4
    ax.plot(radius*np.cos(angle), radius*np.sin(angle), color=LIGHT, lw=1.2, ls='--')
    ts = np.linspace(0, 1, 101)
    points = radius*np.array([np.cos(ts), np.sin(ts)])
    ax.plot(*points, color=BLUE, lw=3)
    ax.scatter([radius], [0], color=INK, s=45, zorder=5)
    ax.annotate(r'$x_0$', (radius, 0), xytext=(9, -20), textcoords='offset points', fontsize=22)
    tm = .53
    current = radius*np.array([np.cos(tm), np.sin(tm)])
    velocity = np.array([-current[1], current[0]])
    ax.scatter(*current, color=ORANGE, s=55, zorder=5)
    tip = current + .37*velocity
    ax.annotate('', tip, current, arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.5))
    ax.annotate(r'$u_t(X_t)$', tip, xytext=(-80, 40), textcoords='offset points', color=ORANGE, fontsize=21)
    ax.annotate(r'$X_t$', current, xytext=(10, -12), textcoords='offset points', color=ORANGE, fontsize=22)
    ax.scatter(*points[:, -1], color=BLUE, s=45)
    ax.annotate(r'$X_1$', points[:, -1], xytext=(-40, -12), textcoords='offset points', color=BLUE, fontsize=21)
    ax.set(xlim=(-1.9, 1.9), ylim=(-1.8, 1.95), aspect='equal')
    ax.set_xticks([-1, 0, 1]); ax.set_yticks([-1, 0, 1])
    ax_style(ax, r'$x_1$', r'$x_2$')
    txt(fig, .08, .785, '例：二维旋转场（角速度为 1）', 18)
    txt(fig, .08, .15, '灰箭头：局部速度    蓝曲线：实际轨迹', 16, GRAY)
    txt(fig, .55, .77, '① 局部规则：当前位置决定当前速度', 18)
    txt(fig, .57, .704, r'$u_t(x)=(-x_2,\,x_1)$', 26, BLUE)
    txt(fig, .55, .614, '② 连续运动：速度沿轨迹不断更新', 18)
    txt(fig, .57, .546, r'$\dot X_t=u_t(X_t),\qquad X_0=x_0$', 25)
    txt(fig, .57, .454, r'$X_t=x_0+\int_0^t u_s(X_s)\,\mathrm{d}s$', 25)
    txt(fig, .55, .36, '③ 流映射：记录每个起点的运动结果', 18)
    txt(fig, .57, .29, r'$X_t=\psi_t(x_0)=R(t)x_0$', 25, BLUE)
    txt(fig, .57, .223, r'$R(t)$ 为逆时针旋转 $t$ 弧度的矩阵', 17, GRAY)
    txt(fig, .05, .105, '一个点得到一条轨迹；让所有初始点一起运动，就得到一族流映射。', 20)
    return fig


def board2():
    fig = base(2, '收缩可以可逆，有限时间不会合并', '用一个可解析求解的例子，同时看清轨迹、流映射与逆映射。')
    ax = fig.add_axes([.085, .40, .405, .36])
    t = np.linspace(0, 1, 150)
    for x0 in [-2, -1, -.5, .5, 1, 2]:
        color = BLUE if x0 > 0 else ORANGE
        ax.plot(t, x0*np.exp(-t), color=color, lw=2, alpha=.55 if abs(x0)<2 else 1)
        ax.scatter([0, 1], [x0, x0/math.e], color=color, s=25)
    ax.axhline(0, color=LIGHT, lw=1)
    ax.set(xlim=(0, 1.05), ylim=(-2.2, 2.2), xticks=[0, .5, 1], yticks=[-2,-1,0,1,2])
    ax_style(ax, r'$t$', r'$X_t$')
    txt(fig, .085, .786, r'$\dot X_t=-X_t$：不同初值的精确轨迹', 18)
    txt(fig, .085, .29, '同一时刻，不同起点仍对应不同位置。', 18, BLUE)
    txt(fig, .085, .225, r'$e^{-t}>0\quad\mathrm{for\ finite}\ t$', 26)
    txt(fig, .085, .158, '趋近原点不等于在有限时间到达原点。', 17, GRAY)
    txt(fig, .55, .77, '① 乘上积分因子', 18)
    txt(fig, .57, .698, r'$\frac{\mathrm{d}}{\mathrm{d}t}(e^tX_t)=e^t(X_t+\dot X_t)=0$', 23)
    txt(fig, .55, .605, '② 利用初始条件', 18)
    txt(fig, .57, .535, r'$e^tX_t=x_0\quad\Rightarrow\quad\psi_t(x_0)=e^{-t}x_0$', 23, BLUE)
    txt(fig, .55, .443, '③ 反向恢复初值', 18)
    txt(fig, .57, .377, r'$\psi_t^{-1}(x)=e^t x$', 27, BLUE)
    txt(fig, .55, .283, '一般情形需要适当的正则性条件：', 17)
    txt(fig, .57, .223, r'$\|u_t(x)-u_t(y)\|\leq L\|x-y\|$', 23)
    txt(fig, .55, .16, '连续性与统一全局 Lipschitz 条件保证唯一解。', 15.5, GRAY)
    txt(fig, .05, .092, '进一步满足空间连续可微等条件时，流及其逆连续可微，即微分同胚。', 18)
    return fig


def board3():
    fig = base(3, '点被压缩，概率密度为何升高', '一维高斯示例：相同概率质量进入更短的区间；阴影面积保持不变。')
    ax = fig.add_axes([.085, .34, .41, .40])
    x = np.linspace(-3.2, 3.2, 900)
    normal = lambda z: np.exp(-z*z/2)/np.sqrt(2*np.pi)
    for t, color in [(0, BLUE), (1, ORANGE)]:
        sigma = np.exp(-t)
        p = normal(x/sigma)/sigma
        ax.plot(x, p, color=color, lw=2.7, label=f'$t={t}$')
        mask = np.abs(x) <= sigma
        ax.fill_between(x, 0, p, where=mask, color=color, alpha=.14)
        for edge in [-sigma, sigma]:
            ax.plot([edge, edge], [0, normal(1)/sigma], color=color, ls=':', lw=1.4)
    ax.set(xlim=(-3.1,3.1), ylim=(0,1.2), xticks=[-2,-1,0,1,2], yticks=[0,.4,.8,1.2])
    ax_style(ax, r'$x$', r'$p_t(x)$')
    ax.legend(frameon=False, loc='upper left', fontsize=19)
    txt(fig, .085, .78, r'$X_0\sim\mathcal{N}(0,1),\qquad X_t=e^{-t}X_0$', 22)
    txt(fig, .085, .245, r'$[-1,1]\ \longmapsto\ [-e^{-1},e^{-1}]$', 24)
    txt(fig, .085, .174, '两块阴影各含约 68.27% 的概率质量。', 17, GRAY)
    txt(fig, .55, .77, '① 局部长度被压缩', 18)
    txt(fig, .57, .704, r'$x=e^{-t}z,\qquad\mathrm{d}x=e^{-t}\mathrm{d}z$', 24)
    txt(fig, .55, .61, '② 概率质量守恒', 18)
    txt(fig, .57, .543, r'$p_t(x)\,\mathrm{d}x=p_0(z)\,\mathrm{d}z$', 25)
    txt(fig, .55, .45, '③ 除以变换后的体积，得到新密度', 18)
    txt(fig, .57, .384, r'$p_t(x)=e^t p_0(e^t x)$', 27, ORANGE)
    txt(fig, .57, .296, r'$X_t\sim\mathcal{N}(0,e^{-2t})$', 25)
    txt(fig, .55, .209, '一般的 d 维流：Jacobian 决定体积变化', 17)
    txt(fig, .56, .147, r'$p_t(\psi_t(z))\,|\det D\psi_t(z)|=p_0(z)$', 22)
    txt(fig, .05, .084, '确定性的映射也能改变分布；随机性来自初始样本，运动过程保持概率质量。', 18)
    return fig


def board4():
    fig = base(4, 'Euler 与 Heun 怎样近似连续运动', '精确解用实线表示；数值状态加帽。Heun 的第二次速度在预测点计算。')
    ax = fig.add_axes([.085, .43, .405, .335])
    h=.25
    t=np.linspace(0,.29,200)
    ax.plot(t,2*np.exp(-t),color=INK,lw=2.2,label='精确解')
    ax.plot([0,h],[2,1.5],color=BLUE,lw=2,ls='--',label='Euler 预测')
    ax.plot([0,h],[2,1.5625],color=ORANGE,lw=2,ls=':',label='Heun 更新')
    ax.scatter([0],[2],color=INK,s=40,zorder=5)
    ax.scatter([h],[1.5],color=BLUE,s=55,zorder=5,marker='s')
    ax.scatter([h],[1.5625],color=ORANGE,s=55,zorder=6,marker='D')
    ax.plot([.20,.29],[1.5-1.5*(.20-h),1.5-1.5*(.29-h)],color=BLUE,lw=1.6)
    ax.annotate(r'$k_2=-1.5$',(.285,1.4475),xytext=(4,4),textcoords='offset points',fontsize=17,color=BLUE)
    ax.annotate('预测点 1.5000',(h,1.5),xytext=(-135,-23),textcoords='offset points',fontsize=14,color=BLUE)
    ax.annotate('修正点 1.5625',(h,1.5625),xytext=(10,18),textcoords='offset points',fontsize=14,color=ORANGE,
                arrowprops=dict(arrowstyle='-',color=ORANGE,lw=.8))
    ax.set(xlim=(-.008,.365),ylim=(1.40,2.06),xticks=[0,.125,.25],yticks=[1.5,1.75,2])
    ax_style(ax,r'$t$',r'$X$')
    ax.legend(frameon=False,loc='upper right',fontsize=13)
    txt(fig,.085,.793,r'$\dot X=-X,\quad X_0=2,\quad h=0.25$',20)
    txt(fig,.55,.785,'Euler：用起点速度走一步',18,BLUE)
    txt(fig,.565,.723,r'$\widehat X_{k+1}=\widehat X_k+h\,u_{t_k}(\widehat X_k)$',23,BLUE)
    txt(fig,.55,.643,'Heun：预测终点，再平均两次速度',18,ORANGE)
    txt(fig,.57,.585,r'$k_1=u_{t_k}(\widehat X_k)$',23)
    txt(fig,.57,.519,r'$\widetilde X_{k+1}=\widehat X_k+h k_1$',23)
    txt(fig,.57,.451,r'$k_2=u_{t_k+h}(\widetilde X_{k+1})$',23)
    txt(fig,.57,.379,r'$\widehat X_{k+1}=\widehat X_k+\frac{h}{2}(k_1+k_2)$',25,ORANGE)
    txt(fig,.085,.327,'同样走 4 步，到达 t = 1',18)
    table=fig.add_axes([.08,.15,.41,.135]);table.axis('off')
    tab=table.table(cellText=[['精确解','0.735759','—'],['Euler','0.632813','4'],['Heun','0.745058','8']],
                    colLabels=['方法','终点','速度计算次数'],loc='center',cellLoc='center',colWidths=[.27,.34,.39])
    tab.auto_set_font_size(False);tab.set_fontsize(14);tab.scale(1,1.65)
    for (row,col),cell in tab.get_celld().items():
        cell.set_edgecolor(LIGHT);cell.set_linewidth(.7)
        if row==0:cell.set_facecolor('#f4f6f8')
    txt(fig,.55,.273,'为什么 Heun 更准确？',18)
    txt(fig,.57,.216,r'$\ddot X_t=\partial_tu_t(X_t)+D_xu_t(X_t)u_t(X_t)$',21)
    txt(fig,.55,.153,'两次速度的平均补回了 Taylor 展开的二阶项。',16,GRAY)
    txt(fig,.05,.084,'足够光滑且满足稳定性条件时：Euler 全局误差 O(h)，Heun 为 O(h²)。',18)
    return fig


def board5():
    fig = base(5, '从随机初值到生成分布', '同一批高斯样本经过连续剪切；这是解析教学示例，用来观察分布怎样被运输。')
    rng=np.random.default_rng(20261008)
    z=rng.normal(size=(450,2))
    for i,t in enumerate([0,.5,1]):
        ax=fig.add_axes([.07+i*.307,.47,.25,.285])
        x=z.copy();x[:,1]+=t*np.sin(z[:,0])
        q=np.linspace(-2.7,2.7,150)
        for level in [-2,-1,0,1,2]:
            ax.plot(q,level+t*np.sin(q),color=LIGHT,lw=.7,zorder=0)
            ax.plot(np.full_like(q,level),q+t*np.sin(level),color=LIGHT,lw=.7,zorder=0)
        ax.scatter(x[:,0],x[:,1],s=7,alpha=.35,color=BLUE,edgecolors='none')
        highlighted=np.array([1.,0.])
        hx=np.array([highlighted[0],highlighted[1]+t*np.sin(highlighted[0])])
        ax.scatter(*hx,s=55,color=ORANGE,zorder=5)
        ax.annotate('',hx+[0,.55],hx,arrowprops=dict(arrowstyle='->',color=ORANGE,lw=1.8))
        ax.set(xlim=(-3,3),ylim=(-3.7,3.7),xticks=[-2,0,2],yticks=[-2,0,2])
        ax_style(ax,r'$x_1$',r'$x_2$')
        ax.set_title(f'$t={t:g}$',fontsize=23,pad=10)
    txt(fig,.07,.355,r'$\psi_t(z)=(z_1,\ z_2+t\sin z_1)$',24,BLUE)
    txt(fig,.565,.355,r'$u_t(x)=(0,\ \sin x_1)$',24,ORANGE)
    txt(fig,.07,.286,r'网格和样本同步变形；此例 $\det D\psi_t=1$，局部面积保持不变。',17,GRAY)
    txt(fig,.075,.211,r'$X_0\sim P_{\mathrm{init}}$',24)
    txt(fig,.305,.211,r'$\longrightarrow$',29,GRAY)
    txt(fig,.385,.224,r'$\dot X_t=u_t^\theta(X_t)$',25,BLUE)
    txt(fig,.394,.167,'固定参数，数值求解 ODE',16,GRAY)
    txt(fig,.695,.211,r'$\longrightarrow$',29,GRAY)
    txt(fig,.765,.211,r'$X_1=\psi_1^\theta(X_0)$',24)
    txt(fig,.07,.093,r'$P_1^\theta=(\psi_1^\theta)_{\#}P_{\mathrm{init}}\ \approx\ P_{\mathrm{data}}$',25)
    txt(fig,.635,.093,'网络输出速度；求解器累计运动。',17)
    return fig


def main():
    pdf_path=DEST/'flow-models-whiteboards.pdf'
    with PdfPages(pdf_path,metadata={'Title':'Flow Models 2.1 白板推导','Author':'学习笔记','Subject':'ODE, flow, density transport, Euler and Heun'}) as pdf:
        for number,builder in enumerate([board1,board2,board3,board4,board5],1):
            fig=builder()
            fig.savefig(DEST/f'board-{number:02d}.png',dpi=180)
            fig.savefig(DEST/f'board-{number:02d}.svg')
            pdf.savefig(fig)
            plt.close(fig)
            print(f'board-{number:02d}: PNG + SVG + PDF page',flush=True)
    export_dir=ROOT.parent/'output/pdf'
    export_dir.mkdir(parents=True,exist_ok=True)
    shutil.copy2(pdf_path,export_dir/pdf_path.name)
    with zipfile.ZipFile(DEST/'flow-models-whiteboards.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DEST.glob('board-*')):
            archive.write(path,path.name)
        archive.write(pdf_path,pdf_path.name)
        archive.write(Path(__file__),'render_flow_whiteboards.py')
    report={
        'boards':5,'image_pixels':[2520,1620],
        'example':{'ode':'x_dot=-x','x0':2,'h':.25,'steps':4,
                   'exact':2/math.e,'euler':2*(1-.25)**4,
                   'heun':2*(1-.25+.25**2/2)**4},
        'matching_shaded_probability':math.erf(1/math.sqrt(2)),
        'shear':{'map':'(z1,z2+t*sin(z1))','field':'(0,sin(x1))','det_jacobian':1,'seed':20261008},
    }
    (DEST/'figure-data.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':
    main()
