"""Build the PRML chapter 9 reading note into the existing GitHub Pages site."""
from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import json
import re
import subprocess

from blog import SITE_TITLE, rebuild_site

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tools/content/prml-ch09'
POST = json.loads((SOURCE / 'post.json').read_text(encoding='utf-8'))
DEST = ROOT / 'docs/posts/prml-mixture-models-em/index.html'
NODE = ROOT / '.runtime/qa-venv/Lib/site-packages/playwright/driver/node.exe'
MATH = re.compile(r'\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)')
PARTS = (
    '00-overview.html',
    '01-clustering-gmm.html',
    '015-worked-example.html',
    '02-latent-extensions.html',
    '03-general-em.html',
    '04-practice-discussion.html',
)

STYLE = r'''
/* This note sits inside the site's established Notion export reading layout. */
html{scroll-behavior:smooth;scroll-padding-top:1.5rem}
.authored-note{white-space:normal;line-height:1.78;font-size:1.05rem}
.authored-note>p,.authored-note>ol,.authored-note>ul,.authored-note>table,.authored-note>.table-scroll,.authored-note>.note-focus,.authored-note>.flow-cards,.authored-note>.em-lab,.authored-note>details{margin:1.15rem 0}
.authored-note p{line-height:1.83}.authored-note h2{margin-top:3.6rem;margin-bottom:1.2rem;padding:0 0 .45rem;border-bottom:1px solid #e2e7e5;scroll-margin-top:1.5rem;font-size:1.75rem}
.authored-note h3{font-size:1.2rem;margin:2.3rem 0 .8rem;line-height:1.55}.authored-note h4{font-size:1.05rem;margin:1.6rem 0 .65rem}
.authored-note ul,.authored-note ol{padding-left:1.5rem}.authored-note li{margin:.45rem 0}.authored-note li::marker{color:#4d8e77}
.authored-note .katex-display{overflow-x:auto;overflow-y:hidden;padding:.3rem .15rem .55rem;margin:1.1rem 0}.authored-note .katex-display>.katex{min-width:max-content}
.authored-note .katex{font-size:1.03em}.authored-note .katex-display>.katex>.katex-html:has(>.tag){padding-inline:2.5em}
.review-banner{border:1px solid #bad8cf;background:#f1f8f4;border-radius:.6rem;padding:.9rem 1.15rem;margin:1rem 0 1.3rem}.review-banner span{display:inline-block;background:#2e745d;color:white;border-radius:99px;font-weight:700;font-size:.78rem;padding:.13rem .7rem}.review-banner p{margin:.45rem 0 0;font-size:.87rem;color:#526b60}
.lead{font-size:1.15rem;line-height:1.9;color:#2b423b}.note-focus{border-left:4px solid #4a9a79;background:#edf6f1;border-radius:0 .35rem .35rem 0;padding:1rem 1.25rem}
.source,.source-note{font-size:.86rem;line-height:1.65;color:#69746f}.source{margin:-.6rem 0 1.25rem}.flow-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.6rem}.flow-cards div{border:1px solid #d3e1da;background:#f8fbf9;border-radius:.4rem;padding:.75rem}.flow-cards b{display:block;color:#1e6b55}.flow-cards span{font-size:.86rem}
.table-scroll{max-width:100%;overflow-x:auto}table{border-collapse:collapse;font-size:.93rem;line-height:1.55;width:100%;margin:1.15rem 0}th,td{text-align:left;vertical-align:top;border:1px solid #dfe5e1;padding:.7rem .78rem}th{background:#eff5f0;color:#225d46}tbody tr:nth-child(even){background:#f9faf9}
.authored-note pre{white-space:pre;overflow-x:auto;background:#1d2f2b;color:#f1f7f4;padding:1rem 1.25rem;line-height:1.6;border-radius:.45rem;font-size:.88rem}.authored-note pre code{white-space:pre;background:none;color:inherit}
.authored-note details{border:1px solid #d8e4dc;border-radius:.4rem;padding:.65rem .95rem;background:#f9fcfa}.authored-note details summary{cursor:pointer;font-weight:600;line-height:1.6}.authored-note details[open] summary{margin-bottom:.8rem}
.note-toc{background:#f7faf8;border:1px solid #dfe9e3;border-radius:.5rem;padding:.8rem 1.2rem;margin:1.35rem 0 2rem;white-space:normal}.note-toc p{margin:.3rem 0}.note-toc ol{padding-left:1.5rem;columns:2;column-gap:2rem}.note-toc li{break-inside:avoid;margin:.38rem 0;font-size:.86rem}.note-toc a{text-decoration:none;color:#2d6753}.note-toc a:hover{text-decoration:underline}.page-title{line-height:1.25}.post-meta{color:#64766a}
.chapter-diagram{max-width:100%;border:1px solid #d7e3db;border-radius:.55rem;background:#fcfefd;padding:.45rem;margin:1.25rem 0}.chapter-diagram svg{display:block;width:100%;height:auto}.chapter-diagram figcaption{color:#66766e;font-size:.84rem;padding:.45rem .6rem}
.em-lab{border:1px solid #cae2d3;border-radius:.6rem;padding:1.15rem;background:#f7fbf8}.lab-controls{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center}.lab-controls label{font-size:.88rem}.lab-controls select,.lab-controls button{border:1px solid #accfbd;border-radius:.4rem;background:#fff;padding:.4rem .6rem;font:inherit}.lab-controls button{cursor:pointer}.lab-controls button:hover{background:#e9f4ed}.lab-controls button:focus-visible,.lab-controls select:focus-visible{outline:3px solid #d1ad65}.lab-status{font-size:.88rem;color:#466755}.em-lab svg{display:block;width:100%;height:auto;background:#fff;border:1px solid #dce8e0;border-radius:.4rem}.lab-readout{font-family:ui-monospace,Consolas,monospace;background:#fff;border:1px solid #e0ebe3;padding:.7rem;line-height:1.75;font-size:.85rem;margin:.7rem 0;overflow-wrap:anywhere}.em-lab table{margin:.6rem 0 0}.references{font-size:.92rem}
@media(max-width:700px){.note-toc ol{columns:1}.flow-cards{grid-template-columns:1fr}.authored-note h2{font-size:1.45rem}.authored-note{font-size:1rem}.authored-note table{font-size:.84rem}.authored-note th,.authored-note td{padding:.5rem}.lab-controls{align-items:stretch}.lab-controls label,.lab-controls button{width:100%}}
@media print{.note-toc{break-after:page}.em-lab button,.em-lab select{display:none}.authored-note h2{break-after:avoid}.authored-note table,.chapter-diagram,.note-focus{break-inside:avoid}.authored-note details:not([open]){display:none}}
'''

