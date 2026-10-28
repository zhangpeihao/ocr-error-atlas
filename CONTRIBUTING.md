# 贡献指南

## 提交前自查

一条案例要被合并，至少满足：

- [ ] **有原图依据。** evidence 里写清怎么核的（如「原图 p6 300dpi 放大 8 倍，右半为『責』」），不接受"根据上下文应该是"。
- [ ] **写清能否全局替换。** 这是最容易出事的点：
  - 「償→債」**不能**全局替换——同一文档里「清償」「賠償」「彌償」的「償」全是正确的
  - 「註→注」**不能**全局替换——「注意」是正确用法
  - 能全局替换的（如纯简体混入的「册→冊」）要在 evidence 里明确说明
- [ ] **区分 OCR 错与原件笔误。** 若原图本身就印错（如该印「任何」却印成「任可」），不要当作 OCR 错提交，另开 issue 或在该条 evidence 里注明。
- [ ] **不重复。** 先搜 `entries/` 和 `riskpairs.json`，同一字对同一语境已有记录就不必再加。

## 加一条案例

在 `entries/` 下新建 `<id>.json`：

```json
{
  "id": "hkicharity-8f3a1c",
  "lang": "zh-Hant",
  "domain": "hkicharity",
  "wrong": "償",
  "right": "債",
  "contexts": ["債項", "債權證"],
  "severity": "high",
  "occurrences": 4,
  "evidence": "原图 p6/p13 三处「債項」、p15 一处「債權證」；Tesseract 与 MinerU 均判「債」",
  "case_doc": "香港華夏醫藥學會慈善基金有限公司 章程",
  "case_page": "6, 13, 15",
  "reported_at": "2026-10-27",
  "reporter": "your-id",
  "confirmed_by": "300dpi 原图 8x 放大 + 同页同字体对照"
}
```

字段要求：

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✓ | 小写字母/数字/连字符，5–64 字符。可用 `atlas.py contribute` 自动生成 |
| `wrong` / `right` | ✓ | 引擎输出 vs 原件正确字。字或词均可 |
| `evidence` | ✓ | 至少 10 字，须可复核 |
| `severity` | ✓ | `high` / `medium` / `low`。high = 术语级，错一字改变含义 |
| `contexts` | | 出现该词的具体搭配，便于检索 |
| `occurrences` | | 在来源文档中出现的次数 |
| `case_doc` / `case_page` | | 出处。**公开提交时请勿放未脱敏的客户文件全文** |

## 加一个字对

编辑 `riskpairs.json` 的 `riskpairs` 数组：

```json
{"a": "債", "b": "償", "high": true, "note": "債項/債權證 vs 償付/清償 —— 主引擎系统性把「債」输出成「償」"}
```

- `high: true` 才会让客户端强制核对，务必慎用——滥用会把所有正常文本都推进人工队列
- `note` 写清为什么容易混、错在哪类词上，别只写"易混"

## 自动生成 PR 材料

在本机勘错完一轮后：

```bash
python3 scripts/atlas.py contribute --from-fixes fixes.json \
    --doc "某公司章程" --pages "6,13" --domain hkicharity
```

会在 `atlas-pr/` 下生成 `entries/*.json` 和现成的 `PULL_REQUEST.md`，把条目复制进本仓库 `entries/` 即可提 PR。工具不会自动推送。

## CI 会做什么

PR 提交后自动：

1. 校验所有 json（字段、id 格式、severity 枚举、字对是否单字、id 是否重复）
2. 全部通过后重建 `atlas.json` 并提交回主分支

校验失败会在 PR 里显示具体哪一条、错在哪。

## 分支与提交信息

- 分支名 `add/<id>` 或 `fix/<id>`
- 提交信息 `add: <wrong>→<right> in <context>`，如 `add: 償→債 in 債項`
