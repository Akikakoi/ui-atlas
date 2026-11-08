#!/usr/bin/env python3
"""校验 UI Atlas 的数据与样例，并输出一份可读的体检表。

用法：
    python ui-atlas/tools/check.py            # 只报告
    python ui-atlas/tools/check.py --strict    # 有警告也算失败

检查项：
    1. id 唯一；styles.json 与 demos/ 目录一一对应；demo 文件存在
    2. tokens 必填键齐全（bg/surface/ink/muted/accent/line/radius/font）
    3. 样例自包含：不出现 http(s):// 外链、不出现 <script>
    4. 样例里用到的 var(--x) 必须已在 :root 定义（带兜底值的只记警告）
    5. 文案完整：features ≥ 3 条、prompt / sources / avoid 非空
最后打印每条风格的字号阶梯、圆角、WCAG 对比度。

退出码：0 通过；1 有错误（--strict 时含警告）。
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMOS = ROOT / "demos"
DATA = ROOT / "styles.json"

REQUIRED_TOKENS = ["bg", "surface", "ink", "muted", "accent", "line", "radius", "font"]
VALID_FORMS = {"landing", "admin", "app"}
VALID_LAYOUTS = {"landing", "admin", "app", "grid", "poster", "console", "article"}

RE_HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RE_RGBA = re.compile(
    r"^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$"
)
RE_VAR_DEF = re.compile(r"--([\w-]+)\s*:")
RE_VAR_USE = re.compile(r"var\(\s*--([\w-]+)\s*(,)?")
RE_ROOT = re.compile(r":root\s*\{([^}]*)\}")
RE_FONT_PX = re.compile(r"font-size:\s*([\d.]+)px")
RE_CLAMP_PX = re.compile(r"clamp\(\s*([\d.]+)px")

# BASE_CSS 预留的「可选钩子」变量：有兜底值、可按风格覆盖，不算漏定义
OPTIONAL_HOOKS = {"nav-border", "btn-border", "btn-shadow", "card-border",
                  "card-shadow", "field", "hover", "accent-ink"}


# ---------------------------------------------------------------- 颜色与对比度
def parse_color(v: str):
    """返回 (r, g, b, a)，rgb 为 0–255，a 为 0–1；无法解析返回 None。"""
    v = v.strip()
    m = RE_HEX.match(v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    m = RE_RGBA.match(v)
    if m:
        a = 1.0 if m.group(4) is None else float(m.group(4))
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)
    return None


def blend(fg, bg):
    """把带 alpha 的前景压在背景上，返回不透明 rgb。"""
    a = fg[3]
    return (fg[0] * a + bg[0] * (1 - a), fg[1] * a + bg[1] * (1 - a), fg[2] * a + bg[2] * (1 - a))


def rel_lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb[0], rgb[1], rgb[2]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(fg_str, bg_str, base_str="#ffffff"):
    """WCAG 对比度。bg 可以是半透明（如 rgba(255,255,255,.10)），会先叠到 base 上。"""
    fg, bg, base = parse_color(fg_str), parse_color(bg_str), parse_color(base_str)
    if not fg or not bg or not base:
        return None
    page = blend(base, (255, 255, 255)) if base[3] < 1 else base[:3]
    bg_rgb = blend(bg, page) if bg[3] < 1 else bg[:3]
    fg_rgb = blend(fg, bg_rgb) if fg[3] < 1 else fg[:3]
    return _ratio(fg_rgb, bg_rgb)


def _ratio(a, b):
    l1, l2 = rel_lum(a), rel_lum(b)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def accent_ink(accent: str, ink: str) -> str:
    """按钮文字色：取黑/白/ink 中对比度最高的那个。"""
    cands = ["#ffffff", "#000000", ink]
    scored = [(contrast(c, accent) or 0, c) for c in cands]
    return max(scored)[1]


def badge(ratio):
    if ratio is None:
        return "  n/a"
    if ratio >= 7:
        return f"{ratio:5.1f} AAA"
    if ratio >= 4.5:
        return f"{ratio:5.1f} AA "
    if ratio >= 3:
        return f"{ratio:5.1f} AA>"
    return f"{ratio:5.1f} ✗  "


def dwidth(s: str) -> int:
    """终端显示宽度：中日韩字符按 2 列。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - dwidth(s))


