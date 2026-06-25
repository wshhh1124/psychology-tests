#!/usr/bin/env python3
"""
小红书笔记生成器
用法: python3 note_generator.py <test_config.json> [--count N] [--style <style>]

给定测试配置，生成：
  - 封面图 PNG（1080×1440，3:4，适配小红书）
  - 文案 MD（标题 + 正文 + 话题标签）
  - preview.html（封面+文案预览页）
全部输出到 notes/<测试名>/
"""
import json
import sys
import os
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Color palettes ──────────────────────────────────────────
PALETTES = [
    {"bg_top": (108, 92, 231, 255), "bg_bot": (162, 155, 254, 255), "accent": "#FFEAA7", "text": "#FFFFFF", "name": "梦幻紫"},
    {"bg_top": (253, 121, 168, 255), "bg_bot": (255, 175, 204, 255), "accent": "#FFEAA7", "text": "#FFFFFF", "name": "恋爱粉"},
    {"bg_top": (0, 184, 148, 255), "bg_bot": (85, 230, 193, 255), "accent": "#FFFFFF", "text": "#FFFFFF", "name": "清新绿"},
    {"bg_top": (253, 203, 110, 255), "bg_bot": (255, 234, 167, 255), "accent": "#2D3436", "text": "#2D3436", "name": "暖阳黄"},
    {"bg_top": (45, 52, 54, 255), "bg_bot": (99, 110, 114, 255), "accent": "#FDCB6E", "text": "#FFFFFF", "name": "高级灰"},
]

COVER_W = 1080
COVER_H = 1440

# ── Font helpers ─────────────────────────────────────────────
def get_font(size, bold=False):
    """Try to load fonts with fallbacks for macOS."""
    font_paths = []
    if bold:
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    else:
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]

    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def gradient_bg(draw, w, h, top_color, bot_color):
    """Draw vertical gradient background."""
    for y in range(h):
        ratio = y / h
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def draw_decorative_circles(draw, w, h, palette):
    """Add subtle decorative circles."""
    import math
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    circles = [
        (w - 80, 200, 180, (255, 255, 255, 15)),
        (60, h - 300, 240, (255, 255, 255, 10)),
        (w // 2 + 150, h // 2 - 100, 120, (255, 255, 255, 12)),
    ]
    for cx, cy, r, fill_color in circles:
        overlay_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill_color)

    return overlay


def draw_stars(draw, w, h):
    """Add tiny star-like dots."""
    import math
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for _ in range(30):
        x = random.randint(40, w - 40)
        y = random.randint(40, h - 40)
        size = random.randint(2, 5)
        alpha = random.randint(20, 60)
        overlay_draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255, alpha))
    return overlay


