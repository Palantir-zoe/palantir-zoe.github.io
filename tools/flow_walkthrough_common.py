"""Shared rendering primitives for the section 2.1 reading companion."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/assets/images/flow-models-walkthrough'
DEST.mkdir(parents=True, exist_ok=True)
font_path = Path('C:/Windows/Fonts/msyh.ttc')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    FONT = fm.FontProperties(fname=str(font_path)).get_name()
else:
    FONT = 'Noto Sans CJK SC'
plt.rcParams.update({'font.family':FONT,'font.size':18,'mathtext.fontset':'stix',
 'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False,
 'axes.labelsize':18,'xtick.labelsize':14,'ytick.labelsize':14,
 'pdf.fonttype':42,'svg.fonttype':'path','savefig.facecolor':'white'})
INK='#20252c'; BLUE='#285f9b'; ORANGE='#ad5626'; GRAY='#697580'; LIGHT='#dbe2e8'

def txt(fig,x,y,s,size=20,color=INK,**kw):
    return fig.text(x,y,s,fontsize=size,color=color,va='center',**kw)

def base(n,title,section,subtitle):
    fig=plt.figure(figsize=(14,9),facecolor='white')
    txt(fig,.05,.955,section,13,GRAY)
    txt(fig,.05,.895,f'{n:02d}  {title}',28,weight='bold')
    txt(fig,.05,.837,subtitle,17,GRAY)
    fig.add_artist(Line2D([.05,.95],[.803,.803],color=LIGHT,lw=1))
    txt(fig,.05,.028,'2.1 FLOW MODELS  ·  按原文顺序逐步理解',12,GRAY)
    txt(fig,.95,.028,f'{n} / 15',12,GRAY,ha='right')
    return fig

def style(ax,xlabel,ylabel):
    ax.set_xlabel(xlabel,labelpad=9);ax.set_ylabel(ylabel,rotation=0,labelpad=16)
    ax.tick_params(colors=GRAY,length=3)
    for spine in ax.spines.values():spine.set_color('#abb4bd')

def arrow(fig,start,end,color=GRAY,lw=2):
    p=FancyArrowPatch(start,end,transform=fig.transFigure,arrowstyle='->',mutation_scale=18,color=color,lw=lw)
    fig.add_artist(p)
    return p

def box(fig,x,y,w,h,label,color=BLUE,size=21):
    rect=Rectangle((x,y),w,h,transform=fig.transFigure,fill=False,edgecolor=color,lw=1.5)
    fig.add_artist(rect)
    txt(fig,x+w/2,y+h/2,label,size,color,ha='center')
    return rect

def footer(fig,s,size=19):
    txt(fig,.05,.091,s,size)
