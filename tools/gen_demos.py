#!/usr/bin/env python3
"""生成 UI 风格样例页：一个风格 = 一个自包含 HTML（无外部依赖，可直接复制）。

用法：
    python ui-atlas/tools/gen_demos.py

产物：
    ui-atlas/demos/<id>.html
    ui-atlas/styles.json   （站点读的数据，含 tokens / 特征 / 提示词）
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # ui-atlas/
DEMOS = ROOT / "demos"

BASE_CSS = """
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.65;
  min-height:100vh;overflow-x:hidden}
.wrap{max-width:1120px;margin:0 auto;padding:0 28px}
.nav{display:flex;align-items:center;gap:14px;padding:18px 0;border-bottom:var(--nav-border,1px solid var(--line))}
.brand{font-weight:800;letter-spacing:.02em;font-size:17px;color:var(--ink);text-decoration:none}
.nav nav{display:flex;gap:20px;margin-left:26px}
.nav nav a{color:var(--muted);text-decoration:none;font-size:14px}
.nav nav a:hover{color:var(--ink)}
.nav .spacer{flex:1}
.btn{border:var(--btn-border,none);background:var(--accent);color:var(--accent-ink,#fff);
  padding:10px 18px;border-radius:var(--radius-sm,8px);font:inherit;font-weight:600;cursor:pointer;
  box-shadow:var(--btn-shadow,none);transition:transform .15s ease,box-shadow .15s ease}
.btn:hover{transform:translateY(-1px)}
.btn.ghost{background:var(--surface);color:var(--ink);border:1px solid var(--line);box-shadow:none}
.hero{padding:76px 0 54px;max-width:760px}
.eyebrow{font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
.panel .eyebrow{margin-bottom:6px;font-size:11px}
.hero h1{margin:0 0 18px;font-size:clamp(34px,5vw,58px);line-height:1.12;letter-spacing:-.01em}
.hero .lede{margin:0 0 26px;color:var(--muted);font-size:17px;max-width:56ch}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.meta{margin:18px 0 0;font-size:13px;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:8px 0 56px}
.card{background:var(--surface);border:var(--card-border,1px solid var(--line));border-radius:var(--radius,14px);
  padding:24px;box-shadow:var(--card-shadow,none)}
.card h3{margin:0 0 8px;font-size:16px}
.card p{margin:0;color:var(--muted);font-size:14px}
.card .k{display:inline-block;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
.panel{background:var(--surface);border:var(--card-border,1px solid var(--line));border-radius:var(--radius,14px);
  padding:30px;display:grid;grid-template-columns:1fr 340px;gap:30px;align-items:start;margin-bottom:64px;
  box-shadow:var(--card-shadow,none)}
.panel h2{margin:0 0 10px;font-size:26px}
.panel p{margin:0;color:var(--muted)}
form{display:grid;gap:14px}
label{display:grid;gap:6px;font-size:13px;color:var(--muted)}
input,select{font:inherit;color:var(--ink);background:var(--field,#fff);border:1px solid var(--line);
  border-radius:var(--radius-sm,8px);padding:10px 12px;outline:none}
input:focus,select:focus{border-color:var(--accent)}
.foot{border-top:1px solid var(--line);padding:22px 0 40px;color:var(--muted);font-size:13px;display:flex;gap:16px;flex-wrap:wrap}
@media (max-width:900px){.cards{grid-template-columns:1fr}.panel{grid-template-columns:1fr}}
"""

# 每个风格：tokens + 自己的 CSS + 文案
S = []


def add(**kw):
    S.append(kw)


add(
    id="glass", name="玻璃拟态", name_en="Glassmorphism", group="classic", era="2019–",
    tokens=dict(bg="#0b1020", surface="rgba(255,255,255,.10)", ink="#eef2ff", muted="#a9b4d0",
                accent="#7aa2ff", line="rgba(255,255,255,.22)", radius="20px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["半透明磨砂面板（backdrop-filter blur + saturate）", "背景必须有高饱和光斑才成立",
              "细亮边（1px rgba 白）替代实色描边", "大圆角 + 低对比阴影，层级靠模糊度区分"],
    prompt="设计一个玻璃拟态产品页：深色渐变底 + 三团彩色光斑，卡片使用半透明白(10%)、backdrop-filter:blur(18px) saturate(140%)、1px 亮边，圆角 20px，避免实色块与硬阴影。",
    brand="Halo", h1="把工作台，做成一块玻璃", lede="半透明的层级，让内容和背景同时被看见。",
    css="""
body{background:
  radial-gradient(60% 60% at 12% 8%,#3b5bff55,transparent 60%),
  radial-gradient(50% 50% at 88% 12%,#ff4fa855,transparent 62%),
  radial-gradient(60% 60% at 60% 92%,#22d3ee44,transparent 60%),
  #0b1020}
.nav{background:rgba(255,255,255,.06);backdrop-filter:blur(14px) saturate(140%);
  border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:12px 18px;margin-top:18px}
.card,.panel{backdrop-filter:blur(18px) saturate(150%);border:1px solid rgba(255,255,255,.22);
  box-shadow:0 18px 50px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.25)}
.btn{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);backdrop-filter:blur(10px)}
.btn.ghost{background:rgba(255,255,255,.06)}
""",
)

add(
    id="neubrutalism", name="新粗野主义", name_en="Neubrutalism", group="classic", era="2022–",
    tokens=dict(bg="#f4f0e6", surface="#fffdf6", ink="#141414", muted="#5a564c",
                accent="#ff5252", line="#141414", radius="0px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["3px 纯黑描边 + 6px 硬投影（无模糊）", "零圆角，色块直接撞色",
              "粗黑标题，字重对比极端", "交互靠位移：hover 时卡片向左上挪 2px"],
    prompt="做一套新粗野主义界面：米白底、3px 黑边、6px 硬阴影（无 blur）、零圆角，主色 #ff5252，标题超粗，hover 时元素位移 2px，不要渐变与柔阴影。",
    brand="BRUTAL/01", h1="不修饰，直接说", lede="粗边、硬影、饱和色。界面不需要讨好谁。",
    css="""
body{background:#f4f0e6}
.card,.panel{border:3px solid #141414;box-shadow:6px 6px 0 #141414;border-radius:0}
.card:hover{transform:translate(-2px,-2px);box-shadow:8px 8px 0 #141414}
.btn{border:3px solid #141414;box-shadow:4px 4px 0 #141414;border-radius:0;color:#141414;background:#ffd24a;font-weight:800}
.btn:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 #141414}
.btn.ghost{background:#fff;border:3px solid #141414}
.hero h1{font-weight:900;letter-spacing:-.03em;text-transform:uppercase}
.nav{border-bottom:3px solid #141414}
""",
)

add(
    id="bento", name="Bento 网格", name_en="Bento Grid", group="classic", era="2023–",
    tokens=dict(bg="#0c0d12", surface="#16181f", ink="#f2f4f8", muted="#8b93a7",
                accent="#a3e635", line="#262a35", radius="22px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["大小不等的圆角方格拼成一屏", "每格只讲一件事，图标 + 一个数字",
              "深底 + 一个荧光强调色", "圆角统一 20–24px，格间距 12–16px"],
    prompt="用 Bento 网格做产品介绍：深色底、圆角 22px 的卡片大小交错（2x2 + 1x1 + 1x2），每格一个指标或一句话，强调色荧光绿，格间距 14px。",
    brand="bento·os", h1="一屏之内，说清所有事", lede="模块化展示：每格一个重点，不堆信息。",
    css="""
.cards{grid-template-columns:repeat(4,1fr);grid-auto-rows:150px}
.cards .card:nth-child(1){grid-column:span 2;grid-row:span 2}
.cards .card:nth-child(2){grid-column:span 2}
.cards .card:nth-child(3){grid-column:span 2}
.card{display:flex;flex-direction:column;justify-content:flex-end;background:linear-gradient(160deg,#1b1e27,#14161d)}
.card .k{color:#a3e635}
.card:hover{outline:1px solid #a3e63566}
panel,.panel{grid-template-columns:1fr 340px}
""",
)

add(
    id="editorial", name="杂志编辑风", name_en="Editorial", group="classic", era="2015–",
    tokens=dict(bg="#fbf7ef", surface="#fffdf8", ink="#1a1713", muted="#6b6357",
                accent="#8a1f11", line="#ddd4c4", radius="2px", font="Georgia,'Songti SC',serif"),
    features=["大号衬线标题 + 极宽字距的栏目名", "正文限宽 62–68ch，行高 1.8",
              "细发丝线分隔，几乎不用阴影", "首字下沉 / 引文缩进等排印细节"],
    prompt="做一本杂志的专题页：米白纸感底、衬线大标题、栏目名宽字距、发丝线分隔、正文限宽 65ch、首字下沉，只用一种深红做强调，不要阴影和圆角。",
    brand="纪事 · CHRONICLE", h1="当界面开始像一本书", lede="留白、字距与栏宽，决定你读得下去还是读不下去。",
    css="""
.hero h1{font-family:Georgia,'Songti SC',serif;font-weight:400;letter-spacing:-.02em;line-height:1.08}
.hero .lede{font-size:18px;line-height:1.9}
.hero{max-width:820px}
.hero h1::first-letter{font-size:1.1em}
.eyebrow{letter-spacing:.4em;color:#8a1f11;font-size:11px}
.card{border:0;border-top:2px solid #1a1713;border-radius:0;background:transparent;padding:22px 0 0}
.row .btn{background:#1a1713;border-radius:0;padding:12px 22px;letter-spacing:.08em;font-size:13px}
.row .btn.ghost{background:transparent;border:1px solid #1a1713}
.nav{border-bottom:2px solid #1a1713}
.panel{border:0;border-top:1px solid #ddd4c4;border-bottom:1px solid #ddd4c4;border-radius:0;background:transparent}
""",
)

add(
    id="swiss", name="瑞士国际主义", name_en="Swiss / International", group="classic", era="1950–",
    tokens=dict(bg="#ffffff", surface="#ffffff", ink="#111111", muted="#6b6b6b",
                accent="#e2001a", line="#111111", radius="0px", font="'Helvetica Neue',Arial,'PingFang SC',sans-serif"),
    features=["严格网格对齐，左对齐到发指", "无衬线 + 极端字号对比（80px 配 12px）",
              "只用黑、白、一个红", "零圆角零阴影，靠线和留白分区"],
    prompt="用瑞士国际主义排版做页面：纯白底、Helvetica、12 栏网格、标题大到 80px、只用黑与红 #e2001a、零圆角零阴影，大量留白，元素严格左对齐。",
    brand="Grid 12", h1="秩序，就是风格", lede="网格、字号、留白。三件事做到极致，不需要第四件。",
    css="""
body{background:#fff}
.hero h1{font-size:clamp(44px,7vw,88px);font-weight:700;letter-spacing:-.04em;line-height:.98}
.eyebrow{color:#e2001a;letter-spacing:.3em}
.cards{gap:0;border-top:2px solid #111}
.card{border:0;border-right:1px solid #111;border-radius:0;padding:26px 22px}
.card:last-child{border-right:0}
.btn,.btn.ghost{border-radius:0;background:#111;color:#fff;border:0;padding:12px 24px}
.btn.ghost{background:#fff;color:#111;border:2px solid #111}
.nav{border-bottom:2px solid #111}
.panel{border:0;border-top:2px solid #111;border-radius:0;padding:34px 0}
input,select{border-radius:0;border:1px solid #111}
""",
)

add(
    id="terminal", name="终端 / CLI", name_en="Terminal", group="classic", era="1970–",
    tokens=dict(bg="#04120a", surface="#071a10", ink="#54f08a", muted="#2f8f5a",
                accent="#a6ff4d", line="#1d4a30", radius="0px", font="Consolas,'Cascadia Mono',monospace"),
    features=["等宽字体，一切用字符拼", "荧光绿文字 + 极暗绿底，轻微辉光",
              "提示符 $ / > 作为视觉锚点", "分割用 ASCII 线条（----），不用卡片阴影"],
    prompt="做一个终端风格落地页：#04120a 底、等宽字、荧光绿文字带轻微 text-shadow 辉光、提示符 $ 引导、用 -- 和 | 做分割，零圆角，可加 scanline。",
    brand="./atlas", h1="> 用命令行介绍产品", lede="没有按钮，只有提示符。回车即执行。",
    css="""
body{background:#04120a;text-shadow:0 0 6px rgba(84,240,138,.35)}
.hero h1{font-family:inherit;font-weight:400;font-size:clamp(28px,4vw,44px)}
.hero h1::before{content:"$ ";color:#54f08a}
.card,.panel{border:1px dashed #1d4a30;background:#071a10;border-radius:0}
.card .k{color:#2f8f5a}
.btn{background:#0b2a18;color:#a6ff4d;border:1px solid #2f8f5a;border-radius:0;font-family:inherit}
.btn::before{content:"> "}
.btn.ghost{background:transparent;color:#54f08a}
.nav{border-bottom:1px solid #1d4a30}
input,select{background:#04120a;color:#54f08a;border:1px solid #1d4a30;border-radius:0}
.eq{color:#2f8f5a}
""",
)

add(
    id="blueprint", name="蓝图 / 工程制图", name_en="Blueprint", group="classic", era="—",
    tokens=dict(bg="#0d3b63", surface="#0f426d", ink="#dcecf9", muted="#8fb8d6",
                accent="#ffd24a", line="rgba(220,236,249,.35)", radius="0px", font="Consolas,'Cascadia Mono',monospace"),
    features=["青底白线 + 细网格纸背景", "虚线框、尺寸标注线、编号引出线",
              "等宽小字写参数（SCALE 1:2 / UNIT mm）", "零圆角，装饰即信息"],
    prompt="做一张工程蓝图式页面：#0d3b63 底 + 细网格、白线框（可用虚线）、尺寸标注与编号引出线、等宽小字标注参数，零圆角零阴影，强调色用黄。",
    brand="DWG A-104", h1="把界面画成一张图纸", lede="每个区块都有编号、尺寸和出处。",
    css="""
body{background:
  linear-gradient(rgba(220,236,249,.10) 1px,transparent 1px) 0 0/28px 28px,
  linear-gradient(90deg,rgba(220,236,249,.10) 1px,transparent 1px) 0 0/28px 28px,
  #0d3b63}
.card,.panel{border:1px dashed rgba(220,236,249,.55);background:rgba(15,66,109,.6);border-radius:0}
.card .k{color:#ffd24a;letter-spacing:.3em}
.btn{background:#ffd24a;color:#0d3b63;border-radius:0;font-family:inherit;border:1px dashed #ffd24a}
.btn.ghost{background:transparent;color:#dcecf9;border:1px dashed rgba(220,236,249,.55)}
.nav{border-bottom:1px dashed rgba(220,236,249,.55)}
input,select{background:rgba(13,59,99,.8);color:#dcecf9;border:1px dashed rgba(220,236,249,.45);border-radius:0}
""",
)

add(
    id="clay", name="粘土拟态", name_en="Claymorphism", group="classic", era="2022–",
    tokens=dict(bg="#eef1ff", surface="#f7f8ff", ink="#2b3152", muted="#767ea6",
                accent="#7c5cff", line="#dfe3fb", radius="28px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["超大圆角 + 双层阴影（外投影 + 内高光）", "糖果色、低饱和底",
              "元素像软糖，按下会有回弹感", "阴影方向统一（左上高光、右下投影）"],
    prompt="做粘土拟态界面：浅色底、圆角 28px、每个元素用 outer shadow + inset 高光做出软糖感，强调色糖果紫，按下时缩放 0.97 回弹。",
    brand="Clay Studio", h1="界面可以捏一捏", lede="软圆角、内高光、外投影，一切都是软的。",
    css="""
body{background:radial-gradient(80% 60% at 20% 0%,#dfe4ff,#eef1ff 60%,#f6f0ff)}
.card,.panel{background:#f7f8ff;border:0;border-radius:28px;
  box-shadow:14px 14px 30px rgba(120,130,190,.22),-10px -10px 24px rgba(255,255,255,.9),
             inset 2px 2px 6px rgba(255,255,255,.9),inset -3px -3px 8px rgba(150,160,210,.18)}
.btn{border-radius:18px;background:#7c5cff;
  box-shadow:6px 6px 14px rgba(124,92,255,.35),inset 2px 2px 4px rgba(255,255,255,.45)}
.btn:active{transform:scale(.97)}
.btn.ghost{background:#f2f4ff;color:#2b3152;box-shadow:5px 5px 12px rgba(120,130,190,.2),inset 1px 1px 3px #fff}
input,select{background:#f4f6ff;border:0;box-shadow:inset 3px 3px 7px rgba(150,160,210,.28),inset -2px -2px 6px #fff}
""",
)

add(
    id="skeuo", name="拟物主义", name_en="Skeuomorphism", group="classic", era="2007–2013",
    tokens=dict(bg="#3b2f27", surface="#f3ead7", ink="#3a2d22", muted="#7c6a56",
                accent="#b8863b", line="#c9b794", radius="8px", font="Georgia,'Songti SC',serif"),
    features=["皮革 / 木纹 / 金属质感，材质即隐喻", "按钮有凸起 + 高光 + 内阴影",
              "衬线字 + 金色描边标题", "纹理用 CSS 渐变模拟，不引入图片"],
    prompt="做拟物风格界面：深木色背景 + 米色纸质面板、按钮做凸起（渐变 + inset 高光 + 外投影）、金色描边标题，衬线字体，材质靠 CSS 渐变模拟。",
    brand="Ledger & Co.", h1="看得见的手感", lede="每个控件都有厚度、纹理和影子。",
    css="""
body{background:
  repeating-linear-gradient(90deg,rgba(0,0,0,.18) 0 2px,transparent 2px 7px),
  linear-gradient(160deg,#4a3a2e,#2c211a)}
.card,.panel{background:
  repeating-linear-gradient(0deg,rgba(160,140,105,.10) 0 1px,transparent 1px 4px),
  linear-gradient(#f7efdd,#eee2c9);
  border:1px solid #b7a483;border-radius:8px;
  box-shadow:0 2px 0 #fff inset,0 -2px 0 rgba(0,0,0,.12) inset,0 8px 18px rgba(0,0,0,.45)}
.hero h1{font-family:Georgia,serif;color:#f6e7c8;text-shadow:0 1px 0 #000,0 0 22px rgba(184,134,59,.55)}
.hero .lede{color:#d9c7a8}
.eyebrow{color:#b8863b;letter-spacing:.3em}
.btn{border-radius:8px;background:linear-gradient(#e0b968,#b8863b);color:#2c1f12;
  border:1px solid #8a6428;box-shadow:0 2px 0 rgba(255,255,255,.65) inset,0 -3px 0 rgba(0,0,0,.22) inset,0 4px 10px rgba(0,0,0,.45)}
.btn:active{box-shadow:0 -2px 0 rgba(255,255,255,.35) inset,0 2px 6px rgba(0,0,0,.5)}
.btn.ghost{background:linear-gradient(#f3e6cc,#e3d3b4);color:#3a2d22;border:1px solid #c3ad86}
.nav{border-bottom:1px solid rgba(246,231,200,.35)}
.nav .brand,.nav nav a{color:#f2e3c4}
""",
)

add(
    id="y2k", name="Y2K 千禧", name_en="Y2K", group="classic", era="1998–2003",
    tokens=dict(bg="#dbe4ff", surface="#eef2ff", ink="#161a3a", muted="#5a6294",
                accent="#ff3ea5", line="#9aa8e0", radius="10px", font="'Trebuchet MS','PingFang SC',sans-serif"),
    features=["金属 / 镭射渐变 + 星星闪光", "窗口边框：标题栏 + 立体按钮",
              "斜体粗字 + 宽字距", "高饱和粉 / 蓝撞色，允许一点“过度设计”"],
    prompt="做 Y2K 风格页面：镭射渐变背景 + 星星闪光、窗口式卡片（标题栏 + 立体按钮）、斜体粗标题、金属质感文字（background-clip:text），粉蓝撞色。",
    brand="★ starNet", h1="未来是闪闪发光的", lede="镭射、金属、星星。2000 年想象的 2026。",
    css="""
body{background:
  radial-gradient(circle at 20% 20%,#ff9ad522,transparent 45%),
  radial-gradient(circle at 80% 10%,#7de0ff33,transparent 45%),
  linear-gradient(160deg,#dfe7ff,#f4ecff 50%,#e2f6ff)}
.hero h1{font-style:italic;font-weight:800;letter-spacing:.01em;
  background:linear-gradient(100deg,#e11d74,#6d3ce8 38%,#0e8fd6 70%,#e0a200);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  -webkit-text-stroke:1.2px rgba(22,26,58,.35);
  filter:drop-shadow(0 3px 0 rgba(255,255,255,.9));font-size:clamp(36px,6vw,64px)}
.card,.panel{background:#eef2ff;border:2px solid #6f7fd0;border-radius:10px;
  box-shadow:3px 3px 0 #6f7fd0,inset 0 1px 0 #fff}
.card .k{color:#ff3ea5}
.btn{border-radius:8px;background:linear-gradient(#ff8ec6,#ff3ea5);color:#fff;border:1px solid #c31f78;
  box-shadow:2px 2px 0 #c31f78,inset 0 1px 0 rgba(255,255,255,.8);font-style:italic;letter-spacing:.04em}
.btn.ghost{background:linear-gradient(#ffffff,#d7e0ff);color:#161a3a;border:1px solid #6f7fd0;box-shadow:2px 2px 0 #6f7fd0}
.nav{border-bottom:2px solid #6f7fd0}
""",
)

add(
    id="ink", name="水墨", name_en="Ink Wash", group="shift", era="—",
    tokens=dict(bg="#f2ecde", surface="#f7f2e6", ink="#1c1712", muted="#6b6255",
                accent="#b02e22", line="#cfc4ae", radius="2px", font="'Songti SC',SimSun,serif"),
    features=["宣纸底 + 墨色浓淡（不用纯黑）", "细墨线 + 大留白，讲究呼吸",
              "只允许一枚朱红（印章）", "标题可竖排，字距松"],
    prompt="做水墨风页面：宣纸底 #f2ecde、墨色分五阶（不用纯黑）、细线框、大量留白、只用一枚朱红做印章，衬线字，标题竖排可加分。",
    brand="山水间", h1="把留白，当成内容", lede="写字如画画：一笔一停，留白处也是画面。",
    css="""
body{background:
  radial-gradient(120% 90% at 20% 0%,rgba(255,255,255,.55),transparent 60%),
  #f2ecde}
.hero h1{font-family:'Songti SC',SimSun,serif;font-weight:400;letter-spacing:.08em}
.hero{max-width:700px}
.eyebrow{color:#b02e22;letter-spacing:.5em}
.card,.panel{background:transparent;border:1px solid #cfc4ae;border-radius:0}
.card .k{color:#6b6255;letter-spacing:.3em}
.btn{background:#1c1712;border-radius:0;letter-spacing:.12em;font-family:inherit}
.btn.ghost{background:transparent;border:1px solid #1c1712;color:#1c1712}
.nav{border-bottom:1px solid #cfc4ae}
.panel{background:rgba(255,255,255,.35)}
.seal{display:inline-block;background:#b02e22;color:#f2ecde;padding:3px 6px;font-size:11px;letter-spacing:.1em;vertical-align:middle}
input,select{background:transparent;border:1px solid #cfc4ae;border-radius:0}
""",
)

add(
    id="cyberneon", name="赛博霓虹", name_en="Cyber Neon", group="shift", era="—",
    tokens=dict(bg="#06060e", surface="#0d0b1a", ink="#f2f6ff", muted="#7a7fa8",
                accent="#ff2d95", line="#2a2a4a", radius="4px", font="Consolas,'Cascadia Mono',monospace"),
    features=["纯黑底 + 霓虹描边 + 外发光", "粉 / 青双色，绝不混成紫",
              "等宽小字做标签，扫描线/噪点加分", "边框要细，靠辉光而不是填充"],
    prompt="做赛博霓虹界面：近黑底、粉色 #ff2d95 与青色 #2de2ff 霓虹描边 + 外发光、等宽小字标签、细边框、加扫描线与噪点，禁止大面积填充。",
    brand="NEON//OS", h1="夜里发光的界面", lede="靠辉光分层，不靠色块。",
    css="""
body{background:
  radial-gradient(70% 50% at 70% 0%,#2a0b3e,transparent 60%),
  radial-gradient(60% 50% at 20% 90%,#062838,transparent 60%),
  #06060e}
.hero h1{color:#fff;text-shadow:0 0 14px rgba(255,45,149,.75),0 0 40px rgba(255,45,149,.35)}
.eyebrow{color:#2de2ff;text-shadow:0 0 10px rgba(45,226,255,.6)}
.card,.panel{background:rgba(13,11,26,.8);border:1px solid rgba(255,45,149,.45);border-radius:4px;
  box-shadow:0 0 18px rgba(255,45,149,.18),inset 0 0 24px rgba(45,226,255,.06)}
.card .k{color:#2de2ff}
.btn{background:transparent;border:1px solid #ff2d95;color:#ff9ccb;border-radius:4px;
  box-shadow:0 0 14px rgba(255,45,149,.5),inset 0 0 12px rgba(255,45,149,.18);font-family:inherit}
.btn.ghost{border-color:#2de2ff;color:#9fe9f7;box-shadow:0 0 14px rgba(45,226,255,.4)}
.nav{border-bottom:1px solid rgba(255,45,149,.35)}
.input,input,select{background:#0a0814;color:#f2f6ff;border:1px solid rgba(45,226,255,.35);border-radius:4px}
""",
)

add(
    id="artdeco", name="装饰艺术", name_en="Art Deco", group="shift", era="1925–",
    tokens=dict(bg="#101423", surface="#161b2e", ink="#f2e6c8", muted="#a99a74",
                accent="#c9a24a", line="#3a3f58", radius="0px", font="Georgia,'Songti SC',serif"),
    features=["深藏青 + 金，绝不加第三种颜色", "对称构图 + 放射线 + 阶梯纹",
              "细金线描边，全大写宽字距", "零圆角，装饰靠线条不靠图形"],
    prompt="做 Art Deco 页面：深藏青底 + 金色 #c9a24a 细线、对称布局、放射线与阶梯装饰、全大写宽字距衬线字，零圆角，只用两色。",
    brand="LE MÉTRO", h1="对称，即庄重", lede="金线、阶梯、放射。装饰不是多余，是语法。",
    css="""
body{background:
  repeating-conic-gradient(from -90deg at 50% -20%,rgba(201,162,74,.07) 0deg 2deg,transparent 2deg 9deg),
  #101423}
.hero h1{font-family:Georgia,serif;font-weight:400;letter-spacing:.16em;text-transform:uppercase;font-size:clamp(30px,4.6vw,52px);color:#f2e6c8}
.eyebrow{color:#c9a24a;letter-spacing:.6em}
.hero{text-align:center;margin:0 auto;max-width:820px}
.hero .row{justify-content:center}
.card,.panel{background:#161b2e;border:1px solid #c9a24a55;border-radius:0;position:relative}
.card::before,.panel::before{content:"";position:absolute;inset:6px;border:1px solid #c9a24a33;pointer-events:none}
.card .k{color:#c9a24a;letter-spacing:.34em}
.btn{background:#c9a24a;color:#101423;border-radius:0;letter-spacing:.14em;font-family:Georgia,serif}
.btn.ghost{background:transparent;border:1px solid #c9a24a;color:#f2e6c8}
.nav{border-bottom:1px solid #c9a24a55}
""",
)

add(
    id="riso", name="丝网 / 孔版印刷", name_en="Risograph", group="shift", era="—",
    tokens=dict(bg="#f3eddf", surface="#faf6ec", ink="#1a1a1a", muted="#6a6456",
                accent="#ff4f8b", line="#d8d0be", radius="2px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["两色套印错位（multiply 叠加）", "半调网点 + 纸颗粒",
              "高饱和单色 + 黑，不用渐变", "边缘略有毛刺，允许“不精准”"],
    prompt="做孔版印刷风页面：米色纸底、两色套印（粉 #ff4f8b + 青绿 #17a398）用 multiply 叠加并故意错位 2–3px、半调网点、纸颗粒，高饱和平涂。",
    brand="RISO PRESS", h1="印歪一点，才像印的", lede="两种油墨、一道错版、满屏网点。",
    css="""
body{background:
  radial-gradient(rgba(120,100,60,.16) 1px,transparent 1.4px) 0 0/5px 5px,
  #f3eddf}
.hero h1{color:#1a1a1a;text-shadow:3px 3px 0 #ff4f8b,6px 6px 0 #17a39855;font-weight:900}
.eyebrow{color:#ff4f8b}
.card,.panel{background:#faf6ec;border:2px solid #1a1a1a;border-radius:2px;
  box-shadow:4px 4px 0 #ff4f8b}
.card .k{color:#17a398}
.btn{background:#ff4f8b;color:#fff;border:2px solid #1a1a1a;border-radius:2px;box-shadow:3px 3px 0 #1a1a1a}
.btn.ghost{background:#faf6ec;color:#1a1a1a;border:2px solid #1a1a1a;box-shadow:3px 3px 0 #17a398}
.nav{border-bottom:2px solid #1a1a1a}
""",
)

add(
    id="memo", name="手账笔记", name_en="Bullet Journal", group="shift", era="—",
    tokens=dict(bg="#fffdf6", surface="#fffef9", ink="#2a3a52", muted="#7c8698",
                accent="#ffb800", line="#dfe3ea", radius="4px", font="'Kaiti SC',KaiTi,'PingFang SC',sans-serif"),
    features=["方格纸底 + 和纸胶带 + 荧光笔", "手写体标题，重点用马克笔划线",
              "便签纸、回形针、贴纸做点缀", "颜色控制在三种以内"],
    prompt="做手账笔记风页面：方格纸背景、手写标题、荧光笔划线重点、和纸胶带贴角、便签纸块，颜色不超过三种（黄 + 蓝 + 墨）。",
    brand="今日手账", h1="把方法，写在格子里", h1_html='把方法，写在<span>格子</span>里', lede="打勾、划线、贴一张便签。",
    css="""
body{background:
  linear-gradient(rgba(120,150,190,.16) 1px,transparent 1px) 0 0/14px 14px,
  linear-gradient(90deg,rgba(120,150,190,.16) 1px,transparent 1px) 0 0/14px 14px,
  #fffdf6}
.hero h1{font-family:'Kaiti SC',KaiTi,serif;font-weight:400;font-size:clamp(32px,5vw,52px)}
.hero h1 span{background:linear-gradient(transparent 62%,#ffe14d 62%);padding:0 .1em}
.card,.panel{background:#fffef9;border:1px solid #dfe3ea;border-radius:4px;box-shadow:0 6px 18px rgba(80,90,110,.08)}
.card{position:relative}
.card::before{content:"";position:absolute;left:-6px;top:-8px;width:44px;height:16px;background:#ffe9a8;
  transform:rotate(-8deg);opacity:.9}
.card .k{color:#ffb800}
.btn{background:#2a3a52;border-radius:4px;font-family:inherit}
.btn.ghost{background:#fffef9;color:#2a3a52;border:1px solid #dfe3ea}
.nav{border-bottom:1px solid #dfe3ea}
""",
)

add(
    id="chalk", name="黑板粉笔", name_en="Chalkboard", group="shift", era="—",
    tokens=dict(bg="#20302a", surface="#26382f", ink="#eef3ea", muted="#9fb2a6",
                accent="#f2d68a", line="rgba(238,243,234,.28)", radius="2px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["墨绿黑板 + 白色粉笔字，边缘略糊", "划线用手指擦过的痕迹（低透明度）",
              "手写感标题 + 粉笔灰点缀", "黄色粉笔做强调"],
    prompt="做黑板粉笔风格：墨绿底、白色粉笔字（轻微模糊与颗粒）、手写感标题、黄色粉笔强调、擦痕做装饰，不要阴影与渐变。",
    brand="课堂 · 03", h1="把道理，写在黑板上", lede="一条线、两个箭头、三句结论。",
    css="""
body{background:
  radial-gradient(rgba(238,243,234,.07) 1px,transparent 1.5px) 0 0/7px 7px,
  radial-gradient(80% 60% at 40% 20%,#2c4038,#1a2620 80%)}
.hero h1{font-weight:400;letter-spacing:.02em;text-shadow:0 0 1px rgba(255,255,255,.4)}
.hero h1 span{color:#f2d68a}
.card,.panel{background:transparent;border:1px solid rgba(238,243,234,.28);border-radius:2px;box-shadow:none}
.card .k{color:#f2d68a}
.btn{background:#f2d68a;color:#1a2620;border-radius:2px;font-family:inherit}
.btn.ghost{background:transparent;color:#eef3ea;border:1px solid rgba(238,243,234,.5)}
.nav{border-bottom:1px solid rgba(238,243,234,.28)}
.panel{background:rgba(238,243,234,.04)}
input,select{background:rgba(238,243,234,.06);color:#eef3ea;border:1px solid rgba(238,243,234,.3);border-radius:2px}
""",
)

add(
    id="pixel", name="像素 / 8-bit", name_en="Pixel Art", group="shift", era="1985–",
    tokens=dict(bg="#0f0f1b", surface="#1b1b2e", ink="#e8e8ff", muted="#8a8ab0",
                accent="#ffd24a", line="#3a3a5c", radius="0px", font="'Courier New',Consolas,monospace"),
    features=["像素级描边（阶梯阴影，不用 border-radius）", "有限调色板 + 高对比",
              "像素字体或等宽字模拟", "按钮按下有 4px 位移"],
    prompt="做 8-bit 像素风页面：深蓝底、像素描边（用多层 box-shadow 做阶梯）、零圆角、有限调色板（蓝紫 + 黄 + 白）、等宽字、按钮按下位移 4px。",
    brand="PIXEL·QUEST", h1="按像素对齐", lede="没有曲线，只有方块。",
    css="""
body{background:
  linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px) 0 0/16px 16px,
  #0f0f1b}
.hero h1{font-family:'Courier New',monospace;font-weight:700;letter-spacing:.02em;color:#ffd24a;
  text-shadow:4px 4px 0 #3a3a5c}
.eyebrow{color:#8fd6ff;letter-spacing:.3em}
.card,.panel{background:#1b1b2e;border:0;border-radius:0;
  box-shadow:0 0 0 3px #3a3a5c,0 0 0 6px #0f0f1b}
.card .k{color:#ffd24a}
.btn{background:#ffd24a;color:#14142a;border-radius:0;box-shadow:0 4px 0 #b08a00;font-family:inherit;font-weight:700}
.btn:active{transform:translateY(4px);box-shadow:0 0 0 #b08a00}
.btn.ghost{background:#2a2a44;color:#e8e8ff;box-shadow:0 4px 0 #14142a}
.nav{border-bottom:4px solid #3a3a5c}
input,select{background:#14142a;color:#e8e8ff;border:0;box-shadow:0 0 0 3px #3a3a5c;border-radius:0}
""",
)

add(
    id="papercut", name="剪纸", name_en="Paper Cut", group="shift", era="—",
    tokens=dict(bg="#f6ecd8", surface="#fffaf0", ink="#2b1f18", muted="#7a6a58",
                accent="#c8371f", line="#e2d5bd", radius="6px", font="'Songti SC',SimSun,serif"),
    features=["层叠纸片 + 投影做深度", "参差的“撕纸”边缘（clip-path）",
              "暖色纸 + 一抹中国红", "元素之间留缝，像真的叠在一起"],
    prompt="做剪纸层叠风页面：暖色纸底、卡片用 clip-path 做参差边缘、每层加 6–10px 硬投影做厚度、中国红做强调，衬线字。",
    brand="纸间", h1="一层一层，叠出画面", lede="纸有厚度，影子会说话。",
    css="""
body{background:
  radial-gradient(rgba(150,120,70,.14) 1px,transparent 1.4px) 0 0/7px 7px,
  #f6ecd8}
.hero h1{font-family:'Songti SC',SimSun,serif;font-weight:400}
.eyebrow{color:#c8371f;letter-spacing:.4em}
.card,.panel{background:#fffaf0;border:1px solid #e2d5bd;border-radius:6px;
  clip-path:polygon(0 2%,6% 0,24% 2%,46% 0,68% 2%,88% 0,100% 3%,99% 32%,100% 62%,98% 88%,100% 98%,74% 100%,50% 98%,26% 100%,4% 98%,0 96%,1% 66%,0 34%);
  box-shadow:8px 10px 0 rgba(43,31,24,.12)}
.card .k{color:#c8371f}
.btn{background:#c8371f;border-radius:4px;font-family:inherit;box-shadow:4px 4px 0 rgba(43,31,24,.18)}
.btn.ghost{background:#fffaf0;color:#2b1f18;border:1px solid #c8371f;box-shadow:4px 4px 0 rgba(43,31,24,.12)}
.nav{border-bottom:1px solid #e2d5bd}
""",
)

add(
    id="newsprint", name="报纸", name_en="Newsprint", group="shift", era="—",
    tokens=dict(bg="#eee9dc", surface="#f7f2e4", ink="#1b1a17", muted="#5f5a4e",
                accent="#8c1c13", line="#1b1a17", radius="0px", font="Georgia,'Songti SC',serif"),
    features=["报头 + 双线 + 日期栏", "多栏排版，正文两端对齐",
              "黑色粗规则线分区，无卡片阴影", "图片位用半调网点占位"],
    prompt="做报纸风页面：纸灰底、报头 + 双线 + 日期、多栏正文、黑色粗线分区、零圆角零阴影，一张半调网点图片位，深红做强调。",
    brand="每日界面 · DAILY UI", h1="第 42 期：界面也需要排版", lede="把落地页当成一版报纸来排。",
    css="""
body{background:
  radial-gradient(rgba(90,80,50,.10) 1px,transparent 1.3px) 0 0/5px 5px,
  #eee9dc}
.hero{border-bottom:3px double #1b1a17;padding-bottom:26px;max-width:900px}
.hero h1{font-family:Georgia,serif;font-weight:700;line-height:1.05;font-size:clamp(32px,5vw,56px)}
.eyebrow{color:#8c1c13;letter-spacing:.3em;font-size:11px}
.cards{gap:0;border-bottom:3px double #1b1a17;padding-bottom:40px}
.card{border:0;border-right:1px solid #1b1a17;border-radius:0;background:transparent;padding:0 20px}
.card:first-child{padding-left:0}
.card:last-child{border-right:0;padding-right:0}
.card .k{color:#8c1c13;letter-spacing:.24em}
.btn{background:#1b1a17;border-radius:0;font-family:Georgia,serif}
.btn.ghost{background:transparent;border:1px solid #1b1a17;color:#1b1a17}
.nav{border-bottom:3px double #1b1a17}
.panel{border:0;border-top:1px solid #1b1a17;border-radius:0;background:transparent;padding:26px 0}
""",
)

add(
    id="hologram", name="全息 HUD", name_en="Hologram HUD", group="shift", era="—",
    tokens=dict(bg="#03121c", surface="rgba(10,40,56,.55)", ink="#cdf6ff", muted="#6fa8bd",
                accent="#3ce0ff", line="rgba(60,224,255,.32)", radius="2px", font="Consolas,'Cascadia Mono',monospace"),
    features=["青蓝线框 + 虚线弧 + 角标", "半透明面板带内发光，像投影",
              "等宽读数（LAT / ORBIT / SIGNAL）", "背景加光锥与细网格"],
    prompt="做全息 HUD 界面：深青底、线框面板（细边 + 内发光）、虚线圆弧与角标、等宽读数、光锥背景，禁止实色填充与圆角。",
    brand="ORBITAL-9", h1="读取中：目标已锁定", lede="界面是一层投影，随时会消失。",
    css="""
body{background:
  radial-gradient(60% 50% at 50% 0%,rgba(60,224,255,.14),transparent 60%),
  linear-gradient(rgba(60,224,255,.06) 1px,transparent 1px) 0 0/32px 32px,
  #03121c}
.hero h1{color:#cdf6ff;text-shadow:0 0 16px rgba(60,224,255,.55);font-family:inherit;letter-spacing:.04em}
.eyebrow{color:#3ce0ff;letter-spacing:.4em}
.card,.panel{background:rgba(10,40,56,.5);border:1px solid rgba(60,224,255,.32);border-radius:2px;
  box-shadow:inset 0 0 28px rgba(60,224,255,.10)}
.card{position:relative}
.card::after{content:"";position:absolute;right:8px;top:8px;width:10px;height:10px;
  border-top:1px solid #3ce0ff;border-right:1px solid #3ce0ff}
.card .k{color:#3ce0ff;letter-spacing:.3em}
.btn{background:transparent;border:1px solid #3ce0ff;color:#9fe9f7;border-radius:2px;
  box-shadow:inset 0 0 14px rgba(60,224,255,.18),0 0 14px rgba(60,224,255,.25);font-family:inherit}
.btn.ghost{border-color:rgba(60,224,255,.45);color:#6fa8bd;box-shadow:none}
.nav{border-bottom:1px solid rgba(60,224,255,.3)}
input,select{background:rgba(3,18,28,.8);color:#cdf6ff;border:1px solid rgba(60,224,255,.3);border-radius:2px}
""",
)


add(
    id="material", name="Material You", name_en="Material 3", group="classic", era="2021–",
    tokens=dict(bg="#f7f2fa", surface="#f3edf7", ink="#1d1b20", muted="#49454f",
                accent="#6750a4", line="#e8def8", radius="28px", font="Roboto,'PingFang SC',sans-serif"),
    features=["色调化表面：底与卡片同色系，靠 tonal 层次区分", "超大圆角（28px）+ 药丸按钮",
              "主色只出现在填充按钮与标签上", "阴影极浅，靠色块分层"],
    prompt="做 Material You 风格：底色 #f7f2fa，卡片用同色系 tonal 面 #f3edf7、圆角 28px、阴影极浅；按钮为药丸形主色填充；强调色 #6750a4 只用于按钮与标签。",
    brand="Material", h1="颜色会跟着你变", lede="同一套组件，随壁纸换一套色调。",
    cards=[("动态配色", "从壁纸取色", "一张图生成整套色调。"), ("组件", "统一的形状语言", "大圆角、药丸按钮、色调表面。"), ("动效", "有方向的过渡", "元素从哪来，就回哪去。")],
    css="""
.card .k{color:#6750a4;background:#e8def8;border-radius:999px;padding:3px 10px;letter-spacing:.12em}
.btn{border-radius:999px;padding:12px 26px;background:#6750a4}
.btn.ghost{background:#e8def8;color:#1d1b20;border:0}
input,select{border-radius:14px;background:#f3edf7;border:1px solid #cac4d0}
.hero h1{font-weight:500;letter-spacing:-.005em}
""",
)

add(
    id="fluent", name="Fluent 亚克力", name_en="Fluent / Acrylic", group="classic", era="2017–",
    tokens=dict(bg="#f3f2f1", surface="#ffffff", ink="#201f1e", muted="#605e5c",
                accent="#0078d4", line="#e1dfdd", radius="8px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["亚克力材质：半透明白 + 强背景模糊", "4–8px 小圆角，克制的边框",
              "强调色只做按钮与焦点下划线", "层与层之间靠 1px 亮边 + 淡阴影"],
    prompt="做 Fluent 亚克力界面：浅灰底 + 彩色微光背景，面板用半透明白 + backdrop-filter blur(20px)、1px 亮边、8px 圆角，强调色 #0078d4 只用于主按钮。",
    brand="Fluent", h1="一层薄薄的材质", lede="亚克力不是玻璃：它更哑、更贴身。",
    css="""
body{background:linear-gradient(140deg,#eaf4fb,#f3f2f1 42%,#efe9f4)}
.nav{background:rgba(255,255,255,.62);backdrop-filter:blur(20px) saturate(160%);border-bottom:1px solid #e1dfdd}
.card,.panel{background:rgba(255,255,255,.68);backdrop-filter:blur(22px) saturate(150%);
  border:1px solid rgba(255,255,255,.7);border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.btn{border-radius:4px;background:#0078d4;border:1px solid #005a9e}
.btn.ghost{background:rgba(255,255,255,.75);color:#201f1e;border:1px solid #8a8886}
input,select{border-radius:4px;border:1px solid #8a8886}
""",
)

add(
    id="antidesign", name="反设计", name_en="Anti-design", group="classic", era="2016–",
    tokens=dict(bg="#fffdf0", surface="#e8ffe8", ink="#111111", muted="#4a4a3a",
                accent="#ff00aa", line="#111111", radius="0px", font="'PingFang SC',sans-serif"),
    features=["故意冲突：字体混搭、颜色撞车、块面歪斜", "波浪下划线、点状描边、贴纸感",
              "拒绝统一栅格，但信息仍然清楚", "少量即可，整页都乱就变成噪声"],
    prompt="做反设计风：米色底、粉绿撞色、块面轻微旋转 1–2 度、点状描边、波浪下划线、标题用衬线 + 正文无衬线混搭，保留可读性。",
    brand="不要好看", h1="故意，做得很不整齐", lede="规则被打破，但重点还在。",
    css="""
body{background:#fffdf0}
.hero h1{font-family:Georgia,serif;color:#ff00aa;text-decoration:underline wavy #00aaff 3px;transform:rotate(-1.2deg)}
.hero .lede{font-family:'PingFang SC',sans-serif}
.card{background:#e8ffe8;border:2px dotted #ff00aa;border-radius:0;transform:rotate(-1deg)}
.card:nth-child(2){background:#fff0f6;border-color:#00aaff;transform:rotate(1.4deg)}
.card:nth-child(3){background:#fffbe0;border-color:#111;transform:rotate(-.6deg)}
.btn{background:#00ff88;color:#111;border:2px solid #111;border-radius:0;transform:rotate(-2deg);font-weight:800}
.btn.ghost{background:#fff;color:#ff00aa;border:2px dashed #ff00aa}
.nav{border-bottom:2px dotted #111}
""",
)

add(
    id="rawhtml", name="裸 HTML", name_en="Raw HTML", group="classic", era="1993–",
    tokens=dict(bg="#ffffff", surface="#fafafa", ink="#000000", muted="#333333",
                accent="#0000ee", line="#cccccc", radius="0px", font="'Times New Roman',serif"),
    features=["几乎不写样式：默认字体、蓝色下划线链接", "灰色分隔线、系统默认按钮",
              "信息密度高，没有卡片阴影", "关键是“不修饰”的分寸感"],
    prompt="做裸 HTML 风格：白底、Times 衬线默认字、蓝色带下划线链接、1px 灰线分隔、浏览器默认按钮外观、零圆角零阴影，不要任何装饰。",
    brand="首页 · Homepage", h1="这是一个网页", lede="没有设计系统，只有浏览器默认样式。",
    cards=[("关于", "关于本站", "一个人维护，更新不定期。"), ("文章", "全部文章", "按时间倒序排列。"), ("联系", "写信给我", "邮箱在页面底部。")],
    css="""
body{background:#fff;font-family:'Times New Roman',SimSun,serif;font-size:16px;line-height:1.5}
.hero{padding:40px 0 28px}
.hero h1{font-size:clamp(26px,3.4vw,38px);font-weight:700;letter-spacing:0}
.hero .lede{font-size:16px;color:#333;max-width:60ch}
.card{background:#fafafa;border:1px solid #ddd;border-radius:0;box-shadow:none}
.card .k{color:#0000ee;text-decoration:underline;letter-spacing:0;text-transform:none;font-size:12px}
.btn{background:#eee;color:#000;border:2px outset #bbb;border-radius:0;font-family:inherit;font-weight:400;padding:6px 14px}
.btn.ghost{background:#eee;border:2px outset #bbb;color:#000}
.nav{border-bottom:1px solid #ccc}
.nav nav a{color:#0000ee;text-decoration:underline}
.panel{background:#fff;border:1px solid #ddd;border-radius:0}
""",
)

add(
    id="japandi", name="侘寂 × 北欧", name_en="Japandi", group="classic", era="2018–",
    tokens=dict(bg="#f4efe8", surface="#faf6f0", ink="#2f3330", muted="#7b7a70",
                accent="#6b7a5e", line="#e3dcd2", radius="2px", font="'Songti SC',Georgia,serif"),
    features=["米白 + 炭黑 + 一点苔绿，几乎无饱和色", "大留白、1px 发丝线、零阴影",
              "衬线标题 + 无衬线正文，字距松", "材质感来自纸色与亚光，不是纹理图"],
    prompt="做 Japandi 风：米白底、炭黑字、苔绿点缀，1px 发丝线、零阴影、小圆角，衬线标题 + 松字距，大留白。",
    brand="間 · MA", h1="少一点，才看得见", lede="留白不是空，是把注意力让出来。",
    css="""
body{background:#f4efe8}
.hero{max-width:720px;padding:84px 0 60px}
.hero h1{font-family:'Songti SC',Georgia,serif;font-weight:400;letter-spacing:.06em}
.eyebrow{color:#6b7a5e;letter-spacing:.44em}
.card,.panel{background:#faf6f0;border:1px solid #e3dcd2;border-radius:2px;box-shadow:none}
.card .k{color:#6b7a5e;letter-spacing:.3em}
.btn{background:#2f3330;border-radius:0;letter-spacing:.1em;font-weight:500}
.btn.ghost{background:transparent;border:1px solid #2f3330;color:#2f3330}
.nav{border-bottom:1px solid #e3dcd2}
""",
)

add(
    id="vaporwave", name="蒸汽波", name_en="Vaporwave", group="classic", era="2010–",
    tokens=dict(bg="#2b1055", surface="rgba(20,8,40,.55)", ink="#ffe9ff", muted="#c8a8e8",
                accent="#ff77c8", line="rgba(255,119,200,.45)", radius="0px", font="Georgia,'PingFang SC',serif"),
    features=["粉紫渐变 + 网格地平线 + 夕阳圆盘", "标题斜体、双色描边、轻微抖动",
              "半透明深色面板 + 霓虹描边", "允许俗气：这是风格的一部分"],
    prompt="做蒸汽波页面：深紫到粉的渐变、透视网格地平线、斜体标题带粉/青双色偏移描边、半透明深紫面板 + 霓虹边，允许俗气。",
    brand="VAPOR 永远", h1="一切都在褪色", lede="粉、紫、网格，和一段听不清的萨克斯。",
    css="""
body{background:
  linear-gradient(180deg,#2b1055 0%,#4a1d7a 40%,#a83b8f 70%,#ff77c8 100%)}
body::after{content:"";position:fixed;left:-20%;right:-20%;bottom:0;height:30vh;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(255,255,255,.35) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.35) 1px,transparent 1px);
  background-size:64px 64px;transform:perspective(280px) rotateX(62deg);transform-origin:bottom;opacity:.34}
.wrap{position:relative;z-index:1}
.hero h1{font-style:italic;color:#fff;text-shadow:3px 3px 0 #ff2d95,6px 6px 0 #2de2ff}
.hero .lede{color:#ffe9ff}
.card,.panel{background:rgba(20,8,40,.55);border:1px solid rgba(255,119,200,.6);border-radius:0;
  backdrop-filter:blur(6px);box-shadow:0 0 20px rgba(255,45,149,.25)}
.card .k{color:#2de2ff}
.btn{background:#ff2d95;color:#fff;border-radius:0;letter-spacing:.1em;text-transform:uppercase}
.btn.ghost{background:rgba(255,255,255,.08);color:#ffe9ff;border:1px solid #ff77c8}
.nav{border-bottom:1px solid rgba(255,119,200,.45)}
""",
)

add(
    id="mono", name="单色极简", name_en="Monochrome", group="classic", era="—",
    tokens=dict(bg="#ffffff", surface="#ffffff", ink="#111111", muted="#6b6b6b",
                accent="#111111", line="#111111", radius="0px", font="'Helvetica Neue',Arial,sans-serif"),
    features=["只有黑白，靠字号与线条建立层级", "1px 实线分区，零阴影零圆角",
              "大标题 + 小标签，中间没有过渡", "留白是最主要的“颜色”"],
    prompt="做单色极简页：纯白底、纯黑字、1px 实线分区、零圆角零阴影，只用字号/字重/留白建立层级，不使用任何彩色。",
    brand="MONO", h1="没有颜色，也能分层", lede="字号、粗细、间距。三样东西足够。",
    css="""
body{background:#fff}
.hero h1{letter-spacing:-.045em;font-weight:700}
.eyebrow{color:#111;letter-spacing:.3em}
.cards{gap:0;border-top:1px solid #111;border-bottom:1px solid #111}
.card{border:0;border-right:1px solid #111;border-radius:0;background:#fff;padding:26px 20px}
.card:last-child{border-right:0}
.card .k{color:#111}
.btn{background:#111;border-radius:0}
.btn.ghost{background:#fff;color:#111;border:1px solid #111}
.nav{border-bottom:1px solid #111}
""",
)

add(
    id="aurora", name="极光渐变", name_en="Aurora Gradient", group="classic", era="2021–",
    tokens=dict(bg="#080b16", surface="rgba(255,255,255,.05)", ink="#eaf0ff", muted="#9aa6c8",
                accent="#5b6cff", line="rgba(255,255,255,.14)", radius="16px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["深底 + 2–3 团大范围彩色渐变（极光）", "卡片用 5% 白 + 1px 亮边，透出背景",
              "按钮用渐变色而非单色", "渐变要慢、要大、要低饱和"],
    prompt="做极光渐变风：深蓝黑底 + 3 团大半径低饱和渐变（蓝/青/紫）、卡片 5% 白 + 1px 亮边 + 背景模糊、主按钮用双色渐变。",
    brand="Aurora", h1="光在动，界面不动", lede="背景慢慢流，前景保持冷静。",
    css="""
body{background:
  radial-gradient(60% 50% at 18% 0%,rgba(91,108,255,.42),transparent 62%),
  radial-gradient(52% 44% at 82% 8%,rgba(0,212,255,.30),transparent 60%),
  radial-gradient(60% 44% at 58% 100%,rgba(168,85,247,.30),transparent 62%),
  #080b16}
.card,.panel{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);
  backdrop-filter:blur(14px);border-radius:16px;box-shadow:0 20px 50px rgba(0,0,0,.35)}
.card .k{color:#7ee0ff}
.btn{background:linear-gradient(95deg,#5b6cff,#00d4ff);color:#04101f;border:0}
.btn.ghost{background:rgba(255,255,255,.08);color:#eaf0ff;border:1px solid rgba(255,255,255,.22)}
.nav{border-bottom:1px solid rgba(255,255,255,.12)}
input,select{background:rgba(255,255,255,.06);color:#eaf0ff;border:1px solid rgba(255,255,255,.18)}
""",
)

add(
    id="dashboard", name="数据看板", name_en="Analytics Dashboard", group="classic", era="—",
    tokens=dict(bg="#0b0f14", surface="#121821", ink="#e6edf6", muted="#8b98a8",
                accent="#2f9e44", line="#1f2a36", radius="6px", font="'Segoe UI',Consolas,sans-serif"),
    features=["深色底 + 高密度信息，一格一个指标", "数字用等宽、大字号，标签小写大写",
              "涨跌用绿/红，但只占很小面积", "卡片描边 1px，无阴影，像监控面板"],
    prompt="做数据看板：深色底、1px 边框卡片、等宽大数字 + 小标签、涨跌色只用在数字上、密度高但间距统一。",
    brand="OPS / 实时", h1="一切都在被测量", lede="每格一个指标，不要装饰。",
    cards=[("01", "请求 / 秒", "12 480 · 较昨日 +6.2%"), ("02", "P95 延迟", "38 ms · 目标 < 50 ms"), ("03", "错误率", "0.12% · 近 24h 无突增")],
    css="""
body{background:#0b0f14}
.card,.panel{background:#121821;border:1px solid #1f2a36;border-radius:6px;box-shadow:none}
.card .k{color:#4ade80;font-family:Consolas,monospace}
.card h3{font-family:Consolas,monospace;font-size:26px;letter-spacing:-.02em}
.card p{font-size:12.5px}
.btn{background:#1f6feb;border-radius:6px}
.btn.ghost{background:#121821;color:#e6edf6;border:1px solid #1f2a36}
.nav{border-bottom:1px solid #1f2a36}
input,select{background:#0e141c;color:#e6edf6;border:1px solid #1f2a36;border-radius:6px}
.hero{padding:56px 0 40px}
""",
)

add(
    id="docs", name="文档站", name_en="Documentation", group="classic", era="—",
    tokens=dict(bg="#ffffff", surface="#f7f8fa", ink="#111827", muted="#6b7280",
                accent="#2563eb", line="#e5e7eb", radius="6px", font="-apple-system,'Segoe UI','PingFang SC',sans-serif"),
    features=["窄正文栏（≤ 72ch）+ 小标题层级", "侧栏导航感：细线、灰底、当前项高亮",
              "代码块与行内 code 是主角", "克制：圆角小、阴影几乎没有"],
    prompt="做文档站页面：白底、正文限宽 72ch、左侧细线导航、卡片用浅灰底 1px 边、代码块突出、强调色仅用于链接与当前项。",
    brand="Atlas Docs", h1="先读这一页，再动手", lede="文档的第一屏不是营销，是路线图。",
    cards=[("快速开始", "五分钟装好环境", "一条命令初始化，跑通第一个示例。"), ("核心概念", "三个词理解模型", "Token、上下文、工具调用。"), ("API 参考", "全部端点与参数", "含请求示例与错误码说明。")],
    css="""
body{background:#fff}
.hero{max-width:760px;padding:52px 0 36px}
.hero h1{font-size:clamp(28px,3.6vw,40px);letter-spacing:-.02em}
.card{background:#f7f8fa;border:1px solid #e5e7eb;border-radius:6px}
.card .k{color:#2563eb;font-family:ui-monospace,Consolas,monospace;letter-spacing:.04em;text-transform:none}
.btn{background:#111827;border-radius:6px;font-size:14px}
.btn.ghost{background:#fff;color:#111827;border:1px solid #d1d5db}
.nav{border-bottom:1px solid #e5e7eb}
.panel{background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px}
""",
)

add(
    id="luxury", name="奢侈品", name_en="Luxury", group="classic", era="—",
    tokens=dict(bg="#0b0b0b", surface="#111111", ink="#f5f1e8", muted="#a39a86",
                accent="#c8a86a", line="#2a2419", radius="0px", font="Georgia,'Songti SC',serif"),
    features=["近黑底 + 香槟金，绝不加第三色", "全大写宽字距 + 细金线",
              "大图位、极简文案、零圆角", "留白与黑场本身就是奢侈感"],
    prompt="做奢侈品风页面：近黑底 + 香槟金 #c8a86a、全大写宽字距衬线标题、细金线分区、零圆角、极简文案与大量黑场。",
    brand="MAISON", h1="克制，是唯一的奢侈", lede="少说一句，价格就高一档。",
    cards=[("高定", "一针一线", "每件 180 小时，只做一件。"), ("成衣", "克制的廓形", "不加装饰，只改比例。"), ("工坊", "巴黎 · 第六区", "预约制，每次只接待一位。")],
    css="""
body{background:#0b0b0b;color:#f5f1e8}
.hero{max-width:760px;padding:96px 0 64px}
.hero h1{font-family:Georgia,serif;font-weight:400;letter-spacing:.16em;text-transform:uppercase;font-size:clamp(26px,3.8vw,44px)}
.eyebrow{color:#c8a86a;letter-spacing:.6em}
.card,.panel{background:#111;border:1px solid #2a2419;border-radius:0;box-shadow:none}
.card .k{color:#c8a86a;letter-spacing:.4em}
.btn{background:#c8a86a;color:#0b0b0b;border-radius:0;letter-spacing:.16em;text-transform:uppercase;font-size:12px;padding:14px 26px}
.btn.ghost{background:transparent;color:#f5f1e8;border:1px solid #c8a86a}
.nav{border-bottom:1px solid #2a2419}
.nav nav a{color:#a39a86;letter-spacing:.14em}
""",
)

add(
    id="kids", name="儿童 / 亲子", name_en="Playful Kids", group="classic", era="—",
    tokens=dict(bg="#fff6e5", surface="#fffdf7", ink="#2b2b2b", muted="#7a6a58",
                accent="#ff5a5f", line="#ffd166", radius="24px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["高饱和三原色 + 超大字", "厚圆角、粗描边、块状阴影",
              "元素轻微旋转，像贴纸", "形状比文字更重要"],
    prompt="做儿童亲子页：奶油底、三原色点缀、24px 大圆角、3px 彩色描边、卡片轻微旋转像贴纸、按钮圆胖、字号偏大。",
    brand="小小工坊", h1="先玩，再说学", lede="大按钮、大圆角、大颜色。",
    cards=[("01", "动手做", "用纸盒做一辆会跑的车。"), ("02", "一起玩", "两个人合作，十分钟一局。"), ("03", "讲故事", "每晚一个，自己编结局。")],
    css="""
body{background:#fff6e5}
.hero h1{font-size:clamp(36px,6vw,64px);font-weight:800;color:#ff5a5f;letter-spacing:-.01em}
.eyebrow{color:#2a9d8f;letter-spacing:.2em}
.card{background:#fffdf7;border:3px solid #ffd166;border-radius:24px}
.card:nth-child(2){border-color:#8ecae6;transform:rotate(-1deg)}
.card:nth-child(3){border-color:#ffb4a2;transform:rotate(1deg)}
.card .k{color:#ff5a5f;background:#ffe6c8;border-radius:999px;padding:2px 10px}
.btn{background:#ff5a5f;border-radius:999px;font-weight:800;padding:13px 26px;font-size:16px}
.btn.ghost{background:#8ecae6;color:#fff;border:0}
.nav{border-bottom:3px dashed #ffd166}
""",
)

add(
    id="cozy", name="温暖小店", name_en="Cozy Shop", group="classic", era="—",
    tokens=dict(bg="#f6efe6", surface="#fffaf3", ink="#3a2c22", muted="#8a7462",
                accent="#8a5a3b", line="#e8dccb", radius="18px", font="Georgia,'Songti SC',serif"),
    features=["奶油 + 咖啡棕 + 木质暖调", "大圆角、柔和投影、衬线标题",
              "手写感的短句，像店招", "图片位留白，不要密集排版"],
    prompt="做温暖小店页：奶油底、咖啡棕主色、18px 圆角、柔和投影、衬线标题 + 手写感短句、宽松行距。",
    brand="午后 · 咖啡", h1="今天也只做三件事", lede="煮一杯、擦一遍桌子、等一个人。",
    css="""
body{background:#f6efe6}
.hero h1{font-family:Georgia,'Songti SC',serif;font-weight:400;line-height:1.25}
.card,.panel{background:#fffaf3;border:1px solid #e8dccb;border-radius:18px;box-shadow:0 10px 24px rgba(120,90,60,.08)}
.card .k{color:#8a5a3b}
.btn{background:#8a5a3b;border-radius:999px;padding:12px 24px}
.btn.ghost{background:#fffaf3;color:#3a2c22;border:1px solid #d9c8b2}
.nav{border-bottom:1px solid #e8dccb}
""",
)

add(
    id="techblue", name="企业科技蓝", name_en="Enterprise SaaS", group="classic", era="2008–",
    tokens=dict(bg="#ffffff", surface="#ffffff", ink="#0b1b3a", muted="#5a6b88",
                accent="#2f6ad8", line="#e6ebf5", radius="12px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["白底 + 蓝，最“安全”的企业观感", "卡片浅边框 + 轻投影，12px 圆角",
              "标题左对齐、正文两行以内", "蓝色渐变按钮 + 次级描边按钮"],
    prompt="做企业 SaaS 落地页：白底、深蓝字、12px 圆角卡片 + 浅边框轻投影、蓝色渐变主按钮、稳重的字号阶梯。",
    brand="Nexus Cloud", h1="让流程自己跑起来", lede="把审批、对账、报表交给一套系统。",
    css="""
body{background:#fff}
.hero h1{color:#0b1b3a;letter-spacing:-.02em}
.card{border:1px solid #e6ebf5;border-radius:12px;box-shadow:0 8px 24px rgba(20,60,140,.06)}
.card .k{color:#2f6ad8}
.btn{background:linear-gradient(180deg,#3d7ae8,#1d4ed8);border-radius:8px;box-shadow:0 4px 12px rgba(29,78,216,.25)}
.btn.ghost{background:#fff;color:#1d4ed8;border:1px solid #c7d7f5}
.nav{border-bottom:1px solid #e6ebf5}
.panel{border:1px solid #e6ebf5;box-shadow:0 8px 24px rgba(20,60,140,.06)}
""",
)

add(
    id="saasgrad", name="SaaS 渐变", name_en="SaaS Gradient", group="classic", era="2020–",
    tokens=dict(bg="#0b0716", surface="rgba(255,255,255,.06)", ink="#f5f3ff", muted="#b4a8d4",
                accent="#8b5cf6", line="rgba(167,139,250,.32)", radius="16px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["紫粉渐变光晕 + 深底", "渐变文字标题、发光按钮",
              "悬浮卡片轻微倾斜/重叠", "一句话价值主张 + 一个 CTA"],
    prompt="做 SaaS 渐变风：深紫黑底 + 顶部紫色光晕、渐变文字标题、发光渐变按钮、半透明卡片带紫边，一句话主张。",
    brand="Orbit", h1="把增长，画成一条曲线", lede="从第一天起就能看见转化。",
    css="""
body{background:
  radial-gradient(70% 55% at 50% 0%,rgba(124,58,237,.35),transparent 62%),
  radial-gradient(40% 30% at 80% 30%,rgba(236,72,153,.18),transparent 60%),
  #0b0716}
.hero h1{background:linear-gradient(95deg,#ffffff,#c4b5fd);-webkit-background-clip:text;background-clip:text;color:transparent}
.card,.panel{background:rgba(255,255,255,.06);border:1px solid rgba(167,139,250,.32);border-radius:16px;
  backdrop-filter:blur(12px);box-shadow:0 24px 60px rgba(76,29,149,.28)}
.card .k{color:#c4b5fd}
.btn{background:linear-gradient(95deg,#8b5cf6,#ec4899);box-shadow:0 10px 30px rgba(139,92,246,.4);border:0}
.btn.ghost{background:rgba(255,255,255,.07);color:#f5f3ff;border:1px solid rgba(167,139,250,.4)}
.nav{border-bottom:1px solid rgba(167,139,250,.22)}
input,select{background:rgba(255,255,255,.06);color:#f5f3ff;border:1px solid rgba(167,139,250,.32)}
""",
)

add(
    id="neumorph", name="新拟物软 UI", name_en="Neumorphism", group="classic", era="2019–",
    tokens=dict(bg="#e8ecf3", surface="#e8ecf3", ink="#3b4252", muted="#7b8296",
                accent="#5b6cff", line="#d4d9e3", radius="16px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["同色双阴影：左上高光、右下投影", "元素与背景同色，靠光影浮起",
              "低对比、低饱和，容易看不清", "按钮按下改为 inset 阴影"],
    prompt="做新拟物软 UI：浅灰蓝底、元素与底同色、左上白高光 + 右下灰投影、16px 圆角、按下变内阴影，保持低对比但可读。",
    brand="Soft UI", h1="从背景里浮起来", lede="没有边框，只有光。",
    css="""
body{background:#e8ecf3}
.card,.panel{background:#e8ecf3;border:0;border-radius:16px;
  box-shadow:9px 9px 20px #c6cbd6,-9px -9px 20px #ffffff}
.card .k{color:#5b6cff}
.btn{background:#e8ecf3;color:#3b4252;border:0;
  box-shadow:5px 5px 12px #c6cbd6,-5px -5px 12px #ffffff}
.btn:active{box-shadow:inset 4px 4px 9px #c6cbd6,inset -4px -4px 9px #ffffff;transform:none}
.btn.ghost{background:#e8ecf3;color:#5b6cff}
.nav{border-bottom:1px solid #dde2ea}
input,select{background:#e8ecf3;border:0;box-shadow:inset 3px 3px 8px #c6cbd6,inset -3px -3px 8px #ffffff}
""",
)

add(
    id="chinesemodern", name="新中式", name_en="Modern Chinese", group="shift", era="—",
    tokens=dict(bg="#f7f4ee", surface="#fffdf8", ink="#221c17", muted="#6f6558",
                accent="#b02e22", line="#e0d8c8", radius="0px", font="'Songti SC','SimSun',serif"),
    features=["留白 + 细线 + 一抹朱红边条", "宋体标题、松字距，横排为主",
              "卡片直角、无阴影，左侧一条朱红竖线", "克制：不加纹理、不做水墨晕染"],
    prompt="做新中式现代页面：米白底、宋体标题松字距、卡片直角无阴影、左侧 3px 朱红竖线、细边框、大量留白。",
    brand="观照", h1="把话说短，把留白留长", lede="少一句解释，多一分体面。",
    css="""
body{background:#f7f4ee}
.hero h1{font-family:'Songti SC',SimSun,serif;font-weight:400;letter-spacing:.1em}
.eyebrow{color:#b02e22;letter-spacing:.52em}
.card,.panel{background:#fffdf8;border:1px solid #e0d8c8;border-radius:0;box-shadow:none;position:relative}
.card::before,.panel::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:#b02e22}
.card .k{color:#b02e22;letter-spacing:.3em}
.btn{background:#b02e22;border-radius:0;letter-spacing:.14em;font-family:inherit}
.btn.ghost{background:transparent;color:#221c17;border:1px solid #221c17}
.nav{border-bottom:1px solid #e0d8c8}
""",
)

add(
    id="gothic", name="哥特暗黑", name_en="Gothic", group="shift", era="—",
    tokens=dict(bg="#080509", surface="#14081c", ink="#e8dcff", muted="#9a86b8",
                accent="#a855f7", line="#4c2a63", radius="0px", font="Georgia,'Songti SC',serif"),
    features=["近黑紫底 + 烛光式紫色辉光", "衬线大写 + 极宽字距，零圆角",
              "细边框 + 四角小装饰", "克制用色：不加第三种颜色"],
    prompt="做哥特暗黑页：近黑底 + 紫色径向辉光、衬线大写宽字距标题、1px 暗紫边框、零圆角、四角小装饰，只用紫与灰白。",
    brand="NOCTURNE", h1="在暗处，字才发光", lede="教堂、烛火、和一句低语。",
    css="""
body{background:radial-gradient(60% 50% at 50% 0%,#2a1038,#080509 72%)}
.hero h1{font-family:Georgia,serif;letter-spacing:.12em;text-transform:uppercase;color:#e8dcff;
  text-shadow:0 0 24px rgba(168,85,247,.45)}
.eyebrow{color:#a855f7;letter-spacing:.5em}
.card,.panel{background:rgba(20,8,28,.75);border:1px solid #4c2a63;border-radius:0;position:relative;
  box-shadow:inset 0 0 40px rgba(76,42,99,.35)}
.card::before{content:"✦";position:absolute;right:10px;top:6px;color:#6b3d8a;font-size:12px}
.card .k{color:#a855f7;letter-spacing:.34em}
.btn{background:#6b21a8;border-radius:0;letter-spacing:.14em;text-transform:uppercase;font-size:12px;padding:13px 24px}
.btn.ghost{background:transparent;color:#c8b0e8;border:1px solid #4c2a63}
.nav{border-bottom:1px solid #4c2a63}
""",
)

add(
    id="ascii", name="ASCII 文本界面", name_en="ASCII / TUI", group="shift", era="—",
    tokens=dict(bg="#000000", surface="#020a02", ink="#b8ffb8", muted="#4a8a4a",
                accent="#4ade80", line="#2a5a2a", radius="0px", font="Consolas,'Cascadia Mono',monospace"),
    features=["一切用等宽字符与虚线框表达", "荧光绿字 + 纯黑底，方括号做标签",
              "分割线用 ---- 而不是边框", "像 80 年代的终端程序"],
    prompt="做 ASCII 文本界面：纯黑底、荧光绿等宽字、虚线框、方括号标签、用 ---- 做分割，零圆角零渐变。",
    brand="+-- atlas.tui --+", h1="文本，就是界面", lede="没有圆角，只有字符。",
    css="""
body{background:#000;color:#b8ffb8;text-shadow:0 0 6px rgba(74,222,128,.4)}
.hero h1{font-family:inherit;font-weight:400;color:#4ade80;font-size:clamp(26px,3.6vw,40px)}
.hero h1::before{content:"> "}
.hero .lede{color:#4a8a4a}
.card,.panel{border:1px dashed #2a5a2a;border-radius:0;background:#020a02}
.card .k{color:#4ade80}
.card .k::before{content:"[ ";}
.card .k::after{content:" ]"}
.btn{background:#04160a;color:#4ade80;border:1px solid #2a5a2a;border-radius:0;font-family:inherit}
.btn::before{content:"[";}
.btn::after{content:"]"}
.btn.ghost{background:transparent;color:#4a8a4a}
.nav{border-bottom:1px dashed #2a5a2a}
input,select{background:#000;color:#b8ffb8;border:1px dashed #2a5a2a;border-radius:0}
""",
)

add(
    id="zine", name="复印小志", name_en="Photocopy Zine", group="shift", era="—",
    tokens=dict(bg="#e9e7e2", surface="#ffffff", ink="#111111", muted="#5a5a55",
                accent="#111111", line="#111111", radius="0px", font="'Arial Black','PingFang SC',sans-serif"),
    features=["黑白复印质感 + 网点噪点", "剪贴式粗标题、块状硬阴影",
              "纸片轻微旋转，边缘参差", "只有黑与纸白，靠字号冲撞"],
    prompt="做复印小志风：灰纸底、纯黑白、网点噪点、剪贴式超粗标题、卡片 2px 黑边 + 4px 硬阴影、轻微旋转。",
    brand="ZINE / 第 3 期", h1="复印出来的态度", lede="剪、贴、复印，然后重复。",
    css="""
body{background:
  radial-gradient(rgba(0,0,0,.12) 1px,transparent 1.4px) 0 0/5px 5px,
  #e9e7e2}
.hero h1{font-family:'Arial Black','PingFang SC',sans-serif;font-weight:900;text-transform:uppercase;
  letter-spacing:-.03em;transform:rotate(-1deg)}
.eyebrow{color:#111;letter-spacing:.3em}
.card,.panel{background:#fff;border:2px solid #111;border-radius:0;box-shadow:5px 5px 0 #111;transform:rotate(-.6deg)}
.card:nth-child(2){transform:rotate(.9deg)}
.card .k{color:#111;letter-spacing:.24em}
.btn{background:#111;color:#fff;border-radius:0;text-transform:uppercase;letter-spacing:.12em;font-weight:800}
.btn.ghost{background:#fff;color:#111;border:2px solid #111}
.nav{border-bottom:2px solid #111}
""",
)

# ================================================================ 第二批：8 条新风格

add(
    id="corporatememphis", name="企业孟菲斯", name_en="Corporate Memphis", group="classic", era="2019–",
    tokens=dict(bg="#ffffff", surface="#f4f5ff", ink="#1b1c26", muted="#6c7186",
                accent="#4a5ee5", line="#e6e8f5", radius="32px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["扁平矢量色块，无描边无渐变", "超大圆角（24–32px）与圆润的胶囊按钮",
              "蓝紫主色 + 珊瑚 / 薄荷两枚粉彩辅色", "人物肢体被几何化、比例夸张"],
    prompt="做 Corporate Memphis 风格：白底、扁平色块无描边、32px 大圆角、主色 #4a5ee5 配珊瑚 #ff6b5b 与薄荷 #7fd6c2、装饰只用圆与半圆，禁止渐变与阴影。",
    brand="Allegro", h1="把复杂，画成几块颜色", lede="扁平、圆润、友好——2019 年之后企业插画的共同语言。",
    css="""
body{background:
  radial-gradient(circle at 90% 10%,#ffd9d4 0 92px,transparent 93px),
  radial-gradient(circle at 97% 30%,#c9f0e7 0 54px,transparent 55px),
  radial-gradient(circle at 6% 96%,#dfe2ff 0 120px,transparent 121px),
  #fff}
.hero h1{font-weight:800;letter-spacing:-.025em}
.card,.panel{background:#f4f5ff;border:0;border-radius:32px;box-shadow:none}
.card .k{color:#4a5ee5;letter-spacing:.16em}
.btn{border-radius:999px;padding:12px 26px;background:#4a5ee5}
.btn.ghost{background:#eef0ff;color:#4a5ee5;border:0}
.nav{border-bottom:0}
""",
)

add(
    id="scandi", name="北欧 Scandi", name_en="Scandi", group="classic", era="2010–",
    tokens=dict(bg="#f6f4ef", surface="#ffffff", ink="#2b2a26", muted="#7b786f",
                accent="#7c8b6b", line="#e6e2d8", radius="6px", font="'Segoe UI','PingFang SC',sans-serif"),
    features=["米白 + 浅木 + 一点苔绿", "1px 细边、几乎无阴影，靠空隙分区",
              "字号偏小、行高 1.8，留白占一半", "像家具目录：物品少、间距大"],
    prompt="做北欧 Scandi 风：米白底、苔绿点缀、1px 细边、6px 小圆角、无阴影、字号偏小行高 1.8、大留白。",
    brand="NORR", h1="少，但要耐用", lede="不是极简秀，是日常里的顺手。",
    css="""
body{background:#f6f4ef}
.hero{max-width:680px}
.hero h1{font-weight:500;font-size:clamp(30px,4vw,46px);letter-spacing:-.015em;line-height:1.2}
.hero .lede{line-height:1.85}
.eyebrow{color:#7c8b6b;letter-spacing:.4em}
.card,.panel{background:#fff;border:1px solid #e6e2d8;border-radius:6px;box-shadow:none}
.card .k{color:#7c8b6b;letter-spacing:.24em}
.btn{background:#2b2a26;border-radius:4px;font-weight:500}
.btn.ghost{background:#fff;border:1px solid #cfcabd;color:#2b2a26}
.nav{border-bottom:1px solid #e6e2d8}
""",
)

add(
    id="amberterminal", name="琥珀终端", name_en="Amber Terminal", group="shift", era="1980–",
    tokens=dict(bg="#0a0700", surface="#140d00", ink="#ffb000", muted="#8a5f00",
                accent="#ffd479", line="#3a2600", radius="0px", font="Consolas,'Cascadia Mono',monospace"),
    features=["单色琥珀屏：黄字黑底，只有一种颜色", "等宽字体 + 轻微辉光与扫描线",
              "装饰用 ASCII 方框与刻度，不用图形", "亮度分层，不靠色相区分层级"],
    prompt="做琥珀终端风：黑底、#ffb000 单色等宽字、轻微发光与扫描线、ASCII 方框分隔、零圆角，不用第二种颜色。",
    brand="amber@tty1", h1="一块琥珀色的屏", lede="1983 年的显示器，只有一种颜色。",
    css="""
body{background:#0a0700;color:#ffb000;text-shadow:0 0 8px rgba(255,176,0,.45)}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:9;opacity:.45;
  background:repeating-linear-gradient(transparent 0 2px,rgba(0,0,0,.55) 2px 4px)}
.hero h1{font-family:inherit;font-weight:400;color:#ffd479;font-size:clamp(26px,3.6vw,42px)}
.hero h1::before{content:"> "}
.hero .lede{color:#8a5f00}
.eyebrow{color:#8a5f00;letter-spacing:.4em}
.card,.panel{background:#140d00;border:1px solid #3a2600;border-radius:0;box-shadow:none}
.card .k{color:#ffd479}
.btn{background:#2a1c00;color:#ffd479;border:1px solid #8a5f00;border-radius:0;font-family:inherit}
.btn.ghost{background:transparent;color:#ffb000;border:1px dashed #3a2600}
.nav{border-bottom:1px solid #3a2600}
input,select{background:#0a0700;color:#ffb000;border:1px solid #3a2600;border-radius:0}
""",
)

add(
    id="posterswiss", name="瑞士海报", name_en="Poster Swiss", group="classic", era="1955–",
    tokens=dict(bg="#f2f0e9", surface="#f2f0e9", ink="#111111", muted="#5c5c5c",
                accent="#ff3b00", line="#111111", radius="0px", font="'Helvetica Neue',Arial,'PingFang SC',sans-serif"),
    features=["海报比例：标题占满上半屏", "零圆角、零卡片，靠字块与粗线分区",
              "只有一个荧光橙做强调", "文字可以溢出、旋转、被裁切"],
    prompt="做瑞士海报风：米白底、Helvetica 超粗标题（96px 以上）、荧光橙 #ff3b00 色块、零圆角零阴影、文字可裁切，只用字块分区。",
    brand="PLAKAT 07", h1="字要大到不用解释", lede="海报的第一原则：隔着十米也读得出来。",
    css="""
body{background:#f2f0e9;overflow-x:hidden}
.hero{max-width:none;padding:56px 0 36px}
.hero h1{font-size:clamp(46px,9vw,104px);font-weight:800;line-height:.88;letter-spacing:-.05em;text-transform:uppercase;max-width:12ch}
.hero .lede{font-size:18px;color:#111;max-width:46ch;border-left:7px solid #ff3b00;padding-left:14px;margin-top:24px}
.eyebrow{color:#ff3b00;letter-spacing:.42em}
.cards{gap:0;border-top:4px solid #111;border-bottom:4px solid #111;padding-bottom:56px}
.card{border:0;border-right:1px solid #111;border-radius:0;background:transparent;padding:24px 20px;box-shadow:none}
.card:last-child{border-right:0}
.card .k{color:#ff3b00}
.btn,.btn.ghost{background:#111;color:#f2f0e9;border:0;border-radius:0;font-weight:800;
  text-transform:uppercase;letter-spacing:.1em;font-size:12px;padding:14px 24px}
.btn.ghost{background:#ff3b00;color:#111}
.nav{border-bottom:4px solid #111}
.panel{border:0;border-top:4px solid #111;border-radius:0;background:transparent}
""",
)

add(
    id="darkeditorial", name="暗色编辑风", name_en="Dark Editorial", group="classic", era="2018–",
    tokens=dict(bg="#0e0e10", surface="#16161a", ink="#f0eee9", muted="#8b8b93",
                accent="#d8ff3e", line="#2a2a30", radius="0px", font="Georgia,'Songti SC',serif"),
    features=["近黑纸面 + 大号衬线标题", "荧光黄绿只占极小面积（标签、链接）",
              "1px 发丝线分区，无卡片阴影", "正文窄栏、行高松，像夜读版"],
    prompt="做暗色编辑风：近黑底、大号衬线标题、1px 细线分区、正文窄栏行高 1.85、荧光黄绿仅用于标签与链接，零圆角零阴影。",
    brand="NIGHT DESK", h1="夜里写的东西，白天再看", lede="暗底不是为了酷，是为了不刺眼。",
    css="""
body{background:#0e0e10}
.hero{max-width:820px}
.hero h1{font-family:Georgia,serif;font-weight:400;font-size:clamp(34px,5vw,60px);line-height:1.1;letter-spacing:-.02em}
.hero .lede{font-size:18px;line-height:1.85;color:#b9b7b1}
.eyebrow{color:#d8ff3e;letter-spacing:.4em}
.card,.panel{background:transparent;border:0;border-top:1px solid #2a2a30;border-radius:0;padding:22px 0 0;box-shadow:none}
.card .k{color:#8b8b93;letter-spacing:.3em}
.btn{background:#f0eee9;color:#0e0e10;border-radius:0;letter-spacing:.06em}
.btn.ghost{background:transparent;color:#f0eee9;border:1px solid #2a2a30}
.nav{border-bottom:1px solid #2a2a30}
.panel{border-bottom:1px solid #2a2a30}
input,select{background:#16161a;color:#f0eee9;border:1px solid #2a2a30;border-radius:0}
""",
)

add(
    id="retroweb", name="Web 2.0 玻璃", name_en="Retro Web 2.0", group="classic", era="2005–2010",
    tokens=dict(bg="#dfe7f5", surface="#ffffff", ink="#1e2a44", muted="#5b6a88",
                accent="#2b6cb0", line="#b9c6dd", radius="8px", font="'Trebuchet MS','PingFang SC',sans-serif"),
    features=["玻璃质感的渐变按钮与光泽标题栏", "1px 浅蓝边 + 内侧 1px 白高光",
              "小字号 NEW / BETA 徽章做点缀", "阴影是柔的——这是 2006 年的投影"],
    prompt="做 Web 2.0 风：浅蓝灰底、白色 8px 圆角卡片 + 1px 浅边、按钮用顶部高光的蓝渐变 + 内白边、加 NEW 徽章。",
    brand="webTwo", h1="光泽、渐变、和一枚 NEW 徽章", lede="那一年，所有按钮都像果冻。",
    css="""
body{background:linear-gradient(#eaf0fa,#dbe4f3 42%,#e7edf8)}
.hero h1{color:#1e2a44;text-shadow:0 1px 0 #fff;font-weight:700}
.eyebrow{color:#2b6cb0}
.eyebrow::after{content:" NEW";background:#ff8a00;color:#fff;border-radius:3px;padding:1px 4px;
  margin-left:6px;font-size:9px;letter-spacing:.06em;vertical-align:middle}
.card,.panel{background:#fff;border:1px solid #b9c6dd;border-radius:8px;
  box-shadow:0 2px 6px rgba(40,70,120,.14),inset 0 1px 0 #fff}
.btn{border-radius:6px;background:linear-gradient(#5b9bd5,#2b6cb0);border:1px solid #1f5290;color:#fff;
  text-shadow:0 -1px 0 rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.5)}
.btn.ghost{background:linear-gradient(#ffffff,#e9eff8);color:#2b6cb0;border:1px solid #b9c6dd;text-shadow:none}
.nav{background:linear-gradient(#fff,#eef3fb);border:1px solid #b9c6dd;border-radius:8px;padding:12px 16px;margin-top:14px}
input,select{border-radius:5px;border:1px solid #b9c6dd;box-shadow:inset 0 1px 2px rgba(40,70,120,.12)}
""",
)

add(
    id="zenminimal", name="禅意极简", name_en="Zen Minimal", group="shift", era="—",
    tokens=dict(bg="#faf9f6", surface="#faf9f6", ink="#22201d", muted="#8d887e",
                accent="#22201d", line="#e7e3da", radius="0px", font="'Songti SC',Georgia,serif"),
    features=["一张纸、一条竖线、一句话", "字号极小 + 字距极大，靠空白呼吸",
              "零阴影零色块，边界只靠空隙", "留白占七成，内容是注脚"],
    prompt="做禅意极简：米白纸底、一条 1px 竖线、极小字号 + 极大字距、零阴影零色块、只用黑白两色，留白占 70%。",
    brand="無 · MU", h1="空白", lede="句子越短，空白越大。",
    css="""
body{background:#faf9f6}
.hero{max-width:560px;padding:110px 0 88px 34px;border-left:1px solid #d9d4c8}
.hero h1{font-family:'Songti SC',Georgia,serif;font-weight:400;font-size:clamp(28px,4vw,44px);letter-spacing:.3em;line-height:1.7}
.hero .lede{font-size:13.5px;letter-spacing:.08em;line-height:2.3;color:#8d887e;max-width:32ch}
.eyebrow{color:#8d887e;letter-spacing:.6em;font-size:10.5px}
.cards{gap:44px;padding-bottom:92px}
.card{background:transparent;border:0;border-top:1px solid #e7e3da;border-radius:0;padding:16px 0 0;box-shadow:none}
.card h3{font-size:14px;font-weight:400;letter-spacing:.1em}
.card p{font-size:12.5px;line-height:2;letter-spacing:.03em}
.card .k{color:#8d887e;letter-spacing:.32em;font-size:10px}
.btn{background:#22201d;border-radius:0;font-size:12px;letter-spacing:.18em;padding:11px 22px}
.btn.ghost{background:transparent;border:1px solid #d9d4c8;color:#22201d}
.nav{border-bottom:1px solid #e7e3da}
""",
)

add(
    id="cyberhud2", name="战术 HUD 2", name_en="Cyber HUD 2", group="shift", era="2024–",
    tokens=dict(bg="#08090a", surface="rgba(20,22,24,.72)", ink="#e9f2e6", muted="#7d8a80",
                accent="#c8ff2e", line="rgba(200,255,46,.28)", radius="0px", font="'Segoe UI',Consolas,sans-serif"),
    features=["斜切角 + 四角括号，全部直角", "荧光黄绿描边 + 刻度网格，无第三种色",
              "边缘铺数据带（SYNC / LOCK / SIG）", "信息密度优先，装饰只是刻度"],
    prompt="做战术 HUD 2.0：近黑底、荧光黄绿 #c8ff2e 描边与刻度网格、clip-path 斜切角、四角括号、等宽读数，零圆角，不加第三种颜色。",
    brand="TAC//OPS", h1="目标：可读，且快", lede="信息密度优先，装饰只是刻度。",
    css="""
body{background:
  linear-gradient(rgba(200,255,46,.045) 1px,transparent 1px) 0 0/24px 24px,
  linear-gradient(90deg,rgba(200,255,46,.045) 1px,transparent 1px) 0 0/24px 24px,
  radial-gradient(70% 50% at 50% -10%,rgba(200,255,46,.10),transparent 60%),
  #08090a}
.hero h1{text-transform:uppercase;letter-spacing:.05em;font-weight:800;font-size:clamp(28px,4.2vw,48px)}
.hero h1::before{content:"// ";color:#c8ff2e}
.eyebrow{color:#c8ff2e;letter-spacing:.5em}
.eyebrow::before{content:"[ "}
.eyebrow::after{content:" ]"}
.card,.panel{background:rgba(20,22,24,.72);border:1px solid rgba(200,255,46,.28);border-radius:0;
  clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,14px 100%,0 calc(100% - 14px))}
.card .k{color:#c8ff2e;letter-spacing:.3em}
.btn{background:#c8ff2e;color:#08120a;border-radius:0;letter-spacing:.1em;text-transform:uppercase;font-weight:800;
  clip-path:polygon(0 0,calc(100% - 10px) 0,100% 10px,100% 100%,10px 100%,0 calc(100% - 10px))}
.btn.ghost{background:transparent;color:#e9f2e6;border:1px solid rgba(200,255,46,.4)}
.nav{border-bottom:1px solid rgba(200,255,46,.28)}
input,select{background:#0d0f10;color:#e9f2e6;border:1px solid rgba(200,255,46,.28);border-radius:0}
""",
)

# ================================================================ 元信息：来源 / 何时别用
# sources 只写流派与代表作品，不写具体站点实现；avoid 是「什么时候不要用」。
META = {
    "glass": dict(
        sources=["Frosted glass 材质：随 macOS Big Sur / iOS 14（2020）的视觉语言普及",
                 "“Glassmorphism” 一词由 Michal Malewicz 于 2020 年提出"],
        avoid="背景没有彩色光斑时不成立——纯色底上的玻璃面板只会变成一层灰雾。"),
    "neubrutalism": dict(
        sources=["Web Brutalism 的回潮，2021 年后由 Gumroad、Gather 等产品带火",
                 "新粗野主义（Neubrutalism）设计标签"],
        avoid="信息密集的后台或表单页：粗边与硬阴影会把密度压成噪声。"),
    "bento": dict(
        sources=["Bento 便当盒布局，2022 年随 Apple 产品页回归",
                 "日式便当的分格逻辑 + Bento Grid 设计体系"],
        avoid="层级超过两层的内容：大小交错的格子会让人找不到入口。"),
    "editorial": dict(
        sources=["杂志与报纸排印传统（Editorial Design）", "衬线长文版式与首字下沉、引文缩进"],
        avoid="需要快速扫读的数据页：衬线 + 宽字距会拖慢速度。"),
    "swiss": dict(
        sources=["瑞士国际主义平面设计（1950s，Josef Müller-Brockmann 等）",
                 "Helvetica 与 12 栏网格体系"],
        avoid="儿童或娱乐产品：秩序感会显得冷。"),
    "terminal": dict(
        sources=["命令行界面（CLI）与 TUI 传统", "CRT 终端与 phosphor 荧光屏"],
        avoid="面向普通消费者的注册与支付流程：等宽字与提示符会抬高心理门槛。"),
    "blueprint": dict(
        sources=["工程制图与蓝图晒图工艺", "技术示意图的标注、编号与尺寸线体系"],
        avoid="需要情绪表达的页面：蓝图的每一处装饰都是参数。"),
    "clay": dict(
        sources=["Claymorphism（2022 年在 Dribbble 兴起）", "糖果色软体 3D 插画"],
        avoid="企业后台表格：双层阴影会让密集行距显脏。"),
    "skeuo": dict(
        sources=["1990s–2010s 拟物界面（皮革、木纹、金属）", "iOS 6 及更早的视觉语言"],
        avoid="需要多主题或暗色适配的场景：材质隐喻一旦被压平成色块就失真。"),
    "y2k": dict(
        sources=["Y2K 千禧美学（1998–2003）", "金属镭射、星星闪光、Windows 98 窗口形态"],
        avoid="金融或医疗信息页：可读性会被装饰牺牲。"),
    "ink": dict(
        sources=["中国水墨画：宣纸、墨分五色、留白", "文人题跋与印章排版"],
        avoid="高信息密度或多按钮操作页：留白要求与功能密度直接冲突。"),
    "cyberneon": dict(
        sources=["Cyberpunk 霓虹视觉（Blade Runner 一系）", "游戏 HUD 与合成波平面设计"],
        avoid="长文本阅读：暗底发光字连续阅读极易疲劳。"),
    "artdeco": dict(
        sources=["装饰艺术运动（1925 巴黎国际博览会）", "金线、放射线、阶梯母题"],
        avoid="高频操作界面：对称与装饰会妨碍扫视。"),
    "riso": dict(
        sources=["Risograph 孔版印刷与错版叠加", "独立出版与地下海报文化"],
        avoid="需要精准还原品牌色的场景：套印错位让色彩不可控。"),
    "memo": dict(
        sources=["Bullet Journal 手账体系", "和纸胶带、荧光笔、便签的文具语言"],
        avoid="企业对外正式页面：手写感会削弱权威。"),
    "chalk": dict(
        sources=["黑板与粉笔的教学场景", "咖啡馆手写菜单"],
        avoid="小字号密集内容：粉笔质感在 12px 以下会糊成一片。"),
    "pixel": dict(
        sources=["8-bit 像素艺术与早期家用游戏机", "有限调色板（NES 一系）"],
        avoid="需要精细图标或层级较多的界面：像素化会吃掉细节。"),
    "papercut": dict(
        sources=["中国剪纸与层叠纸艺", "立体绘本、纸雕"],
        avoid="需要精确对齐的表单：参差边缘会破坏对齐感。"),
    "newsprint": dict(
        sources=["铅字报纸排版：报头、多栏、双线", "凸版印刷的字距与栏宽传统"],
        avoid="移动端单列阅读：多栏与粗线在窄屏没有落脚点。"),
    "hologram": dict(
        sources=["科幻电影中的全息投影 HUD", "航天与军用遥测界面"],
        avoid="需要高对比无障碍的场景：半透明青字对比度普遍不足。"),
    "material": dict(
        sources=["Google Material Design 3 / Material You（2021）", "动态取色（monet）体系"],
        avoid="品牌主色强烈的产品：色调化会稀释品牌识别。"),
    "fluent": dict(
        sources=["Microsoft Fluent Design（2017）的 Acrylic 材质", "Windows 11 的 Mica 层"],
        avoid="背景本身是纯色时：亚克力需要底下有内容才有意义。"),
    "antidesign": dict(
        sources=["Anti-design（2016 年后）", "朋克拼贴与迷幻海报"],
        avoid="任何需要长期使用的产品：冲突感在第二次访问就开始消耗耐心。"),
    "rawhtml": dict(
        sources=["1993–1996 年的第一批网页", "浏览器默认样式本身（UA stylesheet）"],
        avoid="有品牌表达需求的商业页面：它唯一的价值就是「不做」。"),
    "japandi": dict(
        sources=["Japandi：日式侘寂 + 北欧功能主义", "亚光纸色与发丝线"],
        avoid="需要强转化的活动页：克制与转化率天然矛盾。"),
    "vaporwave": dict(
        sources=["Vaporwave / 蒸汽波（2010 年代网络亚文化）", "Windows 95 与罗马雕塑拼贴"],
        avoid="正式商务场景：它的表达是刻意的过时。"),
    "mono": dict(
        sources=["瑞士单色排印", "黑白摄影画册版式"],
        avoid="层级超过三层的界面：没有颜色，层级只能靠间距，容易失控。"),
    "aurora": dict(
        sources=["极光渐变（2021 年后 SaaS 落地页常见）", "大面积低饱和径向渐变 + 玻璃卡片"],
        avoid="暗环境下长时间阅读：低对比渐变底会持续分心。"),
    "dashboard": dict(
        sources=["运维监控面板（Grafana 一系）", "金融终端的信息密度与等宽数字"],
        avoid="营销页面：深色高密度会让人以为进了老后台。"),
    "docs": dict(
        sources=["技术文档站形态（Stripe / Vercel Docs 一系）", "72ch 正文栏 + 代码块优先"],
        avoid="品牌展示页：文档式的克制会被读成「没设计」。"),
    "luxury": dict(
        sources=["奢侈品行业的黑金视觉（Maison 一系）", "全大写宽字距 + 大黑场"],
        avoid="需要解释功能的产品：黑场与极少文案承载不了功能说明。"),
    "kids": dict(
        sources=["儿童教育与亲子产品插画", "贴纸、蜡笔、三原色"],
        avoid="面向成人的工具产品：高饱和与大圆角会被当成玩具。"),
    "cozy": dict(
        sources=["社区咖啡馆的店招与菜单", "奶油 + 咖啡棕的暖调器物"],
        avoid="效率工具：柔和色调会让「快」这件事说不出口。"),
    "techblue": dict(
        sources=["企业 SaaS 官网（2008 年后的标准形态）", "白底深蓝 + 蓝色渐层按钮"],
        avoid="消费级或创意产品：安全即是平庸。"),
    "saasgrad": dict(
        sources=["深色 SaaS 渐变落地页（2020 年后 Stripe / Linear 一系）", "紫粉光晕 + 渐变文字"],
        avoid="金融、政务等需要稳重感的场景：光晕会被读成不严肃。"),
    "neumorph": dict(
        sources=["Neumorphism（2019 年随 Dribbble 流行）", "同色双阴影的 soft UI"],
        avoid="表单密集的界面：低对比让输入框与按钮难以辨认。"),
    "chinesemodern": dict(
        sources=["新中式：宋体、朱红、留白的现代转译", "传统匾额与界画的比例关系"],
        avoid="国际化产品的主界面：文化符号需要语境。"),
    "gothic": dict(
        sources=["哥特建筑与烛光宗教画", "暗色衬线宽字距的书籍排版"],
        avoid="需要亲和力的消费产品：压迫感正是它的功能。"),
    "ascii": dict(
        sources=["BBS / ASCII art / DOS TUI", "等宽字符画边框"],
        avoid="移动端窄屏：字符框在窄屏一律错位。"),
    "zine": dict(
        sources=["Photocopy zine 与地下出版物", "剪贴 + 网点 + 复印噪点"],
        avoid="需要机构可信度的页面：粗糙感会被读成不可靠。"),
    "corporatememphis": dict(
        sources=["Corporate Memphis / Allegria 插画风格（2019 年后被科技公司大量采用）",
                 "扁平几何人物与粉彩色块"],
        avoid="需要表达专业深度的产品：过度使用后它已经成了「廉价感」符号。"),
    "scandi": dict(
        sources=["北欧设计（Scandinavian Design）", "浅木、米白、苔绿的日常器物"],
        avoid="需要在嘈杂环境抢注意力的广告页：克制等于低音量。"),
    "amberterminal": dict(
        sources=["amber phosphor CRT 单色屏", "80 年代终端与 BBS 客户端"],
        avoid="强光户外使用：琥珀字在阳光下几乎不可见。"),
    "posterswiss": dict(
        sources=["瑞士海报学派（Josef Müller-Brockmann 等）", "大字报式平面与展览海报"],
        avoid="需要长文案的落地页：超大字号装不下信息。"),
    "darkeditorial": dict(
        sources=["暗色编辑出版（夜间版专栏、影评刊物）", "大号衬线 + 荧光强调色"],
        avoid="白天的数据录入界面：暗底衬线在密集操作里拖慢速度。"),
    "retroweb": dict(
        sources=["Web 2.0 时代（2005–2010）的玻璃质感 UI", "光泽按钮、渐变标题栏、NEW 徽章"],
        avoid="现代移动端产品：光泽与渐变在视网膜屏上显得廉价。"),
    "zenminimal": dict(
        sources=["禅意极简与日本平面设计中的「間」", "极小字号 + 极大字距的书籍排版"],
        avoid="需要清晰操作引导的产品：留白过多会让人不知道下一步点哪。"),
    "cyberhud2": dict(
        sources=["战术 / 军事 HUD（斜切角、刻度、括号）", "游戏中的目标锁定界面"],
        avoid="面向大众的消费产品：信息密度与荧光色会带来压迫感。"),
}

# ================================================================ 形态：后台 / App
# 同一套 tokens + 同一风格的 CSS，换一套骨架，验证「设计语言能否跨形态成立」。

def _lum(hexv: str) -> float:
    v = hexv.lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        return 0.0
    def ch(i):
        c = int(v[i:i + 2], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(0) + 0.7152 * ch(2) + 0.0722 * ch(4)


def _accent_ink(accent: str) -> str:
    return "#0b0b0b" if _lum(accent) > 0.42 else "#ffffff"


def root_block(t: dict) -> str:
    r = t["radius"]
    try:
        rs = 0 if float(r.replace("px", "")) == 0 else min(8.0, float(r.replace("px", "")))
    except ValueError:
        rs = 8.0
    rs_css = (f"{rs:g}px")
    return (":root{--bg:%s;--surface:%s;--ink:%s;--muted:%s;--accent:%s;--accent-ink:%s;"
            "--line:%s;--radius:%s;--radius-sm:%s;--font:%s}"
            % (t["bg"], t["surface"], t["ink"], t["muted"], t["accent"], _accent_ink(t["accent"]),
               t["line"], r, rs_css, t["font"]))


ADMIN_CSS = """*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:14px;line-height:1.55}
.shell{display:grid;grid-template-columns:236px 1fr;min-height:100vh}
.side{background:var(--surface);border-right:1px solid var(--line);padding:18px 12px;display:flex;flex-direction:column;gap:2px}
.side .brand{font-weight:800;font-size:15.5px;display:flex;gap:9px;align-items:center;padding:6px 10px 4px;color:var(--ink)}
.side .brand i{width:22px;height:22px;border-radius:var(--radius-sm);background:var(--accent);display:inline-block;flex:0 0 auto}
.side .grouplbl{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);padding:16px 10px 6px}
.side a{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 10px;
  border-radius:var(--radius-sm);color:var(--muted);text-decoration:none;font-size:13.5px}
.side a:hover{background:var(--hover,rgba(125,125,125,.14));color:var(--ink)}
.side a.on{background:var(--accent);color:var(--accent-ink);font-weight:600}
.side a em{font-style:normal;font-size:11px;opacity:.7}
.side .fill{flex:1}
.main{min-width:0;display:flex;flex-direction:column}
.topbar{display:flex;align-items:center;gap:12px;padding:16px 24px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.topbar h1{margin:0;font-size:18.5px;letter-spacing:-.01em}
.topbar .sub{font-size:11.5px;color:var(--muted);margin-top:2px}
.sp{flex:1}
.searchbox{display:flex;align-items:center;gap:7px;border:1px solid var(--line);background:var(--surface);
  border-radius:var(--radius-sm);padding:7px 11px;color:var(--muted);font-size:12.5px}
.body{padding:20px 24px 34px;display:grid;gap:16px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:15px 16px}
.stat .lbl{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.stat .num{font-size:25px;font-weight:700;letter-spacing:-.02em;margin:7px 0 3px;font-variant-numeric:tabular-nums}
.stat .dlt{font-size:11.5px;color:var(--accent)}
.tablewrap{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}
.tbar{display:flex;align-items:center;gap:9px;padding:13px 16px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.tbar h2{margin:0;font-size:14px}
.filt{font:inherit;font-size:12.5px;color:var(--ink);background:var(--field,transparent);
  border:1px solid var(--line);border-radius:var(--radius-sm);padding:6px 9px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);
  font-weight:600;padding:10px 16px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:11px 16px;border-bottom:1px solid var(--line);vertical-align:middle}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--hover,rgba(125,125,125,.10))}
.who{display:flex;align-items:center;gap:9px}
.av{width:25px;height:25px;border-radius:999px;background:var(--accent);color:var(--accent-ink);
  display:grid;place-items:center;font-size:11px;font-weight:700;flex:0 0 auto}
.num{font-variant-numeric:tabular-nums}
.badge{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;
  border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.badge.ok{border-color:var(--accent);color:var(--accent)}
.badge.warn{border-style:dashed}
.pager{display:flex;align-items:center;gap:5px;padding:11px 16px;border-top:1px solid var(--line);
  font-size:12px;color:var(--muted)}
.pager button{font:inherit;font-size:12px;min-width:26px;height:26px;border:1px solid var(--line);
  background:transparent;color:var(--ink);border-radius:var(--radius-sm);cursor:pointer;padding:0 6px}
.pager button.on{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.btn{font:inherit;font-size:12.5px;font-weight:600;border:0;background:var(--accent);
  color:var(--accent-ink);padding:8px 14px;border-radius:var(--radius-sm);cursor:pointer}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--ink);font-weight:500}
@media (max-width:900px){.shell{grid-template-columns:1fr}.side{display:none}.stats{grid-template-columns:repeat(2,1fr)}}
"""

APP_CSS = """*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font);display:grid;place-items:center;
  min-height:100vh;padding:16px 0}
.device{width:375px;height:min(812px,calc(100vh - 32px));background:var(--bg);border:9px solid #17181b;
  border-radius:44px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 26px 60px rgba(0,0,0,.35)}
.statusbar{display:flex;align-items:center;justify-content:space-between;padding:12px 22px 6px;
  font-size:11.5px;color:var(--muted)}
.statusbar b{color:var(--ink);font-weight:600}
.appbar{display:flex;align-items:center;gap:10px;padding:4px 18px 12px}
.appbar h1{margin:0;font-size:19px;letter-spacing:-.01em}
.appbar .back{width:26px;height:26px;border-radius:999px;border:1px solid var(--line);display:grid;
  place-items:center;color:var(--muted);font-size:13px;flex:0 0 auto}
.appbar .act{font-size:12.5px;color:var(--accent);font-weight:600}
.sp{flex:1}
.srch{margin:0 18px 12px;display:flex;align-items:center;gap:8px;background:var(--surface);
  border:1px solid var(--line);border-radius:var(--radius);padding:9px 12px;font-size:12.5px;color:var(--muted)}
.chips{display:flex;gap:7px;padding:0 18px 12px;overflow:hidden}
.chips span{font-size:12px;padding:5px 11px;border-radius:999px;border:1px solid var(--line);
  color:var(--muted);white-space:nowrap}
.chips span.on{background:var(--accent);border-color:var(--accent);color:var(--accent-ink);font-weight:600}
.list{flex:1;overflow:hidden;padding:0 18px}
.item{display:flex;gap:11px;align-items:center;padding:11px 0;border-bottom:1px solid var(--line)}
.item:last-child{border-bottom:0}
.thumb{width:50px;height:50px;border-radius:var(--radius);background:var(--surface);
  border:1px solid var(--line);display:grid;place-items:center;font-size:14px;color:var(--accent);flex:0 0 auto}
.item .tt{margin:0 0 2px;font-size:13.5px;font-weight:600}
.item .mm{margin:0;font-size:11.5px;color:var(--muted)}
.item .rt{margin-left:auto;text-align:right;font-size:12px;color:var(--ink);
  white-space:nowrap;font-variant-numeric:tabular-nums}
.tabbar{display:flex;border-top:1px solid var(--line);background:var(--surface);padding:9px 0 14px}
.tabbar a{flex:1;text-align:center;text-decoration:none;color:var(--muted);font-size:10.5px;
  display:grid;gap:4px;justify-items:center}
.tabbar a i{width:17px;height:17px;border:1px solid currentColor;border-radius:5px;display:block}
.tabbar a.on{color:var(--accent);font-weight:600}
.tabbar a.on i{background:currentColor;border-color:currentColor}
"""

# 个别风格在后台 / App 骨架下需要补一点材质（否则 tokens 撑不起来）
FORM_CSS = {
    "glass": ".side,.stat,.tablewrap,.searchbox,.filt,.pager button,.srch,.thumb{backdrop-filter:blur(18px) saturate(150%)}",
    "cyberhud2": ".stat,.tablewrap{clip-path:polygon(0 0,calc(100% - 12px) 0,100% 12px,100% 100%,12px 100%,0 calc(100% - 12px))}",
    "neubrutalism": ".stat,.tablewrap,.searchbox,.filt{box-shadow:4px 4px 0 #141414}",
    "retroweb": ".stat,.tablewrap{box-shadow:0 2px 6px rgba(40,70,120,.14),inset 0 1px 0 #fff}",
}


def _doc(title: str, css: str, body: str) -> str:
    return (
        '<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + title + "</title>\n<style>\n" + css + "\n</style>\n</head>\n<body>\n"
        + body + "\n</body>\n</html>\n"
    )


ADMIN_ROWS = [
    ("陈一舟", "A-2481", "¥ 1,280.00", "已付款", "ok", "11-08 09:12"),
    ("林见夏", "A-2480", "¥ 320.00", "待付款", "warn", "11-08 08:47"),
    ("周叙", "A-2479", "¥ 4,960.00", "已发货", "ok", "11-07 22:05"),
    ("黄侃", "A-2478", "¥ 88.00", "已退款", "", "11-07 19:31"),
    ("吴小满", "A-2477", "¥ 2,140.00", "已付款", "ok", "11-07 16:02"),
    ("钱立言", "A-2476", "¥ 640.00", "待发货", "warn", "11-07 11:24"),
]

ADMIN_STATS = [
    ("本月 GMV", "¥ 2,418,600", "+12.4% 环比"),
    ("订单数", "1,284", "+6.1% 环比"),
    ("客单价", "¥ 1,883", "−2.3% 环比"),
    ("退款率", "0.82%", "−0.14pt"),
]

APP_ITEMS = [
    ("衣", "亚麻衬衫 · 米白", "M / 2 件 · 已发货", "¥ 636"),
    ("食", "单一产地咖啡豆", "250g · 待付款", "¥ 128"),
    ("住", "灰釉陶瓷马克杯", "1 只 · 已签收", "¥ 168"),
    ("行", "原色帆布托特包", "1 只 · 运输中", "¥ 219"),
    ("书", "《字体排印基础》", "第 3 版 · 已完成", "¥ 88"),
    ("茶", "耐热玻璃茶壶", "600ml · 待收货", "¥ 249"),
    ("器", "黄铜刻字书签", "2 枚 · 已完成", "¥ 96"),
]


def admin_html(s: dict) -> str:
    tr = "\n".join(
        '        <tr><td><span class="who"><span class="av">' + n[0] + "</span>" + n + "</span></td>"
        '<td class="num">' + oid + '</td><td class="num">' + amt + "</td>"
        '<td><span class="badge ' + cls + '">' + st + "</span></td>"
        '<td class="num">' + t + "</td></tr>"
        for n, oid, amt, st, cls, t in ADMIN_ROWS
    )
    stats = "\n".join(
        '        <div class="stat"><div class="lbl">' + lbl + '</div><div class="num">' + num +
        '</div><div class="dlt">' + dlt + "</div></div>"
        for lbl, num, dlt in ADMIN_STATS
    )
    body = (
        '<div class="shell">\n'
        '  <aside class="side">\n'
        '    <div class="brand"><i></i>' + s["brand"] + "</div>\n"
        '    <div class="grouplbl">工作台</div>\n'
        '    <a class="on" href="#">总览 <em>24</em></a>\n'
        '    <a href="#">订单 <em>1.2k</em></a>\n'
        "    <a href=\"#\">客户</a>\n"
        "    <a href=\"#\">商品</a>\n"
        '    <div class="grouplbl">设置</div>\n'
        "    <a href=\"#\">团队成员</a>\n"
        "    <a href=\"#\">账单</a>\n"
        '    <div class="fill"></div>\n'
        "    <a href=\"#\">帮助与反馈</a>\n"
        "  </aside>\n"
        '  <div class="main">\n'
        '    <header class="topbar">\n'
        "      <div><h1>订单管理</h1><div class=\"sub\">2026 年 11 月 · 共 1,284 笔</div></div>\n"
        '      <div class="sp"></div>\n'
        '      <div class="searchbox"><span>⌕</span><span>搜索订单号 / 客户</span></div>\n'
        '      <button class="btn ghost">导出 CSV</button>\n'
        '      <button class="btn">新建订单</button>\n'
        "    </header>\n"
        '    <div class="body">\n'
        '      <section class="stats">\n' + stats + "\n      </section>\n"
        '      <section class="tablewrap">\n'
        '        <div class="tbar"><h2>最近订单</h2><div class="sp"></div>\n'
        '          <select class="filt"><option>全部状态</option><option>待付款</option><option>已发货</option></select>\n'
        '          <select class="filt"><option>最近 7 天</option><option>最近 30 天</option></select>\n'
        "        </div>\n"
        "        <table>\n"
        "          <thead><tr><th>客户</th><th>订单号</th><th>金额</th><th>状态</th><th>时间</th></tr></thead>\n"
        "          <tbody>\n" + tr + "\n          </tbody>\n"
        "        </table>\n"
        '        <div class="pager"><span>显示 1–6 / 1,284</span><div class="sp"></div>\n'
        '          <button>‹</button><button class="on">1</button><button>2</button>'
        "<button>3</button><button>›</button>\n"
        "        </div>\n"
        "      </section>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>"
    )
    css = root_block(s["tokens"]) + "\n" + ADMIN_CSS + "\n" + s["css"].strip() + "\n" + FORM_CSS.get(s["id"], "")
    return _doc(f"{s['name']} · UI 样例", css, body)


def app_html(s: dict) -> str:
    items = "\n".join(
        '      <div class="item"><div class="thumb">' + k + "</div>"
        '<div><p class="tt">' + tt + "</p><p class=\"mm\">" + mm + "</p></div>"
        '<div class="rt">' + rt + "</div></div>"
        for k, tt, mm, rt in APP_ITEMS
    )
    body = (
        '<div class="device">\n'
        '  <div class="statusbar"><b>9:41</b><span>⇥ 5G ▮▮▮</span></div>\n'
        '  <div class="appbar"><span class="back">‹</span><h1>我的订单</h1>'
        '<span class="sp"></span><span class="act">筛选</span></div>\n'
        '  <div class="srch"><span>⌕</span><span>搜索商品或订单号</span></div>\n'
        '  <div class="chips"><span class="on">全部</span><span>待付款</span>'
        "<span>待收货</span><span>已完成</span></div>\n"
        '  <div class="list">\n' + items + "\n  </div>\n"
        '  <nav class="tabbar">\n'
        '    <a class="on" href="#"><i></i>订单</a>\n'
        '    <a href="#"><i></i>分类</a>\n'
        '    <a href="#"><i></i>收藏</a>\n'
        '    <a href="#"><i></i>我的</a>\n'
        "  </nav>\n"
        "</div>"
    )
    css = root_block(s["tokens"]) + "\n" + APP_CSS + "\n" + s["css"].strip() + "\n" + FORM_CSS.get(s["id"], "")
    return _doc(f"{s['name']} · UI 样例", css, body)


# ================================================================ 版式（layout）
# form 与 layout 是两个轴：
#   form   = 产品形态（落地页 / 后台 / App）
#   layout = 页面编排（落地页版式 / 网格 / 海报 / 控制台）
# 全部 60 条塞进同一个「SaaS 落地页」版式，看起来就是同一个页面换配色。
# 版式跟着风格在现实里的用途走，才不会 48 张缩略图长一个样。
LAYOUTS = {
    # 网格：一个屏幕里放几块各自独立的信息
    "bento": "grid", "dashboard": "grid", "clay": "grid",
    "material": "grid", "fluent": "grid", "neumorph": "grid", "aurora": "grid",
    # 控制台：工具、遥测、技术图纸
    "terminal": "console", "ascii": "console", "amberterminal": "console",
    "cyberhud2": "console", "hologram": "console", "blueprint": "console",
    # 海报：印刷流派、展览、演出、街头
    "swiss": "poster", "posterswiss": "poster", "artdeco": "poster", "riso": "poster",
    "zine": "poster", "y2k": "poster", "vaporwave": "poster", "cyberneon": "poster",
    "ink": "poster", "luxury": "poster", "chalk": "poster", "antidesign": "poster",
    "papercut": "poster", "pixel": "poster",
    # 长文：杂志、报纸、文档、笔记
    "editorial": "article", "newsprint": "article", "docs": "article", "rawhtml": "article",
    "japandi": "article", "zenminimal": "article", "mono": "article", "darkeditorial": "article",
    "memo": "article", "chinesemodern": "article", "gothic": "article",
    # 其余留在落地页（SaaS、产品页、小店）
}

LAYOUT_LABEL = {"landing": "落地页", "admin": "后台", "app": "App",
                "grid": "网格版式", "poster": "海报版式", "console": "控制台版式", "article": "长文版式"}

# 文案不再写「这个风格长什么样」，而是给每个风格一个它现实里会被用到的场景：
# 茶馆、街头服饰、杂志、乐队海报、机房里的大屏…… 品牌 / 标题 / 一句话，三者都要能在那个场景里说出口。
COPY = {
    "glass": ("Halo", "把整个桌面，收进一块玻璃", "日程、文件、消息，浮在同一个平面上。"),
    "neubrutalism": ("BRUTAL/01", "第三批，只有黑色", "卫衣、帽子、帆布包。12 月 1 日中午上架。"),
    "bento": ("bento·os", "九个格子，一个人干完", "排期、素材、发布，各占一格，不用开会。"),
    "editorial": ("纪事 · CHRONICLE", "我们为什么还在做纸质杂志", "第十二期：关于慢下来的那点手艺。"),
    "swiss": ("Grid 12", "秩序，就是风格", "苏黎世学派 1955–1980，一场关于网格的展览。"),
    "terminal": ("./atlas", "部署只要一行", "没有仪表盘，没有向导。回车，然后等它变绿。"),
    "blueprint": ("DWG A-104", "第六版结构图已发布", "每根梁都有编号、尺寸和出处。"),
    "clay": ("Clay Studio", "给孩子的第一个编辑器", "按钮是软的，按住还能拖动。"),
    "skeuo": ("Ledger & Co.", "这本账，记了四十年", "植鞣皮革、烫金压印、可换内芯。"),
    "y2k": ("★ starNet", "欢迎来到我的主页", "本站正在建设中，留言告诉我你在哪一年。"),
    "vaporwave": ("VAPOR 永远", "一切都在褪色", "粉、紫、网格，和一段听不清的萨克斯。"),
    "material": ("Material", "颜色会跟着壁纸变", "同一套组件，换一张图就是另一套色调。"),
    "fluent": ("Fluent", "一层薄薄的材质", "亚克力不是玻璃：它更哑、更贴身。"),
    "neumorph": ("Soft UI", "从背景里浮起来", "没有边框，只有光。"),
    "aurora": ("Aurora", "光在动，界面不动", "背景慢慢流，前景保持冷静。"),
    "mono": ("MONO", "一本只有黑白的画册", "四十张照片，一段序，没有别的。"),
    "dashboard": ("OPS / 实时", "早上九点的机房", "四十七个指标，一处异常。"),
    "docs": ("Atlas Docs", "先读这一页，再动手", "文档的第一屏不是营销，是路线图。"),
    "techblue": ("Nexus Cloud", "把审批流程搬上线", "报销、合同、用章，一套走完。"),
    "saasgrad": ("Orbit", "从第一天就看得到转化", "注册、激活、付费，一条漏斗看清。"),
    "luxury": ("MAISON", "第二十三季：黑与更黑", "十七件，只在米兰与东京陈列。"),
    "kids": ("小小工坊", "周六上午，做一只纸狮子", "四岁到八岁，家长可以一起坐下来。"),
    "cozy": ("午后 · 咖啡", "今天也只做三件事", "煮一杯、擦一遍桌子、等一个人。"),
    "antidesign": ("不要好看", "海报被撕掉了一半", "剩下的一半，照常开展。"),
    "rawhtml": ("首页 · Homepage", "这是一个网页", "没有设计系统，只有浏览器默认样式。"),
    "japandi": ("間 · MA", "少一点，才看得见", "留白不是空，是把注意力让出来。"),
    "corporatememphis": ("Allegro", "把财报，画成几块颜色", "董事会看得懂的那一版。"),
    "scandi": ("NORR", "一张桌子，用二十年", "白蜡木、亚麻油、六道打磨。"),
    "posterswiss": ("PLAKAT 07", "字要大到不用解释", "隔着十米也读得出来，才叫海报。"),
    "darkeditorial": ("NIGHT DESK", "凌晨三点，写一封长信", "关于这一年读过的十七本书。"),
    "retroweb": ("webTwo", "光泽、渐变、一枚 NEW 徽章", "那一年，所有按钮都像果冻。"),
    "ink": ("山水间", "山里下了三天雨", "一张宣纸，两行字，剩下的都留白。"),
    "chinesemodern": ("观照", "把话说短，把留白留长", "一场关于宋体字的展，九月开展。"),
    "cyberneon": ("NEON//OS", "夜里两点，街还没睡", "霓虹、雨、一台自动贩卖机。"),
    "artdeco": ("LE MÉTRO", "一九二八年的电梯厅", "黄铜、黑檀、放射状的地面。"),
    "riso": ("RISO PRESS", "印歪一点，才像印的", "两种油墨、一道错版、满屏网点。"),
    "memo": ("课堂 · 03", "第三讲：怎么记笔记", "一条线、两个箭头、三句结论。"),
    "chalk": ("黑板 · 04", "今日只剩三样", "南瓜汤、酸面包、手冲。"),
    "pixel": ("PIXEL·QUEST", "第一章：地下二层", "八个方向，一把剑，没有存档。"),
    "papercut": ("纸间", "一层一层，叠出画面", "纸有厚度，影子会说话。"),
    "newsprint": ("每日界面 · DAILY UI", "第 42 期：界面也要排版", "把落地页当成一版报纸来排。"),
    "hologram": ("ORBITAL-9", "读取中：目标已锁定", "界面是一层投影，随时会消失。"),
    "gothic": ("NOCTURNE", "在暗处，字才发光", "教堂、烛火、和一句低语。"),
    "ascii": ("+-- atlas.tui --+", "本日新帖 12 篇", "登入、留言、退出。拨号 56k。"),
    "zine": ("ZINE / 第 3 期", "复印出来的态度", "剪、贴、复印，然后重复。"),
    "amberterminal": ("amber@tty1", "一块琥珀色的屏", "1983 年的显示器，只有一种颜色。"),
    "zenminimal": ("無 · MU", "空白", "一场只有三件作品的展。"),
    "cyberhud2": ("TAC//OPS", "目标：可读，且快", "信息密度优先，装饰只是刻度。"),
}


GRID_CSS = """*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--font);overflow:hidden}
.g{height:100vh;display:grid;grid-template-columns:repeat(6,1fr);grid-template-rows:repeat(4,1fr);
  gap:12px;padding:12px}
.t{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:20px;
  display:flex;flex-direction:column;justify-content:space-between;gap:8px;overflow:hidden;min-height:0}
.t.hero{grid-column:1/5;grid-row:1/4;padding:26px 28px;gap:14px;justify-content:center}
.t.media{grid-column:5/7;grid-row:1/3;justify-content:space-between}
.t.note{grid-column:5/7;grid-row:3/5;justify-content:space-between}
.t.s1{grid-column:1/3;grid-row:4/5}
.t.s2{grid-column:3/5;grid-row:4/5}
.eyebrow{font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:var(--accent);margin:0}
h1{margin:0;font-size:clamp(26px,3.9vw,48px);line-height:1.14;letter-spacing:-.025em;font-weight:700;
  max-width:7.2em;text-wrap:balance}
.lede{margin:0;font-size:13.5px;line-height:1.7;color:var(--muted);max-width:34ch}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:4px}
.btn{font:inherit;font-size:12.5px;font-weight:600;border:0;background:var(--accent);color:var(--accent-ink);
  padding:10px 16px;border-radius:var(--radius-sm);cursor:pointer}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--ink);font-weight:500}
.cap{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.bars{display:flex;align-items:flex-end;gap:6px;flex:1;min-height:80px}
.bars i{flex:1;background:var(--line);border-radius:4px}
.bars i.on{background:var(--accent)}
.q{margin:0;font-size:13.5px;line-height:1.7;color:var(--ink)}
.n{font-size:26px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
@media (max-width:820px){
  .g{grid-template-columns:1fr;grid-template-rows:none;height:auto}
  .t.hero,.t.media,.t.price,.t.s1,.t.s2{grid-column:auto;grid-row:auto;min-height:150px}
}
"""

POSTER_CSS = """*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font)}
.poster{min-height:100vh;display:grid;grid-template-rows:auto 1fr auto;padding:24px 40px 22px}
.p-top{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:16px;padding-bottom:10px;
  border-bottom:1px solid var(--line);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.p-top .b{color:var(--ink);letter-spacing:.1em}
.p-main{display:grid;grid-template-columns:52px minmax(0,1fr) 176px;gap:20px;align-content:center;padding:34px 0 30px}
.num{font-size:11.5px;letter-spacing:.12em;color:var(--muted);padding-top:18px}
h1{margin:0;font-size:clamp(52px,10.4vw,140px);line-height:1.08;letter-spacing:-.05em;font-weight:700;
  overflow-wrap:anywhere}
h1 span{display:block}
.p-side{align-self:end;display:grid;gap:10px;font-size:11.5px;line-height:1.75;color:var(--muted)}
.p-side .first{color:var(--ink);font-size:12.5px;line-height:1.6}
.p-rule{height:11px;background:var(--accent);margin-bottom:12px}
.p-bottom{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;font-size:11px;color:var(--muted)}
.p-bottom b{display:block;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink);margin-bottom:4px}
.sw{display:inline-block;width:10px;height:10px;background:var(--accent);margin-right:6px;vertical-align:-1px}
@media (max-width:820px){
  .poster{padding:18px 20px}
  .p-main{grid-template-columns:1fr;gap:12px}
  .num{padding-top:0}
  .p-bottom{grid-template-columns:repeat(2,1fr)}
}
"""

CONSOLE_CSS = """*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:14px;line-height:1.75}
.term{height:100vh;display:flex;flex-direction:column}
.bar{display:flex;align-items:center;gap:10px;padding:8px 16px;border-bottom:1px solid var(--line);
  font-size:11.5px;color:var(--muted);letter-spacing:.04em}
.dots{display:flex;gap:5px}
.dots i{width:9px;height:9px;border:1px solid currentColor;border-radius:50%;opacity:.55}
.bar .path{margin-left:auto}
.body{flex:1;padding:20px 24px;overflow:hidden}
.ln{margin:0;white-space:pre-wrap}
.p{color:var(--accent)}
.c{color:var(--ink)}
.o{color:var(--muted)}
.tbl{display:grid;grid-template-columns:132px 132px auto;gap:0 18px;width:max-content;
  min-width:392px;color:var(--muted);padding:2px 0}
.tbl .ok{color:var(--accent)}
.cursor{display:inline-block;width:9px;height:16px;background:var(--ink);vertical-align:-3px;
  animation:blink 1.05s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.status{display:flex;justify-content:space-between;padding:6px 16px;border-top:1px solid var(--line);
  font-size:11px;color:var(--muted);letter-spacing:.08em}
@media (prefers-reduced-motion:reduce){.cursor{animation:none}}
"""


def grid_html(s: dict) -> str:
    bars = "".join(
        '<i style="height:%d%%"%s></i>' % (h, ' class="on"' if i == 7 else "")
        for i, h in enumerate([38, 46, 42, 55, 61, 57, 72, 88])
    )
    body = (
        '<div class="g">\n'
        '  <section class="t hero">\n'
        '    <p class="eyebrow">' + s["brand"] + ' · 2026</p>\n'
        "    <h1>" + s["h1"] + "</h1>\n"
        '    <p class="lede">' + s["lede"] + "</p>\n"
        '    <div class="row"><button class="btn">开始使用</button>'
        '<button class="btn ghost">看文档</button></div>\n'
        "  </section>\n"
        '  <section class="t media">\n'
        '    <span class="cap">近 8 周用量</span>\n'
        '    <div class="bars" aria-hidden="true">' + bars + "</div>\n"
        "  </section>\n"
        '  <section class="t note">\n'
        '    <span class="cap">设计说明</span>\n'
        '    <p class="q">' + s["features"][0] + "</p>\n"
        '    <button class="btn">了解更多</button>\n'
        "  </section>\n"
        '  <section class="t s1">\n'
        '    <span class="cap">本周访问</span>\n'
        '    <div class="n">12,480</div>\n'
        "  </section>\n"
        '  <section class="t s2">\n'
        '    <span class="cap">较上周</span>\n'
        '    <div class="n">+8.2%</div>\n'
        "  </section>\n"
        "</div>"
    )
    css = root_block(s["tokens"]) + "\n" + GRID_CSS + "\n" + s["css"].strip()
    return _doc(f"{s['name']} · 网格版式 · UI 样例", css, body)


def _poster_lines(text: str) -> list:
    """海报标题断行：有逗号就断在逗号后，否则对半断；不硬凑单字行。"""
    t = text.strip()
    if "，" in t:
        i = t.index("，") + 1
        return [t[:i], t[i:]]
    if len(t) <= 6:
        return [t]
    k = (len(t) + 1) // 2
    return [t[:k], t[k:]]


POSTER_LINE = {
    "swiss": "展期 3.14–6.02 · 苏黎世设计博物馆",
    "posterswiss": "双年展 · 科艺中心 B1 · 免票",
    "artdeco": "一九二八年，巴黎，一间电梯厅的复原",
    "riso": "每周三开印 · 两种油墨 · 现场取件",
    "zine": "第 3 期 · 印量 200 · 免费取阅",
    "y2k": "本站建于 1999 年，上周二更新过一次",
    "vaporwave": "磁带已售罄 · 数字版随时可听",
    "cyberneon": "每周五 23:00 · 门票 80 · 提供耳塞",
    "ink": "明前龙井，四月十二日开售",
    "luxury": "米兰 9.21 / 东京 10.05 · 需预约",
    "chalk": "今日 11:00–14:00 · 只做午市",
    "antidesign": "被撕掉的那一半，贴在二楼楼梯口",
    "papercut": "展出 36 幅，含 4 幅新作",
    "pixel": "第一章已上线 · 第二、三章 12 月更新",
}


def poster_html(s: dict) -> str:
    feats = s["features"]
    side3 = POSTER_LINE.get(s["id"]) or (feats[1] if len(feats) > 1 else s["name_en"])
    body = (
        '<div class="poster">\n'
        '  <div class="p-top">\n'
        '    <span class="b">' + s["brand"] + "</span>\n"
        "    <span>" + s["name_en"] + "</span>\n"
        "    <span>" + (s.get("era") or "—") + "</span>\n"
        "    <span>No.01 / A1</span>\n"
        "  </div>\n"
        '  <div class="p-main">\n'
        '    <div class="num">01</div>\n'
        "    <h1>" + "".join("<span>" + ln + "</span>" for ln in _poster_lines(s["h1"])) + "</h1>\n"
        '    <div class="p-side">\n'
        '      <p class="first">' + s["lede"] + "</p>\n"
        "      <p>" + side3 + "</p>\n"
        '      <p>主办 / ' + s["brand"] + "</p>\n"
        "    </div>\n"
        "  </div>\n"
        '  <div class="p-rule" aria-hidden="true"></div>\n'
        '  <div class="p-bottom">\n'
        "    <div><b>字体</b>" + s["tokens"]["font"].split(",")[0].strip("'\"") + "</div>\n"
        "    <div><b>字距</b>−0.05em</div>\n"
        '    <div><b>强调色</b><span class="sw"></span>' + s["tokens"]["accent"] + "</div>\n"
        "    <div><b>版式</b>" + s["name"] + "</div>\n"
        "  </div>\n"
        "</div>"
    )
    css = root_block(s["tokens"]) + "\n" + POSTER_CSS + "\n" + s["css"].strip()
    return _doc(f"{s['name']} · 海报版式 · UI 样例", css, body)


CONSOLE_SESSION = {
    "terminal": dict(
        path="~/atlas · 80×24", doc="README.md",
        cmd1="atlas --version", out1="atlas 2.6.0 · build 2026-11-08",
        cmd2="atlas status",
        head=("NAME", "STATUS", "UPTIME"),
        rows=[("gateway", "running", "41d 06h"), ("indexer", "running", "41d 06h"), ("worker×4", "idle", "41d 06h")],
        cmd3="atlas logs --tail 4",
        logs=[("o", "[09:41:02] info  gateway  handshake ok · 12ms"),
              ("o", "[09:41:03] info  indexer  reindex 1,284 docs"),
              ("p", "[09:41:07] warn  worker-3 retry 1/3 · timeout"),
              ("o", "[09:41:09] info  worker-3 recovered")],
        status=("-- INSERT --", "utf-8 · 100% · 1/1"),
    ),
    "ascii": dict(
        path="bbs.starnet:23 · 9600", doc="关于本站",
        cmd1="telnet bbs.starnet", out1="已连接 · guest 登入 · 在线 42 人",
        cmd2="boards --top",
        head=("版块", "在线", "今日帖"),
        rows=[("散文", "12", "48"), ("二手", "7", "31"), ("留言", "23", "96")],
        cmd3="last --n 4",
        logs=[("o", "[22:14] guest   登入 · 端口 3"),
              ("o", "[22:15] guest   读取「散文」第 41 帖"),
              ("p", "[22:19] system  本日新帖 12 篇"),
              ("o", "[22:20] guest   退出")],
        status=("-- 就绪 --", "big5 · 9600 · 1/1"),
    ),
    "amberterminal": dict(
        path="/usr/spool · tty1", doc="MOTD",
        cmd1="ls -l /usr/spool", out1="total 128 · 1983-11-08 03:12",
        cmd2="df -h",
        head=("DEVICE", "MOUNT", "USED"),
        rows=[("tty1", "/", "62%"), ("tty2", "/usr", "71%"), ("lp0", "/spool", "18%")],
        cmd3="tail /var/log/print.log",
        logs=[("o", "[03:12] lp0  job 118 queued · 4 pages"),
              ("o", "[03:14] lp0  job 118 done"),
              ("p", "[03:15] lp0  paper low · 12 sheets"),
              ("o", "[03:15] op   refilled tray")],
        status=("-- 插入 --", "ascii · 100% · 1/1"),
    ),
    "cyberhud2": dict(
        path="TAC//OPS · uplink", doc="BRIEF",
        cmd1="tac status", out1="uplink ok · sig 92% · 4 units online",
        cmd2="tac grid --lock",
        head=("UNIT", "SIG", "LOCK"),
        rows=[("alpha", "92%", "locked"), ("bravo", "88%", "locked"), ("charlie", "61%", "scanning")],
        cmd3="tac log --tail 4",
        logs=[("o", "[T-12] alpha  handshake ok"),
              ("o", "[T-09] charlie re-acquire"),
              ("p", "[T-04] charlie sig 61% · below 70%"),
              ("o", "[T-01] delta   standby")],
        status=("-- ARMED --", "sig · 92% · 4/4"),
    ),
    "hologram": dict(
        path="ORB-9 · projection", doc="manifest",
        cmd1="orbital scan", out1="projection 41% · est. 12s remaining",
        cmd2="orbital lock",
        head=("TARGET", "RANGE", "STATE"),
        rows=[("KX-118", "2.4 km", "locked"), ("VX-042", "8.1 km", "pending"), ("—", "—", "lost")],
        cmd3="orbital log",
        logs=[("o", "[orb] KX-118  vector stable"),
              ("o", "[orb] VX-042  drift 0.3°"),
              ("p", "[orb] VX-042  signal lost"),
              ("o", "[orb] holding projection")],
        status=("-- 投影中 --", "41% · 12s"),
    ),
    "blueprint": dict(
        path="DWG A-104 · rev 6", doc="NOTES",
        cmd1="dwg list --rev 6", out1="sheets 12 · rev 6 · 2026-11-08",
        cmd2="dwg check",
        head=("SHEET", "REV", "CHECK"),
        rows=[("A-101", "6", "ok"), ("A-104", "6", "ok"), ("S-203", "5", "stale")],
        cmd3="dwg diff --rev 5..6",
        logs=[("o", "[rev5] 梁 L-12 位移 40mm"),
              ("o", "[rev6] 已修正并复核"),
              ("p", "[rev6] S-203 未同步 · 仍为 rev5"),
              ("o", "[rev6] 待结构专业确认")],
        status=("-- 审阅 --", "A-104 · rev 6"),
    ),
}


def console_html(s: dict) -> str:
    c = CONSOLE_SESSION.get(s["id"], CONSOLE_SESSION["terminal"])
    tbl = "".join(
        "<span>" + a + '</span><span class="ok">' + b + "</span><span>" + d + "</span>"
        for a, b, d in c["rows"]
    )
    logs = "".join(
        '    <p class="ln ' + cls + '">' + txt + "</p>\n" for cls, txt in c["logs"]
    )
    rule = "─" * 46
    body = (
        '<div class="term">\n'
        '  <div class="bar">\n'
        '    <span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>\n'
        "    <span>" + s["brand"] + "</span>\n"
        '    <span class="path">' + c["path"] + "</span>\n"
        "  </div>\n"
        '  <div class="body">\n'
        '    <p class="ln"><span class="p">$</span> <span class="c">' + c["cmd1"] + "</span></p>\n"
        '    <p class="ln o">' + c["out1"] + "</p>\n"
        '    <p class="ln">&nbsp;</p>\n'
        '    <p class="ln"><span class="p">$</span> <span class="c">' + c["cmd2"] + "</span></p>\n"
        '    <p class="ln o">' + rule + "</p>\n"
        '    <div class="tbl"><span>' + c["head"][0] + "</span><span>" + c["head"][1]
        + "</span><span>" + c["head"][2] + "</span>" + tbl + "</div>\n"
        '    <p class="ln o">' + rule + "</p>\n"
        '    <p class="ln">&nbsp;</p>\n'
        '    <p class="ln"><span class="p">$</span> <span class="c">' + c["cmd3"] + "</span></p>\n"
        + logs +
        '    <p class="ln">&nbsp;</p>\n'
        '    <p class="ln"><span class="p">$</span> <span class="c">cat ' + c["doc"] + "</span></p>\n"
        '    <p class="ln c">' + s["h1"] + "</p>\n"
        '    <p class="ln o">' + s["lede"] + "</p>\n"
        '    <p class="ln">&nbsp;</p>\n'
        '    <p class="ln"><span class="p">$</span> <span class="cursor" aria-hidden="true"></span></p>\n'
        "  </div>\n"
        '  <div class="status"><span>' + c["status"][0] + "</span><span>" + c["status"][1] + "</span></div>\n"
        "</div>"
    )
    css = root_block(s["tokens"]) + "\n" + CONSOLE_CSS + "\n" + s["css"].strip()
    return _doc(f"{s['name']} · 控制台版式 · UI 样例", css, body)


# 报纸就该分栏——正文分两栏，其他长文保持单栏
ARTICLE_COLS = {"newsprint": 2}

# 长文版式的正文：不是「介绍这个风格」，而是这个体裁里真会出现的段落。
# 每条 2–3 段，可带一个小标题（tuple 第一项为空表示没有小标题）。
PROSE = {
    "editorial": [
        ("", "编辑部在城北一栋老厂房的三层，冬天暖气不热。每期开工那天，我们把上一期的样刊摊满长桌，从第一页翻到最后一页，只用红笔圈出两样东西：哪里读不下去，哪里翻得太快。"),
        ("", "剩下的活都是慢的。纸选 80g 轻涂，翻页时不该有声音；油墨只用两种，多一种就抢戏；栏宽定死在六十二字，因为再宽一点，眼睛就得回头找下一行。"),
        ("一期刊物要过多少只手", "编辑、校对、印厂师傅、装订工，最后是邮局。每一道都有人签字，签完这一页才算完。有人说这是浪费，我们觉得，签过字的东西才有分量。"),
    ],
    "rawhtml": [
        ("", "这个页面是用记事本写的。没有框架，没有构建步骤，没有样式表——浏览器给什么，它就长什么样。"),
        ("", "链接是蓝色的，因为它们一直是蓝色的。标题有六级，因为 HTML 只有六级。图片没有圆角，因为 1993 年没有圆角。"),
        ("为什么还留着它", "它提醒我：排版不是必需品。内容能读、链接能点，页面就成立了。剩下的都是后来的事。"),
    ],
    "japandi": [
        ("", "一只碗，放在桌上。碗里什么都没有，但你不会说它是空的——它等着被用。留白也是这样，不是没东西，是还没被填。"),
        ("", "我们把器物的颜色减到三种：亚麻、烟灰、苔绿。多一种，眼睛就要多分一次神，吃饭这件事就被打断了。"),
        ("空出来的地方", "桌子留出一半，才放得下第二只碗。房间留出一面墙，光才有地方落。做这些东西这些年，学会的减法比加法多。"),
    ],
    "mono": [
        ("", "这四十张照片拍于同一条街，跨度十一年。中间那家五金店换了三次招牌，老板没换。"),
        ("", "去掉颜色不是风格，是必要的偷懒：一旦只剩明暗，构图就无处可躲。哪张照片是靠颜色撑着的，一眼就看得出来。"),
        ("关于排序", "画册的顺序改了七遍。最后按每天经过它的时间来排，从清晨到深夜，而不是按拍得好看的程度。"),
    ],
    "docs": [
        ("", "这份文档假设你已经在跑一个项目，只想把它接进来。所以第一页不是介绍，是路线图：三步能跑起来，五分钟能出错，出错之后去哪查。"),
        ("", "我们尽量把「为什么」写在「怎么做」旁边。你在凌晨两点读到的每一句，都应该是有人在凌晨两点写下的。"),
        ("读不下去怎么办", "每条命令后面都有一个可以直接复制的片段，每个报错都有一条对应的说明。如果哪一页让你卡住超过十分钟，那是我们的问题，请告诉我们。"),
    ],
    "darkeditorial": [
        ("", "这封信写于凌晨三点，写到一半停电，笔记本剩 12% 的电。我把它写完了，然后删掉了开头两段——它们太客气。"),
        ("", "今年读了十七本书，记住的不到五本。记住的这几本有一个共同点：作者都在某处停下来，说了一句不确定的话，然后继续。"),
        ("关于不确定", "确定的东西读起来很省力，也很容易忘。我愿意相信那些写到一半开始犹豫的人，他们至少没有骗自己。"),
    ],
    "memo": [
        ("", "笔记不是抄写。抄写只证明你手在动；笔记要证明你在想。所以我的本子上，右边记老师说的，左边记我没听懂的。"),
        ("", "三个符号够用：一条线连因果，两个箭头分先后，一个方框圈结论。颜色只用两种，红的标疑点，蓝的写自己的话。"),
        ("复习的时候", "只看左边。左边懂了，右边就不用再看；左边一直是空的，说明这节课白上了。"),
    ],
    "newsprint": [
        ("", "本报讯（记者 界面观察）本周三，三家独立工作室先后改版官网，均放弃单栏滚动，改用多栏排版，理由高度一致：图文太多，一栏排不下。"),
        ("", "据其中一家负责人介绍，改版后首屏信息量提升约四成，用户平均停留时间反而下降。他承认这在预期之内：「报纸从来不追求你一次读完。」"),
        ("排版的旧账", "排版学界人士指出，多栏、细线、报头这套结构自上世纪初定型，一百年来只改过字号。界面的问题，纸早就答过了。"),
    ],
    "chinesemodern": [
        ("", "这场展只做一件事：把宋体从屏幕里请出来，放回它该有的尺寸。四十八个字，每个字一米二，观众要退后三步才能看全。"),
        ("", "字大了，毛病也大了。横细竖粗不再是风格，是结构；撇捺的收笔藏不住，哪里犹豫，哪里就软。"),
        ("为什么是宋体", "因为它是我们唯一还在天天读的古典字体。印刷体里的宋，屏幕上的黑，中间隔着一百年——这场展想把这一百年摆出来给人看。"),
    ],
    "gothic": [
        ("", "教堂里的字是往上走的。不是因为高，是因为蜡烛在下面，光从低处来，字只能向上找地方。"),
        ("", "我们把这一页做成暗的，不是为了酷。亮底上的黑字会喊；暗底上的浅字只会说，说完就退回去。"),
        ("留一句就好", "所以你在这里只看到一句话，和它下面很大的一块黑暗。那块黑暗不是没做完，是我们想让你在那儿停一下。"),
    ],
    "zenminimal": [
        ("", "三件作品：一块石头，一张纸，一段录音。展厅一百二十平米，其余的地方都空着。"),
        ("", "空着不是省事。人走进来，先要绕一圈，找不到东西，才会停下来。停下来的那几分钟，才是这场展的全部内容。"),
        ("看完了", "出口没有导览，没有纪念品。如果你回去的路上还记得石头的温度，那就不用再来了。"),
    ],
}

ARTICLE_CSS = """*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15.5px;line-height:1.85}
.wrap{max-width:1040px;margin:0 auto;padding:22px 28px 36px;display:grid;
  grid-template-columns:104px minmax(0,1fr);gap:0 40px}
.mast{grid-column:1/-1;display:flex;align-items:baseline;gap:14px;padding-bottom:12px;
  border-bottom:1px solid var(--line);margin-bottom:28px}
.mast .b{font-weight:700;font-size:16px}
.mast nav{margin-left:auto;display:flex;gap:16px;font-size:12px;color:var(--muted)}
a{color:inherit;text-decoration:none}
.rail{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
  display:grid;gap:8px;align-content:start;padding-top:8px}
.art{min-width:0;max-width:60ch}
.eyebrow{margin:0 0 14px;font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:var(--accent)}
h1{margin:0 0 18px;font-size:clamp(28px,4vw,46px);line-height:1.18;letter-spacing:-.02em;font-weight:700;
  text-wrap:balance}
.stand{margin:0 0 22px;font-size:17px;line-height:1.8;color:var(--muted)}
.rule{border:0;border-top:1px solid var(--line);margin:0 0 26px}
.sec{display:grid;grid-template-columns:32px minmax(0,1fr);gap:10px;margin:0 0 20px}
.sec .n{font-size:11px;color:var(--accent);padding-top:7px;font-variant-numeric:tabular-nums}
.sec p{margin:0;font-size:15px;line-height:1.9}
.art h2{margin:30px 0 12px;font-size:16px;font-weight:600;letter-spacing:.01em}
.art .body{margin:0 0 18px;font-size:15.5px;line-height:1.95}
.art .cols{column-count:2;column-gap:32px;column-rule:1px solid var(--line);max-width:none}
.art .cols h2{margin-top:0}
.art:has(.cols){max-width:none}
.pull{margin:30px 0;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);
  font-size:17px;line-height:1.75;letter-spacing:-.01em;color:var(--muted)}
.pull-k{display:block;margin-bottom:8px;font-size:11px;letter-spacing:.24em;text-transform:uppercase;
  color:var(--accent)}
.colophon{grid-column:1/-1;margin-top:34px;padding-top:14px;border-top:1px solid var(--line);
  font-size:11.5px;color:var(--muted);display:flex;gap:14px}
@media (max-width:820px){
  .wrap{grid-template-columns:1fr;padding:18px 20px}
  .rail{grid-auto-flow:column;justify-content:start;gap:14px;padding:0 0 18px}
  .art{max-width:none}
}
"""


def article_html(s: dict) -> str:
    f = s["features"]
    rows = PROSE.get(s["id"])
    if rows:
        secs = "".join(
            (('      <h2>' + sub + "</h2>\n") if sub else "")
            + '      <p class="body">' + txt + "</p>\n"
            for sub, txt in rows
        )
    else:
        secs = "".join(
            '      <div class="sec"><span class="n">%02d</span><p>%s</p></div>\n' % (i + 1, x)
            for i, x in enumerate(f)
        )
    pull = META.get(s["id"], {}).get("avoid") or s["lede"]
    body = (
        '<div class="wrap">\n'
        '  <header class="mast"><span class="b">' + s["brand"] + "</span>"
        '<nav><a href="#">目录</a><a href="#">归档</a><a href="#">关于</a></nav></header>\n'
        '  <aside class="rail"><span>' + s["name_en"] + "</span><span>"
        + (s.get("era") or "—") + "</span><span>8 分钟</span></aside>\n"
        '  <article class="art">\n'
        '    <p class="eyebrow">' + s["name"] + "</p>\n"
        "    <h1>" + s["h1"] + "</h1>\n"
        '    <p class="stand">' + s["lede"] + "</p>\n"
        '    <hr class="rule">\n'
        + ('    <div class="cols">\n' + secs + "    </div>\n" if ARTICLE_COLS.get(s["id"]) else secs) +
        '    <p class="pull"><span class="pull-k">别用在这</span>' + pull + "</p>\n"
        "  </article>\n"
        '  <footer class="colophon"><span>© 2026 ' + s["brand"] + "</span>"
        "<span>风格样例 · 非真实刊物</span></footer>\n"
        "</div>"
    )
    css = root_block(s["tokens"]) + "\n" + ARTICLE_CSS + "\n" + s["css"].strip()
    return _doc(f"{s['name']} · 长文版式 · UI 样例", css, body)


def page_html(s: dict, form: str, layout: str) -> str:
    if form == "admin":
        return admin_html(s)
    if form == "app":
        return app_html(s)
    if layout == "grid":
        return grid_html(s)
    if layout == "poster":
        return poster_html(s)
    if layout == "console":
        return console_html(s)
    if layout == "article":
        return article_html(s)
    return landing_html(s)


def demo_html(s: dict, form: str = "landing") -> str:
    if form == "admin":
        return admin_html(s)
    if form == "app":
        return app_html(s)
    return landing_html(s)


def landing_html(s: dict) -> str:
    brand = s["brand"]
    cards = s.get("cards") or [
        ("01", "只留必要", "舍掉的东西，比留下的更能说明这是什么。"),
        ("02", "耐用", "时间越久越顺手，不用每两年翻新一次。"),
        ("03", "说得清", "每个选择都有理由，不只是「看起来不错」。"),
    ]
    cards_html = "\n".join(
        f'    <article class="card"><span class="k">{k}</span><h3>{h}</h3><p>{p}</p></article>'
        for k, h, p in cards
    )
    h1 = s.get("h1_html") or s["h1"]
    lede = s["lede"]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{s['name']} · UI 样例</title>
<style>
:root{{--bg:{s['tokens']['bg']};--surface:{s['tokens']['surface']};--ink:{s['tokens']['ink']};
--muted:{s['tokens']['muted']};--accent:{s['tokens']['accent']};--line:{s['tokens']['line']};
--radius:{s['tokens']['radius']};--radius-sm:8px;--font:{s['tokens']['font']}}}
{BASE_CSS.strip()}
{s['css'].strip()}
</style>
</head>
<body>
<div class="wrap">
  <header class="nav">
    <a class="brand" href="#">{brand}</a>
    <nav><a href="#">首页</a><a href="#">服务</a><a href="#">联系</a></nav>
    <span class="spacer"></span>
    <button class="btn ghost">了解</button>
    <button class="btn">联系我们</button>
  </header>

  <section class="hero">
    <p class="eyebrow">{s['name_en']}</p>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    <div class="row">
      <button class="btn">了解更多</button>
      <button class="btn ghost">联系方式</button>
    </div>
    <p class="meta">样例页面 · 不承载真实业务</p>
  </section>

  <section class="cards">
{cards_html}
  </section>

  <section class="panel">
    <div>
      <p class="eyebrow">关于这份样例</p>
      <h2>把「{s['name']}」的 tokens 拿走</h2>
      <p>规则不多，但每条都不能省。留个邮箱，我们把 CSS 变量、可执行提示词和一份可编辑样例发给你。</p>
    </div>
    <form onsubmit="event.preventDefault();this.querySelector('.btn').textContent='已发送 ✓'">
      <label>邮箱<input type="email" placeholder="you@example.com" required></label>
      <label>想用在哪<select><option>落地页</option><option>后台界面</option><option>品牌官网</option></select></label>
      <button class="btn" type="submit">发送</button>
    </form>
  </section>

  <footer class="foot">
    <span>© 2026 {brand}</span><span>风格样例 · 非真实业务</span><span>生成于 ui-atlas/tools/gen_demos.py</span>
  </footer>
</div>
</body>
</html>
"""


# 形态矩阵：这 6 个风格各补 admin / app 两个形态
VARIANT_BASES = ["glass", "swiss", "neubrutalism", "ink", "terminal", "luxury"]
VARIANT_FORMS = ["admin", "app"]
FORM_LABEL = {"landing": "落地页", "admin": "后台", "app": "App"}
FORM_ORDER = {"landing": 0, "admin": 1, "app": 2}


def _interleave(bases: list) -> list:
    """把同一组里的风格按版式交错排：相邻两张尽量不是同一种版式。"""
    buckets = {}
    for b in bases:
        buckets.setdefault(LAYOUTS.get(b["id"], "landing"), []).append(b)
    order, last = [], None
    while any(buckets.values()):
        keys = sorted([k for k, v in buckets.items() if v], key=lambda k: -len(buckets[k]))
        pick = next((k for k in keys if k != last), keys[0])
        order.append(buckets[pick].pop(0))
        last = pick
    return order


def main() -> None:
    DEMOS.mkdir(parents=True, exist_ok=True)
    for s in S:
        c = COPY.get(s["id"])
        if c:
            s["brand"], s["h1"], s["lede"] = c
    by_id = {s["id"]: s for s in S}

    jobs = [(s, "landing", None) for s in S]
    for base in VARIANT_BASES:
        if base not in by_id:
            raise SystemExit(f"VARIANT_BASES 里的 {base} 不存在")
        b = by_id[base]
        for form in VARIANT_FORMS:
            v = dict(b)
            v["id"] = f"{base}-{form}"
            v["name"] = f"{b['name']} · {FORM_LABEL[form]}"
            v["name_en"] = f"{b['name_en']} {FORM_LABEL[form]}"
            jobs.append((v, form, base))

    data = []
    for s, form, base in jobs:
        layout = LAYOUTS.get(s["id"], "landing") if form == "landing" else form
        (DEMOS / f"{s['id']}.html").write_text(page_html(s, form, layout), encoding="utf-8")
        meta = META.get(base or s["id"], {})
        data.append({
            "id": s["id"], "name": s["name"], "name_en": s["name_en"],
            "group": s["group"], "era": s.get("era", ""),
            "form": form, "layout": layout, "base": base or s["id"],
            "tokens": s["tokens"], "features": s["features"], "prompt": s["prompt"],
            "sources": meta.get("sources", []), "avoid": meta.get("avoid", ""),
            "demo": f"demos/{s['id']}.html",
        })

    seq = {}
    for grp in ("classic", "shift"):
        for i, b in enumerate(_interleave([s for s in S if s["group"] == grp])):
            seq[b["id"]] = i
    # 落地页那 48 条先铺满（版式交错），形态变体（后 台 / App）统一排在后面，
    # 否则每一屏都是「同一风格的三张」，看着又变成重复。
    data.sort(key=lambda x: (x["group"] != "classic",
                             0 if x["form"] == "landing" else 1,
                             seq.get(x["base"], 0),
                             FORM_ORDER[x["form"]]))
    (ROOT / "styles.json").write_text(json.dumps({"total": len(data), "styles": data},
                                                 ensure_ascii=False, indent=2), encoding="utf-8")
    forms, layouts = {}, {}
    for e in data:
        forms[e["form"]] = forms.get(e["form"], 0) + 1
        layouts[e["layout"]] = layouts.get(e["layout"], 0) + 1
    print(f"生成 {len(data)} 个样例 → {DEMOS}")
    print("形态分布：" + " / ".join(f"{FORM_LABEL[k]} {v}" for k, v in forms.items()))
    print("版式分布：" + " / ".join(f"{LAYOUT_LABEL[k]} {v}" for k, v in layouts.items()))


if __name__ == "__main__":
    main()
