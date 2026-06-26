#!/usr/bin/env python3
"""
批量生成小红书笔记图文组图HTML
用法: python3 generate_note_html.py note-configs/note-02-back-pain.json
      python3 generate_note_html.py --all   # 批量生成全部
"""
import json, os, sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(PROJECT, 'social-card')

HTML_TEMPLATE = '''<!doctype html>
<html lang="zh-CN" data-theme="ink-classic">
<head>
<meta charset="utf-8">
<title>{cover_hook}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*,*::before,*::after{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{background:#1a1a1a;font-family:Georgia,"Noto Serif SC","Songti SC","PingFang SC",serif;-webkit-font-smoothing:antialiased;padding:48px 24px}}
.sheet{{display:flex;flex-direction:column;align-items:center;gap:48px}}
:root,[data-theme="ink-classic"]{{
  --paper:#f3f0e8;--paper-2:#ebe6da;--ink:#0a0a0b;--muted:#68625a;
  --line:rgba(10,10,11,.22);--accent:#111111;--accent-soft:#d8d2c6;
}}
.poster{{position:relative;width:1080px;height:1440px;background:var(--paper);color:var(--ink);overflow:hidden;isolation:isolate}}
.poster.xhs{{width:1080px;height:1440px}}
.poster.xhs .content{{padding:96px 88px;position:relative;width:100%;height:100%;z-index:2;display:flex;flex-direction:column}}
.grain{{position:absolute;inset:0;z-index:1;pointer-events:none;opacity:.35;mix-blend-mode:multiply;background-image:radial-gradient(rgba(0,0,0,.045) 1px,transparent 1px);background-size:3px 3px}}
.paper-wash{{position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(180deg,rgba(10,10,11,.02),rgba(10,10,11,.05) 60%,rgba(10,10,11,.08))}}
.kicker{{font-family:"IBM Plex Mono",monospace;font-size:20px;letter-spacing:.22em;text-transform:uppercase;color:rgba(10,10,11,.50);margin:0 0 16px}}
.h-hero{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:134px;line-height:1.06;letter-spacing:-.01em;color:var(--ink);margin:0}}
.h-display{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:106px;line-height:1.08;letter-spacing:-.01em;color:var(--ink);margin:0}}
.h-xl{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:78px;line-height:1.10;letter-spacing:-.01em;color:var(--ink);margin:0}}
.h-md{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:54px;line-height:1.16;letter-spacing:-.01em;color:var(--ink);margin:0}}
.h-sub{{font-family:Georgia,serif;font-style:italic;font-weight:400;font-size:34px;color:var(--muted);margin:0}}
.lead{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:400;font-size:28px;line-height:1.6;color:rgba(10,10,11,.82);margin:0}}
.body-text{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:400;font-size:26px;line-height:1.7;color:rgba(10,10,11,.80);margin:0}}
.meta{{font-family:"IBM Plex Mono",monospace;font-size:17px;letter-spacing:.14em;text-transform:uppercase;color:rgba(10,10,11,.50);margin:0}}
.pull-quote{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:68px;line-height:1.22;color:var(--ink);margin:0;padding-left:48px;border-left:6px solid var(--accent)}}
.stack{{display:flex;flex-direction:column}}.gap-2{{gap:24px}}.gap-3{{gap:36px}}.gap-4{{gap:48px}}.grow{{flex:1}}.center{{text-align:center}}
.rule{{height:1px;background:var(--line);border:0;margin:24px 0}}
.rule-accent{{height:3px;background:var(--accent);border:0;margin:28px 0;width:120px}}
.w-60{{width:60px}}
.issue-row{{display:flex;align-items:center;gap:14px;font-family:"IBM Plex Mono",monospace;font-size:18px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}
.issue-row .dot{{width:5px;height:5px;border-radius:50%;background:var(--accent)}}
.issue-strip{{position:absolute;left:88px;right:88px;bottom:56px;display:flex;justify-content:space-between;align-items:center;gap:24px;font-family:"IBM Plex Mono",monospace;font-size:16px;letter-spacing:.10em;text-transform:uppercase;color:var(--muted);border-top:1px solid var(--line);padding-top:16px;z-index:2}}
.issue-strip span{{white-space:nowrap}}
.info-card{{background:var(--paper-2);padding:28px 32px;margin-bottom:18px}}
.info-card .card-label{{font-family:"IBM Plex Mono",monospace;font-size:16px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}}
.info-card .card-title{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:30px;line-height:1.3;margin-bottom:6px}}
.info-card .card-desc{{font-family:Georgia,"Noto Serif SC","Songti SC",serif;font-size:21px;line-height:1.5;color:var(--muted)}}
.illus{{position:absolute;z-index:0;pointer-events:none}}
.illus-circle{{position:absolute;border-radius:50%}}
.dot-grid{{position:absolute;background-image:radial-gradient(circle,var(--line) 1.5px,transparent 1.5px);background-size:24px 24px;opacity:.25}}
</style>
</head>
<body><main class="sheet">

{page1}

{page2}

{page3}

{page4}

{page5}

{casePage}

</main></body></html>'''

