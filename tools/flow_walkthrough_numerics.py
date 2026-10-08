"""Boards 09--12: numerical simulation in the order of section 2.1."""
from flow_walkthrough_common import *

SECTION = 'Simulating an ODE · 数值求解'


def board09():
    fig = base(9, 'Euler：用起点速度，近似这一小段位移', SECTION,
               r'例子固定为 $\dot X=-X$，$X_0=2$。先只走一步：$h=0.25$。')
    ax = fig.add_axes([.09, .335, .365, .355])
    ts = np.linspace(0, .25, 200)
    velocity = -2 * np.exp(-ts)
    ax.fill_between(ts, -2, 0, color=ORANGE, alpha=.16)
    ax.fill_between(ts, velocity, 0, facecolor='none', edgecolor=BLUE,
                    hatch='///', linewidth=0, alpha=.7)
    ax.plot(ts, velocity, color=BLUE, lw=3)
    ax.hlines(-2, 0, .25, color=ORANGE, lw=2.5)
    ax.axhline(0, color=GRAY, lw=1)
    ax.scatter([0, .25], [-2, velocity[-1]], color=[ORANGE, BLUE], s=65, zorder=5)
    ax.set(xlim=(-.012, .265), ylim=(-2.32, .20), xticks=[0, .125, .25],
           yticks=[-2, -1, 0])
    style(ax, '时间 s', '速度')
    ax.yaxis.set_label_coords(-.065, 1.05)
    ax.text(.013, -.58, '阴影在横轴下方\n积分是负位移', fontsize=18, color=INK)
    ax.annotate(r'$u_s(X_s)=-2e^{-s}$', (.18, -2*np.exp(-.18)),
                xytext=(.12, -1.20), fontsize=21, color=BLUE,
                arrowprops=dict(arrowstyle='->', color=BLUE))
    txt(fig, .09, .75, '沿真实轨迹，速度会逐渐改变', 20)
    txt(fig, .54, .745, '精确：把沿途速度积分起来', 20, BLUE)
    txt(fig, .54, .687, r'$X_h=X_0+\int_0^h u_s(X_s)\,\mathrm{d}s$', 26)
    txt(fig, .54, .622, r'$=2+(2e^{-0.25}-2)\approx 1.557602$', 23)
    txt(fig, .54, .535, '近似：这一小段始终使用起点速度', 20, ORANGE)
    txt(fig, .54, .478, r'$\widehat X_1=X_0+h\,u_0(X_0)$', 26)
    txt(fig, .54, .414, r'$=2+0.25\times(-2)=1.5$', 24)
    txt(fig, .54, .341, '矩形积分为 −0.5，下降得偏多。', 19, GRAY)
    txt(fig, .09, .235, '精确积分 ≈ −0.442398；Euler 矩形近似 = −0.5。', 20)
    txt(fig, .09, .175, '这里的面积带符号；“速度 × 时间”给出位移，不是终点位置。', 20)
    footer(fig, 'Euler 的想法：先算近似位移，再把它加到当前状态上。')
    return fig


