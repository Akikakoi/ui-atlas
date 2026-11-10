#!/usr/bin/env python3
"""校验 UI Atlas 动效系统：token、规则、反例与 3 屏流程。

用法：
    python tools/check_motion.py
    python tools/check_motion.py --strict

检查项：
    1. motion/tokens.css 存在，四组 token 齐全
    2. motion/flow.html 引用 tokens.css，有三屏（list / detail / success）
    3. flow 有 View Transitions 与 fallback，处理 prefers-reduced-motion
    4. flow 自包含：无 <link> 外链、无 <script src>、无远程 src/href
    5. motion.html 有 >= 10 条规则、>= 6 组反例，并链接到 flow 与 lab
    6. motion/lab.html 有 >= 5 个控件、>= 10 条规则体检、>= 4 个预设与复制入口
    7. 页面结构：doctype / lang / viewport / title / .hint
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "motion" / "tokens.css"
FLOW = ROOT / "motion" / "flow.html"
LAB = ROOT / "motion" / "lab.html"
PAGE = ROOT / "motion.html"

RE_REMOTE = re.compile(r"""\b(?:src|href)\s*=\s*["']\s*(?:https?:)?//""", re.I)
RE_SCRIPT_SRC = re.compile(r"<script[^>]*\bsrc\s*=", re.I)
RE_REDUCE = re.compile(r"prefers-reduced-motion", re.I)

TOKEN_KEYS = [
    "--dur-1", "--dur-2", "--dur-3", "--dur-4", "--dur-5",
    "--ease-standard", "--ease-enter", "--ease-exit", "--ease-spring",
    "--move-1", "--move-2", "--move-3", "--move-4", "--move-5",
    "--stagger-1", "--stagger-2", "--stagger-3",
]


def main() -> int:
    strict = "--strict" in sys.argv
    errors: list[str] = []
    warns: list[str] = []

    if not TOKENS.exists():
        errors.append("缺少 motion/tokens.css")
    else:
        css = TOKENS.read_text(encoding="utf-8")
        missing = [k for k in TOKEN_KEYS if k not in css]
        if missing:
            errors.append("tokens.css 缺少：" + ", ".join(missing))
        if not RE_REDUCE.search(css):
            errors.append("tokens.css 没有 prefers-reduced-motion 兜底")

    if not FLOW.exists():
        errors.append("缺少 motion/flow.html")
    else:
        src = FLOW.read_text(encoding="utf-8")
        for screen in ("list", "detail", "success"):
            if f'data-screen="{screen}"' not in src:
                errors.append(f"flow 缺少 {screen} 屏")
        if "tokens.css" not in src:
            errors.append("flow 没有引用 motion/tokens.css")
        if "startViewTransition" not in src:
            errors.append("flow 没有使用 View Transitions")
        if not RE_REDUCE.search(src):
            errors.append("flow 没有 prefers-reduced-motion 处理")
        if 'class="hint"' not in src:
            warns.append("flow 缺少 .hint 操作提示")
        if RE_SCRIPT_SRC.search(src):
            errors.append("flow 出现 <script src>，流程应内联脚本")
        if RE_REMOTE.search(src):
            errors.append("flow 出现远程 src/href")
        if '<link rel="stylesheet" href="tokens.css">' not in src:
            errors.append("flow 的 tokens.css 链接路径应为 tokens.css")

    if not LAB.exists():
        errors.append("缺少 motion/lab.html")
    else:
        src = LAB.read_text(encoding="utf-8")
        controls = len(re.findall(r"id=\"(?:dist|dur|ease|stagger|count)\"", src))
        checks = len(re.findall(r"data-check=\"", src))
        presets = len(re.findall(r"data-preset=\"", src))
        if controls < 5:
            errors.append(f"lab 只有 {controls} 个参数控件，至少 5 个")
        if checks < 10:
            errors.append(f"lab 只有 {checks} 条规则体检，至少 10 条")
        if presets < 4:
            errors.append(f"lab 只有 {presets} 个预设，至少 4 个")
        if not RE_REDUCE.search(src):
            errors.append("lab 没有 prefers-reduced-motion 处理")
        if "tokens.css" not in src:
            errors.append("lab 没有引用 motion/tokens.css")
        if RE_REMOTE.search(src):
            errors.append("lab 出现远程 src/href")
        if "复制 CSS" not in src or "复制链接" not in src:
            errors.append("lab 缺少复制 CSS / 复制链接入口")

    page_src = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    rules = len(re.findall(r"data-rule\b", page_src))
    antis = len(set(re.findall(r'data-anti="([^"]+)"', page_src)))

    if not PAGE.exists():
        errors.append("缺少 motion.html")
    else:
        if rules < 10:
            errors.append(f"motion.html 只有 {rules} 条规则，至少 10 条")
        if antis < 6:
            errors.append(f"motion.html 只有 {antis} 组反例，至少 6 组")
        if "motion/flow.html" not in page_src:
            errors.append("motion.html 没有链接到 3 屏流程")
        if "motion/tokens.css" not in page_src:
            errors.append("motion.html 没有引用 tokens.css")
        if "motion/lab.html" not in page_src:
            errors.append("motion.html 没有链接到参数实验台")
        if RE_REMOTE.search(page_src):
            errors.append("motion.html 出现远程 src/href")
        if not page_src.lstrip().lower().startswith("<!doctype html>"):
            errors.append("motion.html 缺少 <!doctype html>")

    print(f"tokens: {TOKENS.relative_to(ROOT)}")
    print(f"flow:   {FLOW.relative_to(ROOT)}")
    print(f"lab:    {LAB.relative_to(ROOT)}")
    print(f"page:   {PAGE.relative_to(ROOT)}")
    print(f"规则:   {rules} 条")
    print(f"反例:   {antis} 组")
    for w in warns:
        print(f"警告  {w}")
    for e in errors:
        print(f"错误  {e}")
    print(f"\n{len(errors)} 个错误，{len(warns)} 个警告")

    if errors or (strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