# ---------------------------------------------------------------- 单个样例
def audit_demo(path: Path, style: dict):
    """返回 (错误列表, 警告列表, 指标字典)。错误/警告都带 文件:行 定位。"""
    errs, warns = [], []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{path.name}: 读取失败 {e}"], [], {}

    rel = path.relative_to(ROOT).as_posix()
    lines = text.splitlines()

    # 3. 自包含
    for i, line in enumerate(lines, 1):
        if re.search(r"https?://", line):
            errs.append(f"{rel}:{i} 出现外链（样例必须自包含）：{line.strip()[:60]}")
        if "<script" in line.lower():
            errs.append(f"{rel}:{i} 出现 <script>（默认样式里不允许脚本）：{line.strip()[:60]}")

    # 4. var 定义
    root_blocks = RE_ROOT.findall(text)
    defined = set()
    for b in root_blocks:
        defined.update(RE_VAR_DEF.findall(b))
    if not defined:
        errs.append(f"{rel}: 找不到 :root 里的变量定义")
    for i, line in enumerate(lines, 1):
        for name, has_fallback in RE_VAR_USE.findall(line):
            if name in defined or name in OPTIONAL_HOOKS:
                continue
            if has_fallback:
                warns.append(f"{rel}:{i} var(--{name}) 未在 :root 定义，靠兜底值工作")
            else:
                errs.append(f"{rel}:{i} var(--{name}) 没有定义也没有兜底值")

    # 指标
    px = sorted({float(v) for v in RE_FONT_PX.findall(text)} |
                {float(v) for v in RE_CLAMP_PX.findall(text)})
    t = style["tokens"]
    ink_bg = contrast(t["ink"], t["bg"])
    ink_surface = contrast(t["ink"], t["surface"], t["bg"] if parse_color(t["bg"])[3] < 1 else t["bg"])
    acc = contrast(accent_ink(t["accent"], t["ink"]), t["accent"])
    metrics = {
        "radius": t["radius"],
        "ink/bg": ink_bg,
        "ink/surface": ink_surface,
        "accent": acc,
        "font": px,
    }
    return errs, warns, metrics



# ---------------------------------------------------------------- 参考实现
REF_DIR = ROOT / "ref"
REF_CSS = ("tokens.css", "base.css", "components.css", "pages.css")
# 参考实现里允许的「自带兜底值」变量
REF_OPTIONAL = {"refnav-h"}


def audit_ref():
    """ref/<风格>/ 下：三份 CSS 必须存在，页面只能引用已定义的变量，且不许外链与脚本。

    返回 (页数, root 变量数, 错误, 警告)。
    """
    errs, warns = [], []
    if not REF_DIR.exists():
        return 0, 0, errs, warns

    pages = 0
    root_tokens = 0
    for folder in sorted(p for p in REF_DIR.iterdir() if p.is_dir()):
        defined, css_texts = set(), {}
        for name in REF_CSS:
            f = folder / name
            if not f.exists():
                errs.append(f"ref/{folder.name}: 缺少 {name}")
                continue
            text = f.read_text(encoding="utf-8")
            css_texts[f] = text
            defined |= set(RE_VAR_DEF.findall(text))
        tok = folder / "tokens.css"
        if tok.exists():
            blocks = RE_ROOT.findall(tok.read_text(encoding="utf-8"))
            root_tokens = max(root_tokens, len(RE_VAR_DEF.findall(blocks[0])) if blocks else 0)

        htmls = sorted(folder.glob("[0-9][0-9]-*.html"))
        if not htmls:
            errs.append(f"ref/{folder.name}: 没有任何页面")
        stale = sorted(p.name for p in folder.glob("*.html")
                       if not re.match(r"\d\d-", p.name))
        for s in stale:
            warns.append(f"ref/{folder.name}/{s}: 不以数字开头，未被参考实现收录")

        sources = dict(css_texts)
        for p in htmls:
            sources[p] = p.read_text(encoding="utf-8")
            pages += 1

        for path, text in sources.items():
            rel = path.relative_to(ROOT).as_posix()
            low = text.lower()
            if "<script" in low:
                errs.append(f"{rel}: 出现 <script>（参考实现也不许脚本）")
            for i, line in enumerate(text.splitlines(), 1):
                if re.search(r"https?://", line) and "www.w3.org" not in line:
                    errs.append(f"{rel}:{i} 出现外链：{line.strip()[:56]}")
                for vname, has_fb in RE_VAR_USE.findall(line):
                    if vname in defined or vname in REF_OPTIONAL:
                        continue
                    msg = f"{rel}:{i} var(--{vname}) 未在 tokens.css 定义"
                    (warns if has_fb else errs).append(msg)

        for name in REF_CSS:
            if name not in [f.name for f in css_texts]:
                continue
    return pages, root_tokens, errs, warns