def generate_cover(test_config, palette, output_path):
    """Generate a 小红书-style cover image."""
    w, h = COVER_W, COVER_H
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background
    gradient_bg(draw, w, h, palette["bg_top"], palette["bg_bot"])

    # Decorative elements
    circles = draw_decorative_circles(draw, w, h, palette)
    img = Image.alpha_composite(img, circles)
    draw = ImageDraw.Draw(img)

    stars = draw_stars(draw, w, h)
    img = Image.alpha_composite(img, stars)
    draw = ImageDraw.Draw(img)

    # Icon
    icon = test_config.get("icon", "🧠")
    icon_font = get_font(120)
    try:
        icon_bbox = draw.textbbox((0, 0), icon, font=icon_font)
        icon_w = icon_bbox[2] - icon_bbox[0]
    except Exception:
        icon_w = 120
    draw.text(((w - icon_w) // 2, 200), icon, font=icon_font, fill="white")

    # Main title - wrap into multiple lines
    title = test_config.get("title", "心理测试")
    title_font = get_font(80, bold=True)
    title_lines = wrap_text(title, title_font, draw, w - 160)

    y = 400
    for line in title_lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = len(line) * 40
        draw.text(((w - tw) // 2, y), line, font=title_font, fill="white")
        # Add subtle shadow
        draw.text(((w - tw) // 2 + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 40))
        draw.text(((w - tw) // 2, y), line, font=title_font, fill="white")
        y += 110

    # Subtitle / hook
    hooks = [
        "10道题 · 测出最真实的你 🔮",
        "你敢来测吗？结果超乎想象 ✨",
        "99%的人测完都说准！💯",
        "朋友都在测，快来试试 👀",
    ]
    hook = random.choice(hooks)
    sub_font = get_font(42)
    try:
        sbbox = draw.textbbox((0, 0), hook, font=sub_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        sw = len(hook) * 21

    # Tag badge below subtitle
    y += 60
    badge_pad = 40
    badge_h = 70
    try:
        badge_w = sw + badge_pad * 2
    except Exception:
        badge_w = 500
    badge_x = (w - badge_w) // 2
    draw.rounded_rectangle(
        [badge_x, y, badge_x + badge_w, y + badge_h],
        radius=35, fill=(255, 255, 255, 40)
    )
    draw.text(((w - sw) // 2, y + 12), hook, font=sub_font, fill="white")

    # Bottom section - question count + CTA
    y = h - 320
    cta_font = get_font(36)
    cta_lines = [
        f"共 {len(test_config.get('questions', []))} 道题 | 约 2 分钟",
        "点击下方链接，立刻测试 👇",
    ]
    for line in cta_lines:
        try:
            cbbox = draw.textbbox((0, 0), line, font=cta_font)
            cw = cbbox[2] - cbbox[0]
        except Exception:
            cw = len(line) * 18
        draw.text(((w - cw) // 2, y), line, font=cta_font, fill=(255, 255, 255, 180))
        y += 55

    # Convert to RGB and save
    img_rgb = img.convert("RGB")
    img_rgb.save(output_path, "PNG", quality=95)
    return output_path


def wrap_text(text, font, draw, max_width):
    """Wrap Chinese text into multiple lines."""
    lines = []
    current_line = ""
    for char in text:
        test_line = current_line + char
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = len(test_line) * 40
        if tw > max_width and current_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    return lines if lines else [text]


def generate_note_text(test_config, style_idx=0):
    """Generate note title, body, and hashtags."""
    title = test_config.get("title", "心理测试")
    questions = test_config.get("questions", [])
    n_questions = len(questions)

    # Pick 2 sample questions as teasers
    teaser_questions = random.sample(questions, min(2, len(questions)))

    styles = [
        {
            "note_title": f"「{title}」你敢来测吗？🔮",
            "body": f"""最近发现了一个超有意思的心理测试——{title}！

只用了{n_questions}道题，就把我的隐藏性格摸得透透的...结果出来的时候我直接震惊了😱

随便剧透两道题给你们感受下：

1️⃣ {teaser_questions[0]['text']}

2️⃣ {teaser_questions[1]['text'] if len(teaser_questions) > 1 else '...'}

每道题都直击灵魂，做完你会看到一个完全不一样的自己。

我测出来的结果真的太准了！闺蜜测完也说好准👆

戳下方链接，看看你是什么类型？记得回来评论区告诉我结果！💕""",
            "hashtags": ["心理测试", "恋爱测试", "性格测试", "了解自己", "超准测试", "心理学科普", "情感测试", "测一测"]
        },
        {
            "note_title": f"我竟然是这样的人？！这个测试太准了💯",
            "body": f"""刷到就是缘分！这个{title}真的绝了...

花了大概两分钟做完，结果出来那一刻我沉默了——比我自己还了解我自己。

给你们看看其中两道题：

✨ {teaser_questions[0]['text']}

✨ {teaser_questions[1]['text'] if len(teaser_questions) > 1 else '...'}

一共有{n_questions}道题，每道都让我思考了一下下。

链接放下面了！做完的说一下你们是什么类型，我想看看有没有一样的😭""",
            "hashtags": ["心理测试", "准到离谱", "恋爱人格", "自我认知", "性格分析", "今日测试", "心理学", "测一测"]
        },
        {
            "note_title": f"{title.replace('你的', '')}？你的是什么？点进来测！",
            "body": f"""⚠️ 警告：这可能是你今天点进来最正确的一个链接！

{title}——我设计这个测试的原因很简单：帮你看清自己在感情中真正的样子。

一共{n_questions}道选择题，每道题都经过了精心设计👇

不剧透太多了，做完你就知道。反正我测完发给朋友，大家都说准到起鸡皮疙瘩...

🔗 链接在下方，两分钟的事，试一下不亏～""",
            "hashtags": ["心理测试", "测测你", "情感心理", "自我探索", "性格测试", "今日分享", "走心推荐"]
        },
    ]

    return styles[style_idx % len(styles)]


def generate_note(test_config_path, output_dir=None, style_idx=0):
    """Generate a complete note package from a test config."""
    # Load config
    with open(test_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    test_name = os.path.splitext(os.path.basename(test_config_path))[0]

    if output_dir is None:
        output_dir = os.path.join(PROJECT_DIR, 'notes', test_name)

    os.makedirs(output_dir, exist_ok=True)

    # Pick palette with variation
    palette = PALETTES[style_idx % len(PALETTES)]

    # Generate cover image
    cover_path = os.path.join(output_dir, 'cover.png')
    generate_cover(config, palette, cover_path)
    print(f'✅ 封面图: {cover_path}')

    # Generate note text
    note = generate_note_text(config, style_idx)
    md_path = os.path.join(output_dir, '文案.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# {note['note_title']}\n\n")
        f.write(note['body'])
        f.write(f"\n\n---\n")
        f.write(" ".join(f"#{tag}" for tag in note['hashtags']))
    print(f'✅ 文案: {md_path}')

    # Generate preview HTML
    preview_path = os.path.join(output_dir, 'preview.html')
    generate_preview_html(config, note, palette, preview_path)
    print(f'✅ 预览: {preview_path}')

    return output_dir


def generate_preview_html(config, note, palette, preview_path):
    """Generate an HTML preview showing cover + text together."""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>笔记预览 - {config["title"]}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f5f5f5;
    padding: 24px 16px;
  }}
  .wrapper {{
    max-width: 420px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }}
  .section-title {{
    font-size: 13px;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-align: center;
  }}
  .cover-preview {{
    width: 100%;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  }}
  .cover-preview img {{
    width: 100%;
    display: block;
  }}
  .note-card {{
    background: #fff;
    border-radius: 16px;
    padding: 24px 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  }}
  .note-card h2 {{
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 16px;
    line-height: 1.4;
  }}
  .note-card .body {{
    font-size: 15px;
    line-height: 1.8;
    color: #2D3436;
    white-space: pre-wrap;
  }}
  .note-card .hashtags {{
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;
    font-size: 14px;
    color: #6C5CE7;
    line-height: 1.8;
  }}
  .btn-row {{
    display: flex;
    gap: 10px;
  }}
  .btn {{
    flex: 1;
    padding: 14px;
    border-radius: 14px;
    font-size: 15px;
    font-weight: 600;
    text-align: center;
    cursor: pointer;
    border: none;
    text-decoration: none;
    display: inline-block;
    color: #fff;
    background: linear-gradient(135deg, #6C5CE7, #A29BFE);
  }}
  .btn-outline {{
    background: #fff;
    color: #6C5CE7;
    border: 2px solid #EDE8FD;
  }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="section-title">📱 笔记封面图</div>
  <div class="cover-preview">
    <img src="cover.png" alt="封面图">
  </div>
  <div class="btn-row">
    <a class="btn" href="cover.png" download>📥 下载封面图</a>
    <button class="btn btn-outline" onclick="copyText()">📋 复制文案</button>
  </div>

  <div class="section-title">📝 笔记文案</div>
  <div class="note-card" id="noteText">
    <h2>{note['note_title']}</h2>
    <div class="body">{note['body']}</div>
    <div class="hashtags">{' '.join('#' + t for t in note['hashtags'])}</div>
  </div>
</div>

<script>
function copyText() {{
  const text = document.getElementById('noteText').innerText;
  navigator.clipboard.writeText(text).then(() => {{
    alert('文案已复制到剪贴板！');
  }});
}}
</script>
</body>
</html>'''
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 note_generator.py <config.json> [--count N] [--style <0-4>]')
        print('示例: python3 note_generator.py tests/love-style.json --count 3')
        sys.exit(1)

    config_file = sys.argv[1]
    count = 1
    style_start = random.randint(0, len(PALETTES) - 1)

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--count' and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        elif args[i] == '--style' and i + 1 < len(args):
            style_start = int(args[i + 1])
            i += 2
        else:
            i += 1

    for n in range(count):
        style_idx = style_start + n
        test_name = os.path.splitext(os.path.basename(config_file))[0]
        out = os.path.join(PROJECT_DIR, 'notes', test_name, f'v{style_idx + 1}')
        generate_note(config_file, out, style_idx)
        print(f'  → 第 {n + 1} 套笔记: {out}\n')
