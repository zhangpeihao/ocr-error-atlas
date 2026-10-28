# OCR 误判经验库（ocr-error-atlas）

扫描件 OCR 的单字误识经验表，供 [ocr-proofread](https://github.com/<owner>/ocr-proofread) 技能拉取使用。

**这不是通用字典，是踩过的坑。** 每条案例都要求能追到"哪份文件的哪一页、原图长什么样"，没有证据的猜测不收。

## 它解决什么问题

OCR 引擎把「債項」输出成「償項」、把「超逾」输出成「超過」、把「入會」输出成「人會」——这类错误单个看不要紧，但法律文书的条文一旦错一个字，可能改变整个条款的性质。自动比对能发现大部分，剩下一部分要靠"这类字以前错过"的先验知识去定向盯。

这份库就是那个先验知识。

## 怎么用

技能端不需要 clone 本仓库，直接拉构建产物：

```bash
# 一次性接上（把 <owner> 换成实际账号后写进 sources 配置）
python3 scripts/atlas.py sync --source https://raw.githubusercontent.com/<owner>/ocr-error-atlas/main/atlas.json
python3 scripts/atlas.py sync --source https://raw.githubusercontent.com/<owner>/ocr-error-atlas/main/atlas.json --apply
```

或者把地址填进技能的 `references/atlas.sources.json`，之后 `atlas.py sync` 会自动按序尝试（GitHub 不通时回退 Gitee）。

拉下来的是 `riskpairs.remote.txt`，技能优先读它；删掉即回退到技能自带的本地基线。

## 仓库结构

```
atlas.json          构建产物，客户端拉这个（勿手改，CI 生成）
riskpairs.json      形近字对清单（人工维护）
entries/            案例，一条一个文件（PR 友好，避免冲突）
schema/             协议定义
scripts/build_atlas.py  汇总 + 校验
```

改任何内容都要落到 `riskpairs.json` 或 `entries/`，`atlas.json` 由 CI 重建。

## 两类数据

**riskpairs** — 形近字对，回答"哪两个字容易混"。`high: true` 表示出现即强制人工核对（术语级，错一字改变含义）；低危的只做统计抽样。

**entries** — 具体案例，回答"这个字在哪份文件被错成了什么、依据是什么"。前者是索引，后者是证据。

**方法** — 见 [METHOD.md](METHOD.md)：怎么判字形、什么时候不能信引擎票数、哪些简体字不能动、等长替换原则。案例库解决"盯哪里"，方法备忘解决"凭什么是这个字"。

## 贡献

欢迎提 PR。规范见 [CONTRIBUTING.md](CONTRIBUTING.md)。

简版要求：
1. 必须有原图依据（不是靠语境猜的）
2. 必须写明该字对能否全局替换（「償→債」不能，因为「清償/賠償」的「償」是对的）
3. 一条一个文件，放 `entries/`，CI 自动校验
4. PR 只加文件，不要改 `atlas.json`

## 目前覆盖

| 项 | 数量 |
|---|---|
| 形近字对 | 32 对（高危 13 / 低危 19），见 `riskpairs.json` |
| 案例 | 20 条，覆盖 8 类字对；单一最大样本为 23 份香港中醫公會章程（510 页 / 10.2 万汉字） |
| 语种 | 繁體中文（香港法律/公司文书）为主 |
| 主引擎 | unlimited-ocr v2；交叉验证 MinerU、Tesseract chi_tra |
| 方法论 | [METHOD.md](METHOD.md)（三引擎同错实证、字形相似度为何不可用、等长替换、简体白名单） |

## 免责

经验库只能把"已知的坑"标出来，**不能保证漏掉的都对**。实测中存在三个引擎同时对同一处犯同样错误的情况（例如「入」被一致判成「人」），这类只能靠人眼复核。要作条文引证的材料，请对高危条款另做人工对读。

## 许可

数据部分建议 CC BY 4.0，脚本 MIT。使用前请按实际需要调整 [LICENSE](LICENSE)。