def main() -> int:
    strict = "--strict" in sys.argv
    if not DATA.exists():
        print("缺少 styles.json，先跑 tools/gen_demos.py")
        return 1

    raw = DATA.read_text(encoding="utf-8")
    data = json.loads(raw)
    styles = data.get("styles", [])

    errs, warns = [], []
    if data.get("total") != len(styles):
        errs.append(f"styles.json: total={data.get('total')} 与条目数 {len(styles)} 不一致")
    if re.search(r"https?://", raw):
        errs.append("styles.json: 出现外链")

    seen = {}
    metrics_rows = []
    for s in styles:
        sid = s.get("id", "<无 id>")
        loc = f"styles.json[{sid}]"

        if sid in seen:
            errs.append(f"{loc}: id 重复")
        seen[sid] = s

        # 2. tokens
        tokens = s.get("tokens") or {}
        for k in REQUIRED_TOKENS:
            if not (tokens.get(k) or "").strip():
                errs.append(f"{loc}: tokens.{k} 缺失或为空")

        # 5. 文案
        feats = s.get("features") or []
        if len(feats) < 3:
            errs.append(f"{loc}: features 只有 {len(feats)} 条，至少 3 条")
        if len(set(feats)) != len(feats):
            errs.append(f"{loc}: features 有重复条目")
        for k in ("prompt", "avoid", "name", "name_en"):
            if not (s.get(k) or "").strip():
                errs.append(f"{loc}: {k} 为空")
        if not (s.get("sources") or []):
            errs.append(f"{loc}: sources 为空")
        if s.get("form") not in VALID_FORMS:
            errs.append(f"{loc}: form={s.get('form')!r} 不在 {sorted(VALID_FORMS)}")
        if s.get("layout") not in VALID_LAYOUTS:
            errs.append(f"{loc}: layout={s.get('layout')!r} 不在 {sorted(VALID_LAYOUTS)}")

        # 1. demo 文件
        demo = s.get("demo") or ""
        if demo != f"demos/{sid}.html":
            errs.append(f"{loc}: demo 路径应为 demos/{sid}.html，实际 {demo!r}")
        p = ROOT / demo if demo else None
        if p is None or not p.exists():
            errs.append(f"{loc}: 样例文件不存在 {demo}")
            continue

        e, w, m = audit_demo(p, s)
        errs += e
        warns += w
        if m:
            metrics_rows.append((sid, s.get("form", "?"), m))

    # 1. 目录与 json 一致
    on_disk = {p.name for p in DEMOS.glob("*.html")}
    in_json = {f"{k}.html" for k in seen}
    for extra in sorted(on_disk - in_json):
        errs.append(f"demos/{extra}: 磁盘上有，但 styles.json 里没有（跑一次 gen_demos.py？）")
    for miss in sorted(in_json - on_disk):
        errs.append(f"demos/{miss}: styles.json 里有，但磁盘上没有")

    # ---------------------------------------------------------------- 参考实现
    ref_pages, ref_tokens, ref_errs, ref_warns = audit_ref()
    errs += ref_errs
    warns += ref_warns

    # ---------------------------------------------------------------- 报告
    print("=" * 96)
    print(f"UI Atlas 校验 · {len(styles)} 条风格 / {len(on_disk)} 个样例文件"
          f" ＋ 参考实现 {ref_pages} 页 / {ref_tokens} 个 token")
    print("=" * 96)

    if warns:
        print(f"\n警告 {len(warns)} 条（不影响使用）：")
        for w in warns[:12]:
            print("  ! " + w)
        if len(warns) > 12:
            print(f"  … 另有 {len(warns) - 12} 条")

    if errs:
        print(f"\n错误 {len(errs)} 条：")
        for e in errs:
            print("  x " + e)
    else:
        print("\n错误 0 条 ✓")

    print("\n" + "-" * 96)
    print(pad("id", 26) + pad("形态", 8) + pad("圆角", 8) + pad("ink/bg", 10)
          + pad("ink/surf", 11) + pad("accent", 10) + "字号阶梯(px)")
    print("-" * 96)
    for sid, form, m in metrics_rows:
        ladder = " ".join(f"{v:g}" for v in m["font"][:8])
        print(pad(sid, 26) + pad(form, 8) + pad(m["radius"], 8)
              + pad(badge(m["ink/bg"]), 10) + pad(badge(m["ink/surface"]), 11)
              + pad(badge(m["accent"]), 10) + ladder)
    print("-" * 96)

    low = [(sid, m) for sid, _f, m in metrics_rows
           if m["ink/bg"] is not None and m["ink/bg"] < 3]
    if low:
        print("\n对比度低于 3:1（正文将不可读，建议复核）：")
        for sid, m in low:
            print(f"  · {sid}  ink/bg = {m['ink/bg']:.2f}")

    ok = not errs and (not strict or not warns)
    print("\n结论：" + ("通过" if ok else "未通过"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