APP_JS = r'''
(() => {
  const points = [-2, -1, 1, 2];
  const lab = document.getElementById('em-lab');
  if (!lab) return;
  const chart = document.getElementById('em-chart');
  const status = document.getElementById('em-status');
  const output = document.getElementById('em-readout');
  const table = document.getElementById('em-responsibilities');
  const button = document.getElementById('em-step');
  const preset = document.getElementById('em-preset');
  const NS = 'http://www.w3.org/2000/svg';
  let state;
  const density = (x,m,v) => Math.exp(-(x-m)*(x-m)/(2*v))/Math.sqrt(2*Math.PI*v);
  function likelihood(s) {
    return points.reduce((sum,x) => sum + Math.log(s.pi[0]*density(x,s.mu[0],s.variance[0])+s.pi[1]*density(x,s.mu[1],s.variance[1])),0);
  }
  function element(name, attrs) {
    const tag=document.createElementNS(NS,name);
    for(const [key,value] of Object.entries(attrs)) tag.setAttribute(key,String(value));
    chart.appendChild(tag); return tag;
  }
  function svgText(x,y,value,color='#62766a') {
    const tag=element('text',{x,y,fill:color,'font-size':13,'font-family':'Segoe UI, sans-serif'});
    tag.textContent=value; return tag;
  }
  function draw() {
    chart.replaceChildren();
    const left=53, right=741, top=34, bottom=250;
    const xScale=x => left+(x+4.5)/9*(right-left);
    const samples=Array.from({length:240},(_,i)=>-4.5+i*9/239);
    const c1=samples.map(x=>state.pi[0]*density(x,state.mu[0],state.variance[0]));
    const c2=samples.map(x=>state.pi[1]*density(x,state.mu[1],state.variance[1]));
    const total=samples.map((_,i)=>c1[i]+c2[i]);
    const maximum=Math.max(...total,...c1,...c2)*1.16;
    const yScale=y => bottom-y/maximum*(bottom-top);
    element('line',{x1:left,y1:bottom,x2:right,y2:bottom,stroke:'#788b7c','stroke-width':1.5});
    for(const tick of [-4,-2,0,2,4]){
      element('line',{x1:xScale(tick),y1:bottom,x2:xScale(tick),y2:bottom+6,stroke:'#87978a'});
      svgText(xScale(tick)-6,bottom+22,String(tick));
    }
    for(const [arr,color,width] of [[total,'#1f2d28',3.2],[c1,'#2876a3',2.8],[c2,'#cb7442',2.8]]){
      const path=arr.map((y,i)=>(i===0?'M':'L')+xScale(samples[i]).toFixed(2)+' '+yScale(y).toFixed(2)).join(' ');
      element('path',{d:path,fill:'none',stroke:color,'stroke-width':width});
    }
    for(const x of points) element('circle',{cx:xScale(x),cy:bottom,r:5.2,fill:'#163d2e'});
    svgText(left,23,'混合密度 p(x)','#1f2d28');
    svgText(left+150,23,'π₁ N(x | μ₁, σ₁²)','#2876a3');
    svgText(left+390,23,'π₂ N(x | μ₂, σ₂²)','#cb7442');
    svgText(right-76,bottom+22,'观测 x');
    output.textContent='π=['+state.pi.map(v=>v.toFixed(3)).join(', ')+']   μ=['+state.mu.map(v=>v.toFixed(4)).join(', ')+']   方差=['+state.variance.map(v=>v.toFixed(4)).join(', ')+']   ℓ='+likelihood(state).toFixed(6);
  }
  function reset(){
    state={pi:[.5,.5],mu:preset.value==='symmetric'?[0,0]:[-1,1],variance:preset.value==='symmetric'?[2.5,2.5]:[1,1],responsibility:null,phase:'E',iteration:0};
    button.textContent='执行 E 步';table.replaceChildren();
    const row=document.createElement('tr'),cell=document.createElement('td');cell.colSpan=3;cell.textContent='点击“执行 E 步”后显示。';row.appendChild(cell);table.appendChild(row);
    status.textContent='初始参数已给定：先计算责任度。';draw();
  }
  function eStep(){
    state.responsibility=points.map(x=>{
      const unnormalized=state.mu.map((m,k)=>state.pi[k]*density(x,m,state.variance[k]));
      const denominator=unnormalized[0]+unnormalized[1];
      return unnormalized.map(v=>v/denominator);
    });
    table.replaceChildren();
    state.responsibility.forEach((row,i)=>{
      const tr=document.createElement('tr');
      [String(points[i]),row[0].toFixed(6),row[1].toFixed(6)].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.appendChild(td);});
      table.appendChild(tr);
    });
    state.phase='M';button.textContent='执行 M 步';
    status.textContent='E 步完成：责任度已刷新，参数与观测似然尚未变化。';
  }
  function mStep(){
    const r=state.responsibility;
    const Nk=[0,1].map(k=>r.reduce((sum,row)=>sum+row[k],0));
    const means=[0,1].map(k=>points.reduce((sum,x,i)=>sum+r[i][k]*x,0)/Nk[k]);
    const variance=[0,1].map(k=>Math.max(.05,points.reduce((sum,x,i)=>sum+r[i][k]*(x-means[k])**2,0)/Nk[k]));
    state={pi:Nk.map(value=>value/points.length),mu:means,variance,responsibility:r,phase:'E',iteration:state.iteration+1};
    button.textContent='执行下一轮 E 步';
    status.textContent='第 '+state.iteration+' 轮 M 步完成：使用上方固定责任度更新了参数。下一步才会重算责任度。';
    draw();
  }
  preset.addEventListener('change',reset);
  document.getElementById('em-reset').addEventListener('click',reset);
  button.addEventListener('click',()=>state.phase==='E'?eStep():mStep());
  reset();
})();
'''