def page_cover(cfg):
    c = cfg['cover']
    return f'''<section class="poster xhs">
  <div class="grain"></div><div class="paper-wash"></div>
  <div class="illus" style="top:-80px;right:-120px">
    <div class="illus-circle" style="width:500px;height:500px;background:var(--accent);opacity:.08;top:0;left:0"></div>
    <div class="illus-circle" style="width:320px;height:320px;background:var(--accent-soft);opacity:.12;top:200px;left:-80px"></div>
    <div class="illus-circle" style="width:180px;height:180px;background:var(--line);opacity:.15;top:60px;left:280px"></div>
  </div>
  <div class="dot-grid" style="left:60px;bottom:200px;width:240px;height:240px"></div>
  <div class="content stack" style="justify-content:space-between">
    <div class="issue-row"><span>身心科普</span><span class="dot"></span><span>{c.get('series','')}</span></div>
    <div class="stack gap-3 grow" style="justify-content:center">
      <h1 class="h-hero">{c['hookLine1']}<br>{c['hookLine2']}</h1>
      <div class="rule-accent w-60"></div>
      <p class="h-sub" style="font-size:30px">{c['subtitle']}</p>
    </div>
    <div class="issue-strip"><span>{c.get('source','')}</span><span>—</span><span>{c.get('book','')}</span></div>
  </div>
</section>'''

def page_credibility(cfg):
    c = cfg.get('cover', cfg)
    return f'''<section class="poster xhs">
  <div class="grain"></div><div class="paper-wash"></div>
  <div class="illus" style="top:120px;right:80px">
    <div style="width:180px;height:180px;border:2px solid var(--line);position:absolute;top:0;left:0"></div>
    <div style="width:180px;height:180px;border:2px solid var(--line);position:absolute;top:36px;left:36px"></div>
  </div>
  <div class="content stack gap-4" style="justify-content:center">
    <div class="issue-row"><span>关于作者与本书</span></div>
    <div class="stack gap-3">
      <div class="info-card">
        <p class="card-label">Author</p>
        <p class="card-title">露易丝·海</p>
        <p class="card-desc">国际心理治疗专家，自我肯定理论开创者。《生命的重建》全球销量超 5000 万册，被誉为"身心疗愈之母"。</p>
      </div>
      <div class="info-card">
        <p class="card-label">Co-Author</p>
        <p class="card-title">蒙娜·丽莎·舒尔茨 博士</p>
        <p class="card-desc">神经精神病学家，30 年临床经验。从脑科学和免疫学角度为身心连接提供了坚实的科学证据。</p>
      </div>
      <div class="info-card">
        <p class="card-label">The Book · 2025 中信出版社</p>
        <p class="card-title">《一切都会好的》</p>
        <p class="card-desc">7 情绪中心理论 · 85 道身心评估 · 200+ 症状对照表 · 医学+营养+正念+直觉引导综合疗法</p>
      </div>
    </div>
    <div class="issue-strip"><span>New York Times Bestselling Author</span><span>—</span><span>Heal Your Life</span></div>
  </div>
</section>'''

def page_bombshell(cfg):
    b = cfg['bombshell']
    return f'''<section class="poster xhs">
  <div class="grain"></div><div class="paper-wash"></div>
  <div class="illus" style="top:50%;left:50%;transform:translate(-50%,-50%)">
    <div class="illus-circle" style="width:500px;height:500px;background:var(--accent);opacity:.03;top:-250px;left:-250px"></div>
    <div class="illus-circle" style="width:300px;height:300px;background:var(--accent-soft);opacity:.06;top:-150px;left:-150px"></div>
  </div>
  <div class="content stack gap-4" style="justify-content:center">
    <div class="issue-row"><span>颠覆认知的研究</span><span class="dot"></span><span>Counterintuitive</span></div>
    <div class="pull-quote" style="font-size:64px;line-height:1.22">
      "{b['quote']}"
    </div>
    <div class="rule-accent w-60"></div>
    <p class="lead" style="font-size:28px">{b['explanation']}</p>
    <div class="issue-strip"><span>Source: 《一切都会好的》</span><span>—</span><span>Peer-reviewed</span></div>
  </div>
</section>'''

