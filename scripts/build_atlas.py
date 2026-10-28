#!/usr/bin/env python3
"""把 riskpairs.json + entries/*.json 汇总成 atlas.json（客户端拉取的单文件产物）。

用法：
    python3 scripts/build_atlas.py            # 构建并写 atlas.json
    python3 scripts/build_atlas.py --check    # 只校验，不写（CI 用）

校验规则：
  - schema 必须为 1
  - entry 的 id 匹配 ^[a-z0-9][a-z0-9-]{4,63}$
  - entry 必须有 wrong / right / evidence / severity
  - severity ∈ {high, medium, low}
  - riskpair 的 a/b 均为单字
  - entry id 不重复
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = 1
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{4,63}$")
SEV = {"high", "medium", "low"}


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验不写文件")
    ap.add_argument("-o", "--out", default=str(ROOT / "atlas.json"))
    a = ap.parse_args()

    errors: list[str] = []

    # ---- riskpairs ----
    rp_file = ROOT / "riskpairs.json"
    if not rp_file.exists():
        fail("缺少 riskpairs.json", errors)
        pairs = []
    else:
        rp = json.loads(rp_file.read_text(encoding="utf-8"))
        if rp.get("schema") != SCHEMA:
            fail(f"riskpairs.json schema 应为 {SCHEMA}", errors)
        pairs = rp.get("riskpairs", [])
        seen = set()
        for i, p in enumerate(pairs):
            if len(str(p.get("a", ""))) != 1 or len(str(p.get("b", ""))) != 1:
                fail(f"riskpairs[{i}] 的 a/b 必须为单字：{p}", errors)
            key = (p.get("a"), p.get("b"))
            if key in seen:
                fail(f"riskpairs 重复：{key}", errors)
            seen.add(key)

    # ---- entries ----
    entries_dir = ROOT / "entries"
    entries, ids = [], set()
    for f in sorted(entries_dir.glob("*.json")) if entries_dir.exists() else []:
        try:
            e = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{f.name} JSON 解析失败：{exc}", errors)
            continue
        eid = e.get("id", "")
        if not ID_RE.match(str(eid)):
            fail(f"{f.name}: id 不合规（{eid!r}），应为小写字母数字连字符，5–64 字符", errors)
        if eid in ids:
            fail(f"{f.name}: id 重复 {eid}", errors)
        ids.add(eid)
        for req in ("wrong", "right", "evidence"):
            if not e.get(req):
                fail(f"{f.name}: 缺 {req}", errors)
        if e.get("severity") not in SEV:
            fail(f"{f.name}: severity 应为 {sorted(SEV)}，实际 {e.get('severity')!r}", errors)
        entries.append(e)

    if not entries:
        fail("entries/ 为空，至少要有一条案例", errors)

    if errors:
        print("校验失败：", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    if a.check:
        print(f"校验通过：riskpairs={len(pairs)}  entries={len(entries)}")
        return 0

    now = datetime.now(timezone.utc).astimezone()
    atlas = {
        "schema": SCHEMA,
        "version": now.strftime("%Y.%m.%d.") + str(len(entries)),
        "updated": now.isoformat(timespec="seconds"),
        "note": "由 scripts/build_atlas.py 从 riskpairs.json + entries/ 生成，请勿手改",
        "riskpairs": [{"a": p["a"], "b": p["b"], "high": bool(p.get("high")), **(
            {"note": p["note"]} if p.get("note") else {})} for p in pairs],
        "entries": sorted(entries, key=lambda x: x["id"]),
    }
    out = Path(a.out)
    out.write_text(json.dumps(atlas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"已生成 {out.name}：version={atlas['version']} "
          f"riskpairs={len(atlas['riskpairs'])} entries={len(atlas['entries'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