def _table(ax, values, labels, widths, fontsize=19):
    ax.axis('off')
    table = ax.table(cellText=values, colLabels=labels, colWidths=widths,
                     cellLoc='center', colLoc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(LIGHT)
        cell.set_linewidth(.8)
        cell.set_facecolor('#f0f4f8' if r == 0 else 'white')
        cell.get_text().set_color(INK)
        if r == 0:
            cell.get_text().set_fontsize(fontsize-1)
    return table


def board10():
    fig = base(10, 'Euler：把第一步重复四次', SECTION,
               '每次都用“当前状态”重新算速度。横轴是时间，纵轴是状态。')
    values = []
    states = [2.0]
    for k in range(4):
        x = states[-1]
        nxt = x - .25*x
        values.append([str(k), f'{k*.25:g}', f'{x:g}', f'{-x:g}',
                       f'{-.25*x:.8f}'.rstrip('0').rstrip('.'),
                       f'{nxt:.7f}'.rstrip('0').rstrip('.')])
        states.append(nxt)
    txt(fig, .055, .752, r'$h=0.25,\quad t_k=kh,\quad\widehat X_{k+1}=\widehat X_k+h(-\widehat X_k)$', 24)
    table_ax = fig.add_axes([.05, .46, .9, .245])
    _table(table_ax, values,
           ['步数 k', r'时间 $t_k$', '当前状态', '当前速度', '这步位移', '下一状态'],
           [.09, .11, .18, .18, .20, .24], fontsize=18)
    ax = fig.add_axes([.095, .205, .45, .18])
    t = np.linspace(0, 1, 200)
    ax.plot(t, 2*np.exp(-t), color=BLUE, lw=2.5, label='精确解')
    ax.plot(np.arange(5)*.25, states, '-o', color=ORANGE, lw=2, ms=6,
            label='Euler 近似')
    ax.set(xlim=(-.02, 1.03), ylim=(.45, 2.12), xticks=[0, .25, .5, .75, 1],
           yticks=[.5, 1, 1.5, 2])
    style(ax, '时间 t', '状态 X')
    ax.yaxis.set_label_coords(-.055, 1.07)
    ax.legend(frameon=False, fontsize=15, loc='upper right')
    txt(fig, .60, .355, '四步后，到达 t = 1：', 20)
    txt(fig, .60, .290, r'$\widehat X_4=2(1-0.25)^4=0.6328125$', 22, ORANGE)
    txt(fig, .60, .225, r'$X_1=2e^{-1}\approx 0.735759$', 23, BLUE)
    txt(fig, .60, .165, '带帽的是数值状态；下标 k 是步数。', 18, GRAY)
    footer(fig, '状态从 2 变成 1.5 后，下一步的速度也要从 −2 改成 −1.5。')
    return fig


def board11():
    fig = base(11, 'Heun：先预测，再用平均速度修正', SECTION,
               r'仍从 $X_0=2$ 出发，$h=0.25$。修正时仍然从原来的状态 2 开始算。')
    ax = fig.add_axes([.08, .43, .37, .26])
    ts = np.linspace(0, .25, 200)
    ax.plot(ts, 2*np.exp(-ts), color=GRAY, lw=2, alpha=.7)
    ax.plot([0, .25], [2, 1.5], '--', color=ORANGE, lw=2)
    ax.plot([0, .25], [2, 1.5625], color=BLUE, lw=2)
    ax.axvline(.25, color=LIGHT, lw=1.5)
    ax.scatter([0], [2], c=INK, s=55, zorder=5)
    ax.scatter([.25], [1.5], facecolors='white', edgecolors=ORANGE, s=80, lw=2, zorder=6)
    ax.scatter([.25], [1.5625], c=BLUE, s=60, zorder=6)
    ax.annotate('', xy=(.25, 1.553), xytext=(.25, 1.509),
                arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    ax.annotate('修正值 1.5625', (.25, 1.5625), xytext=(.12, 1.79),
                fontsize=17, color=BLUE, arrowprops=dict(arrowstyle='-', color=BLUE))
    ax.annotate('预测值 1.5', (.25, 1.5), xytext=(.12, 1.39),
                fontsize=17, color=ORANGE, arrowprops=dict(arrowstyle='-', color=ORANGE))
    ax.text(.002, 1.39, '灰线：精确解', fontsize=14, color=GRAY)
    ax.set(xlim=(-.015, .30), ylim=(1.32, 2.10), xticks=[0, .125, .25], yticks=[1.5, 2])
    style(ax, '时间 t', '状态 X')
    ax.yaxis.set_label_coords(-.055, 1.06)
    txt(fig, .08, .755, '两个终点都对应同一个新时间', 20)
    txt(fig, .52, .752, '① 起点速度 → 预测终点', 20, ORANGE)
    txt(fig, .52, .696, r'$k_1=-2,\quad\widetilde X_1=2+0.25(-2)=1.5$', 22)
    txt(fig, .52, .623, '② 新时间 + 预测位置 → 第二次速度', 20)
    txt(fig, .52, .574, r'$k_2=u_{0.25}(1.5)=-1.5$', 22)
    txt(fig, .52, .522, r'$\bar k=(k_1+k_2)/2=(-2-1.5)/2=-1.75$', 20)
    txt(fig, .52, .465, '③ 从原状态，用平均速度重新走一步', 20, BLUE)
    txt(fig, .52, .410, r'$\widehat X_1=2+0.25(-1.75)=1.5625$', 23, BLUE)
    txt(fig, .08, .326, '一般形式：', 19)
    txt(fig, .24, .326, r'$k_1=u_{t_k}(\widehat X_k),\qquad\widetilde X_{k+1}=\widehat X_k+h k_1$', 24)
    txt(fig, .24, .260, r'$k_2=u_{t_k+h}(\widetilde X_{k+1})$', 24)
    txt(fig, .24, .192, r'$\widehat X_{k+1}=\widehat X_k+\frac{h}{2}(k_1+k_2)$', 26, BLUE)
    footer(fig, '图中竖直小箭头表示数值修正，并不表示真实轨迹在这一瞬间跳动。', size=18)
    return fig


def board12():
    fig = base(12, '步长减半，会改变多少误差？', SECTION,
               '补充理解：比较同一条 ODE 的两种数值近似；仍属于数值求解这一段。')
    exact = 2*np.exp(-1)
    ns = np.array([4, 8, 16])
    hs = 1/ns
    euler = 2*(1-hs)**ns
    heun = 2*(1-hs+hs**2/2)**ns
    err_e = np.abs(euler-exact)
    err_h = np.abs(heun-exact)
    txt(fig, .055, .753, r'$\dot X=-X,\quad X_0=2,\quad X_1=2e^{-1}\approx0.735759$', 24)
    values = [[str(n), f'{h:g}', f'{xe:.7f}', f'{ee:.7f}', f'{xh:.7f}', f'{eh:.7f}']
              for n, h, xe, ee, xh, eh in zip(ns, hs, euler, err_e, heun, err_h)]
    table_ax = fig.add_axes([.05, .495, .9, .21])
    _table(table_ax, values,
           ['步数 n', '步长 h', 'Euler 终值', '绝对误差', 'Heun 终值', '绝对误差'],
           [.10, .12, .20, .19, .20, .19], fontsize=18)
    ax = fig.add_axes([.105, .205, .355, .215])
    ax.semilogy(ns, err_e, '-o', color=ORANGE, lw=2, label='Euler')
    ax.semilogy(ns, err_h, '-o', color=BLUE, lw=2, label='Heun')
    ax.set(xticks=ns, xlim=(3, 17), ylim=(.00035, .17), yticks=[.001, .01, .1])
    ax.set_yticklabels(['0.001', '0.01', '0.1'])
    ax.grid(axis='y', color=LIGHT, lw=.8)
    style(ax, '步数 n', '绝对误差')
    ax.yaxis.label.set_fontsize(16)
    ax.yaxis.label.set_rotation(90)
    ax.yaxis.set_label_coords(-.155, .5)
    ax.legend(frameon=True, facecolor='white', edgecolor='white', framealpha=.95,
              fontsize=16, loc='upper right')
    txt(fig, .105, .458, '纵轴取对数；点越低，误差越小。', 16, GRAY)
    txt(fig, .54, .432, '固定区间的全局误差（需光滑与稳定性条件）：', 17)
    txt(fig, .54, .371, r'$\mathrm{Euler}:\ O(h)\qquad\mathrm{Heun}:\ O(h^2)$', 25)
    txt(fig, .54, .308, '步长减半：误差渐近约降至 1/2、1/4。', 19)
    txt(fig, .54, .240, '计算成本：每步分别查询速度场 1 次、2 次。', 18)
    txt(fig, .54, .176, '同为 n 步时，Heun 用了约两倍查询次数。', 18, GRAY)
    footer(fig, '增加步数让数值轨迹更接近精确解；比较精度时，也要记住计算成本。', size=18)
    return fig