def page_body_signals(cfg):
    s = cfg['bodySignals']
    signals_html = ''.join(f'<p class="body-text" style="font-size:26px">→ {sig}</p>' for sig in s['signals'])
    note_html = f'<p class="body-text" style="font-size:21px;color:var(--muted)">"{s["note"]}"</p>' if 'note' in s else ''
    return f'''<section class="poster xhs">
  <div class="grain"></div><div class="paper-wash"></div>
  <div class="illus" style="bottom:-60px;right:-40px">
    <div class="illus-circle" style="width:300px;height:300px;background:var(--accent-soft);opacity:.20;top:0;left:0"></div>
    <div class="illus-circle" style="width:160px;height:160px;background:var(--accent);opacity:.08;top:100px;left:100px"></div>
  </div>
  <div class="content stack gap-4" style="justify-content:center">
    <div class="issue-row"><span>身体在替情绪说话</span></div>
    <h2 class="h-md" style="font-size:52px">{s['title']}</h2>
    <div class="rule-accent w-60"></div>
    <div class="stack gap-1">{signals_html}</div>
    <div class="rule-accent w-60"></div>
    <p class="lead" style="font-size:30px">{s['insight']}</p>
    {note_html}
    <div class="issue-strip"><span>Listen to your body</span><span>—</span><span>Emotional Center</span></div>
  </div>
</section>'''

def page_cta(cfg):
    ct = cfg['cta']
    return f'''<section class="poster xhs">
  <div class="grain"></div><div class="paper-wash"></div>
  <div class="illus" style="top:50%;left:50%;transform:translate(-50%,-50%)">
    <div class="illus-circle" style="width:450px;height:450px;background:var(--accent);opacity:.03;top:-225px;left:-225px"></div>
  </div>
  <div class="content stack center" style="justify-content:center;align-items:center;text-align:center">
    <p class="kicker" style="text-align:center">85 Questions · 7 Dimensions</p>
    <h2 class="h-xl" style="font-size:72px;text-align:center">{ct['title']}</h2>
    <div class="rule-accent w-60" style="margin:28px auto"></div>
    <p class="lead" style="text-align:center;font-size:26px">{ct['description']}</p>
    <div style="margin:36px 0">
      <div style="display:inline-block;padding:24px 48px;border:3px solid var(--accent)">
        <p class="meta" style="font-size:17px;text-align:center;color:var(--ink)">点击下方商品链接 · 获取完整评估</p>
      </div>
    </div>
    <div class="rule-accent w-60" style="margin:28px auto"></div>
    <p class="body-text" style="text-align:center;font-size:24px;color:var(--muted);font-style:italic">每天对自己说：</p>
    <p class="lead" style="text-align:center;font-size:30px;font-weight:700">"一切都会好的。"</p>
    <p class="meta" style="font-size:13px;text-align:center;margin-top:8px">— 露易丝·海</p>
  </div>
  <div class="issue-strip"><span>Louise Hay</span><span>—</span><span>All Is Well</span><span>—</span><span>Begin Your Journey</span></div>
</section>'''

def page_case_study(cfg):
    cs = cfg.get('caseStudy')
    if not cs:
        return ''
    items = cs.get('items', [])
    items_html = ''.join(f'<p class="body-text" style="font-size:26px;margin-bottom:16px">{item}</p>' for item in items)
    note_html = f'<p class="body-text" style="font-size:21px;color:var(--muted);margin-top:24px">{cs["note"]}</p>' if cs.get('note') else ''
    return f'''<section class="poster xhs">
  <div class="grain"></div><div class="paper-wash"></div>
  <div class="illus" style="top:50%;left:50%;transform:translate(-50%,-50%)">
    <div class="illus-circle" style="width:500px;height:500px;background:var(--accent);opacity:.03;top:-250px;left:-250px"></div>
    <div class="illus-circle" style="width:300px;height:300px;background:var(--accent-soft);opacity:.06;top:-150px;left:-150px"></div>
  </div>
  <div class="content stack gap-4" style="justify-content:center">
    <div class="issue-row"><span>{cs.get('label','案例')}</span><span class="dot"></span><span>真实故事</span></div>
    <h2 class="h-md" style="font-size:52px">{cs['title']}</h2>
    <div class="rule-accent w-60"></div>
    <div class="stack gap-2">
      {items_html}
    </div>
    {note_html}
    <div class="issue-strip"><span>{cs.get('source','')}</span><span>—</span><span>《一切都会好的》</span></div>
  </div>
</section>'''

def generate(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    html = HTML_TEMPLATE.format(
        cover_hook=cfg['cover']['hookLine1'],
        page1=page_cover(cfg),
        page2=page_credibility(cfg),
        page3=page_bombshell(cfg),
        page4=page_body_signals(cfg),
        page5=page_cta(cfg),
        casePage=page_case_study(cfg)
    )

    out_dir = os.path.join(OUTPUT, cfg['id'])
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'cover.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅ {cfg["id"]} → {out_path}')
    return out_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 generate_note_html.py <config.json>')
        print('      python3 generate_note_html.py --all')
        sys.exit(1)

    if sys.argv[1] == '--all':
        configs_dir = os.path.join(PROJECT, 'note-configs')
        for fn in sorted(os.listdir(configs_dir)):
            if fn.endswith('.json'):
                generate(os.path.join(configs_dir, fn))
    else:
        generate(sys.argv[1])