def latent_diagram() -> str:
    return r'''<figure class="chapter-diagram"><svg viewBox="0 0 760 240" role="img" aria-label="混合模型的生成过程：混合比例选择隐藏分量，分量参数与隐藏分量共同决定观测"><defs><marker id="p-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9" fill="none" stroke="#577969"/></marker></defs><rect x="35" y="44" width="173" height="66" rx="12" fill="#e7f4ea" stroke="#86b89a"/><rect x="292" y="44" width="173" height="66" rx="12" fill="#eef3f9" stroke="#9bb6d0"/><rect x="549" y="44" width="173" height="66" rx="12" fill="#faf0e7" stroke="#d1ad8a"/><text x="53" y="74" font-size="19" font-family="Microsoft YaHei">混合比例 π</text><text x="302" y="74" font-size="19" font-family="Microsoft YaHei">隐藏来源 z</text><text x="568" y="74" font-size="19" font-family="Microsoft YaHei">观测数据 x</text><text x="53" y="96" font-size="12" font-family="Microsoft YaHei">给分量分配先验概率</text><text x="302" y="96" font-size="12" font-family="Microsoft YaHei">训练时没有观察到</text><text x="568" y="96" font-size="12" font-family="Microsoft YaHei">真正拿到的样本</text><path d="M208 76 H282" stroke="#577969" stroke-width="2" marker-end="url(#p-arrow)"/><path d="M465 76 H539" stroke="#577969" stroke-width="2" marker-end="url(#p-arrow)"/><rect x="297" y="150" width="172" height="53" rx="11" fill="#f8f8f0" stroke="#c8ccb4"/><text x="315" y="182" font-size="17" font-family="Microsoft YaHei">分量参数 μ, Σ</text><path d="M468 176 C570 176 632 162 632 120" fill="none" stroke="#9eaa6d" stroke-width="2" marker-end="url(#p-arrow)"/></svg><figcaption>原创教学示意：\(p(x,z\mid\theta)=p(z\mid\pi)p(x\mid z,\mu,\Sigma)\)。观测不到 z 时，对 z 求和得到混合密度。</figcaption></figure>'''

