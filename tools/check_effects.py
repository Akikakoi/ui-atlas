#!/usr/bin/env python3
"""校验 UI Atlas 动效图鉴：effects.json 与 effects/*.html 是否一一对得上。

用法：
    python tools/check_effects.py            # 只报告
    python tools/check_effects.py --strict    # 有警告也算失败

检查项：
    1. total 与条目数一致；id 唯一；cat / trigger / level 取值合法
    2. effects.json 与 effects/ 目录一一对应，demo 路径存在
    3. 每条文案完整：features >= 2、how / watch / tech / tags 非空
    4. 深度档案完整：anatomy >= 3、params >= 3、variants >= 2、cost 合法、avoid 非空
    5. 机制归档完整：family 合法；variant_of 指向同族的已有条目
    6. 样例自包含：无 <link>、无 <script src>、无外链 src/href、无 @import
    7. 样例结构：doctype、lang、viewport、title、.hint 操作提示
    8. 无障碍：必须处理 prefers-reduced-motion
最后打印每条效果的行数、体积、是否含 JS、是否声明 reduced-motion。

退出码：0 通过；1 有错误（--strict 时含警告）。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FX_DIR = ROOT / "effects"
DATA = ROOT / "effects.json"

VALID_CATS = {"pointer", "scroll", "type", "layout", "feedback", "bg", "transition"}
VALID_TRIGGERS = {"hover", "scroll", "click", "view", "load", "auto", "drag"}
VALID_FAMILIES = {
    "pointer-field", "cursor-chrome", "direct-drag", "scroll-progress",
    "text-sequence", "layout-reflow", "entrance-stagger", "state-feedback",
    "ambient-bg", "view-transition",
}

RE_LINK = re.compile(r"<link\b", re.I)
RE_SCRIPT_SRC = re.compile(r"<script[^>]*\bsrc\s*=", re.I)
RE_REMOTE_ATTR = re.compile(r"""\b(?:src|href)\s*=\s*["']\s*(?:https?:)?//""", re.I)
RE_IMPORT = re.compile(r"@import\b", re.I)
RE_REDUCE = re.compile(r"prefers-reduced-motion", re.I)
RE_SCRIPT = re.compile(r"<script>([\s\S]*?)</script>", re.I)
RE_STYLE = re.compile(r"<style>([\s\S]*?)</style>", re.I)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def main() -> int:
    strict = "--strict" in sys.argv
    errors: list[str] = []
    warns: list[str] = []

    if not DATA.exists():
        print(f"缺少 {DATA}")
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))
    effects = data.get("effects", [])
    total = data.get("total")

    if total != len(effects):
        fail(errors, f"total={total} 与条目数 {len(effects)} 不一致")

    cats = data.get("cats", [])
    cat_ids = {c.get("id") for c in cats}
    if cat_ids != VALID_CATS:
        fail(errors, f"cats 与约定不一致：{sorted(cat_ids)}")

    families = data.get("families", [])
    family_ids = {f.get("id") for f in families}
    if family_ids != VALID_FAMILIES:
        fail(errors, f"families 与约定不一致：{sorted(family_ids)}")
    for f in families:
        if not str(f.get("name", "")).strip() or not str(f.get("note", "")).strip():
            fail(errors, f"family {f.get('id')}: name / note 不能为空")

    seen: set[str] = set()
    family_of: dict[str, str] = {}
    rows = []
    for e in effects:
        eid = e.get("id", "<无 id>")
        if not eid or not re.fullmatch(r"[a-z][a-z0-9-]*", eid):
            fail(errors, f"{eid}: id 必须是 kebab-case 小写")
        if eid in seen:
            fail(errors, f"{eid}: id 重复")
        seen.add(eid)

        if e.get("cat") not in VALID_CATS:
            fail(errors, f"{eid}: cat 非法（{e.get('cat')}）")
        if e.get("trigger") not in VALID_TRIGGERS:
            fail(errors, f"{eid}: trigger 非法（{e.get('trigger')}）")
        if e.get("level") not in (1, 2, 3):
            fail(errors, f"{eid}: level 只能是 1/2/3")
        if e.get("family") not in VALID_FAMILIES:
            fail(errors, f"{eid}: family 非法（{e.get('family')}）")
        else:
            family_of[eid] = e["family"]

        for key in ("name", "name_en", "how", "watch", "demo"):
            if not str(e.get(key, "")).strip():
                fail(errors, f"{eid}: {key} 为空")
        if len(e.get("features") or []) < 2:
            fail(errors, f"{eid}: features 至少 2 条")
        if not (e.get("tech") or []):
            fail(errors, f"{eid}: tech 为空")
        if not (e.get("tags") or []):
            fail(errors, f"{eid}: tags 为空（搜索会少一路入口）")

        depth = e.get("depth") or {}
        anatomy = depth.get("anatomy") or []
        params = depth.get("params") or []
        variants = depth.get("variants") or []
        cost = depth.get("cost") or {}
        if len(anatomy) < 3:
            fail(errors, f"{eid}: depth.anatomy 至少 3 条")
        if len(params) < 3:
            fail(errors, f"{eid}: depth.params 至少 3 组")
        else:
            for p in params:
                if not isinstance(p, list) or len(p) != 2 or not all(str(x).strip() for x in p):
                    fail(errors, f"{eid}: depth.params 每项必须是 [名称, 值]")
                    break
        if len(variants) < 2:
            fail(errors, f"{eid}: depth.variants 至少 2 条")
        else:
            for v in variants:
                if not isinstance(v, list) or len(v) != 2 or not all(str(x).strip() for x in v):
                    fail(errors, f"{eid}: depth.variants 每项必须是 [名称, 说明]")
                    break
        if not isinstance(cost, dict) or cost.get("tier") not in {"低", "中", "高"}:
            fail(errors, f"{eid}: depth.cost.tier 只能是 低/中/高")
        if not str(depth.get("avoid", "")).strip():
            fail(errors, f"{eid}: depth.avoid 为空")

        demo = e.get("demo", "")
        path = ROOT / demo
        if demo != f"effects/{eid}.html":
            fail(errors, f"{eid}: demo 路径应为 effects/{eid}.html（当前 {demo}）")
        if not path.exists():
            fail(errors, f"{eid}: 缺少文件 {demo}")
            continue

        src = path.read_text(encoding="utf-8")
        if not src.lstrip().lower().startswith("<!doctype html>"):
            fail(errors, f"{eid}: 缺少 <!doctype html>")
        if 'lang="zh-CN"' not in src:
            fail(errors, f"{eid}: <html> 缺少 lang=\"zh-CN\"")
        if "name=\"viewport\"" not in src and "name='viewport'" not in src:
            fail(errors, f"{eid}: 缺少 viewport")
        if "<title>" not in src:
            fail(errors, f"{eid}: 缺少 <title>")
        if 'class="hint"' not in src:
            fail(errors, f"{eid}: 缺少 .hint 操作提示，预览里的人不知道该怎么玩")
        if RE_LINK.search(src):
            fail(errors, f"{eid}: 出现 <link>，样例必须自包含")
        if RE_SCRIPT_SRC.search(src):
            fail(errors, f"{eid}: 出现 <script src>，样例必须自包含")
        if RE_REMOTE_ATTR.search(src):
            fail(errors, f"{eid}: 出现远程 src/href")
        if RE_IMPORT.search(src):
            fail(errors, f"{eid}: 出现 @import")
        if not RE_REDUCE.search(src):
            warns.append(f"{eid}: 没有 prefers-reduced-motion 处理")

        js = RE_SCRIPT.search(src)
        css = RE_STYLE.search(src)
        if e.get("cat") == "bg" and "<canvas" in src and js and "requestAnimationFrame" in js.group(1) and "visibilitychange" not in js.group(1):
            warns.append(f"{eid}: 背景 canvas 的 rAF 没有 visibilitychange 暂停")
        if not css:
            fail(errors, f"{eid}: 没有 <style>，样式应内联")
        if len(src.encode("utf-8")) > 40 * 1024:
            warns.append(f"{eid}: 文件超过 40KB")

        rows.append(
            (
                eid,
                e.get("cat", ""),
                len(src.splitlines()),
                len(src.encode("utf-8")) / 1024,
                len(js.group(1).splitlines()) if js else 0,
                "yes" if js else "no",
                "yes" if RE_REDUCE.search(src) else "NO",
            )
        )

    for e in effects:
        vo = e.get("variant_of")
        if not vo:
            continue
        eid = e.get("id", "<无 id>")
        if vo == eid:
            fail(errors, f"{eid}: variant_of 不能指向自己")
        elif vo not in family_of:
            fail(errors, f"{eid}: variant_of 指向不存在的条目（{vo}）")
        elif family_of[vo] != e.get("family"):
            fail(errors, f"{eid}: variant_of 必须与目标同族（{family_of[vo]} ≠ {e.get('family')}）")

    # 目录里多出来的文件
    if FX_DIR.exists():
        on_disk = {p.name for p in FX_DIR.glob("*.html")}
        missing = on_disk - {f"{e.get('id')}.html" for e in effects}
        for name in sorted(missing):
            warns.append(f"effects/{name} 没有登记在 effects.json")

    width = max([len(r[0]) for r in rows] or [10])
    print(f"\n{'id'.ljust(width)}  {'cat'.ljust(10)} {'行':>5} {'KB':>6} {'JS':>5} {'动效':>6} {'JS行':>5}")
    print("-" * (width + 46))
    for eid, cat, lines, kb, js_lines, has_js, motion in rows:
        print(f"{eid.ljust(width)}  {cat.ljust(10)} {lines:>5} {kb:>6.1f} {has_js:>5} {motion:>6} {js_lines:>5}")

    print(f"\n共 {len(rows)} 条效果 · {len(cat_ids)} 个类别")
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