def math_render(source: str) -> tuple[str,int]:
    matches=list(MATH.finditer(source))
    payload=[{'tex':unescape(m.group(1) if m.group(1) is not None else m.group(2)).strip(), 'display':m.group(1) is not None} for m in matches]
    result=subprocess.run([str(NODE),str(ROOT/'tools/render_prml_math.cjs')],input=json.dumps(payload,ensure_ascii=False),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stderr)
    rendered=json.loads(result.stdout)
    iterator=iter(rendered)
    return MATH.sub(lambda match: next(iterator),source),len(payload)

def build():
    if not NODE.exists():
        raise FileNotFoundError('Local Node runtime used for KaTeX compilation is unavailable')
    pieces=[(SOURCE/name).read_text(encoding='utf-8') for name in PARTS]
    pieces[0]=pieces[0].replace('<div class="flow-cards">',latent_diagram()+'<div class="flow-cards">',1)
    content='\n'.join(pieces)
    headings=re.findall(r'<h2\s+id="([^"]+)"\s*>(.*?)</h2>',content,flags=re.S)
    nav=''.join('<li><a href="#'+escape(identifier,quote=True)+'">'+title+'</a></li>' for identifier,title in headings)
    toc='<nav class="note-toc" aria-label="本篇目录"><p><strong>本篇目录 · '+str(len(headings))+' 节</strong></p><ol>'+nav+'</ol></nav>'
    body,formulas=math_render(content)
    sample=(ROOT/'docs/posts/guidance/index.html').read_text(encoding='utf-8')
    head=re.search(r'<head>(.*?)</head>',sample,re.S).group(1)
    head=re.sub(r'<title>.*?</title>','<title>'+escape(POST['title']+' · '+SITE_TITLE)+'</title>',head,count=1)
    head=re.sub(r'<meta\s+name="description"[^>]*>','',head)
    head += '<meta name="description" content="'+escape(POST['description'],quote=True)+'">'
    head += '<meta name="robots" content="noindex, nofollow">'
    head += '<style>'+STYLE+'</style>'
    html='<!doctype html><html lang="zh-CN"><head>'+head+'</head><body><article class="page sans"><nav class="site-nav" aria-label="网站导航"><a href="../../">← '+escape(SITE_TITLE)+'</a></nav><header><p class="post-meta">'+escape(POST['section'])+'</p><h1 class="page-title">'+escape(POST['title'])+'</h1></header>'+toc+'<div class="page-body authored-note">'+body+'</div><nav class="post-nav" aria-label="文章导航"><a href="../../">返回文章目录</a></nav></article><script>'+APP_JS+'</script></body></html>'
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(html,encoding='utf-8',newline='\n')
    posts_path=ROOT/'docs/posts.json'
    posts=json.loads(posts_path.read_text(encoding='utf-8'))
    old=next((i for i,record in enumerate(posts) if record['slug']==POST['slug']),None)
    if old is None:posts.append(POST)
    else:posts[old]=POST
    posts_path.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    rebuild_site(ROOT)
    report={'page':str(DEST.relative_to(ROOT)),'headings':len(headings),'formulas':formulas,'chinese_characters':len(re.findall(r'[\u4e00-\u9fff]',content)),'size_bytes':DEST.stat().st_size}
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    build()
