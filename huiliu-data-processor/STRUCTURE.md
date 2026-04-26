# 项目文件结构

```
huiliu-data-processor/
│
├── 📄 核心文件
│   ├── process.py                  主处理脚本（V2.4，~780行，17规则）
│   ├── README.md                   使用指南
│   ├── CHANGELOG.md                更新日志
│   ├── SKILL.md                    Skill 配置
│   ├── PROJECT_OVERVIEW.md         项目总览
│   ├── STRUCTURE.md                本文件（项目结构说明）
│   └── config.json                 配置文件
│
├── 📁 docs/                        详细文档目录
│   ├── README.md                   文档目录说明
│   ├── CHANGELOG_V2.2.md           V2.2 详细更新日志
│   ├── CHANGELOG_V2.3.md           V2.3 详细更新日志
│   ├── CHANGELOG_V2.4.md           V2.4 详细更新日志
│   └── SUMMARY_FINAL_V2.4.md       完整项目总结
│
├── 📁 tests/                       测试文件目录
│   ├── README.md                   测试说明文档
│   ├── test_new_rules.jsonl        规则 10-12 测试数据
│   ├── test_refund_overpromise.jsonl  规则 13 测试数据
│   ├── test_claim_human.jsonl      规则 14 测试数据
│   ├── test_call_escalate.jsonl    规则 15-16 测试数据
│   ├── test_xiaoxiang_refund.jsonl 规则 17 测试数据
│   └── test_*_output.jsonl         测试输出文件
│
├── 📁 archive/                     归档目录
│   ├── README.md                   归档说明文档
│   ├── process.py                  V1 旧脚本
│   ├── filters.py                  V1 过滤规则
│   ├── README.md                   V1 文档
│   └── CHANGELOG_V2*.md            中间版本文档
│
├── 📁 scripts/                     工具脚本
│   ├── validate.py                 快速验证文件格式
│   ├── sample.py                   随机抽样
│   └── analyze.py                  统计分析
│
├── 📁 utils/                       工具模块
│   ├── __init__.py
│   ├── parser.py                   数据解析（TSV/JSON）
│   ├── validator.py                数据验证
│   ├── formatter.py                数据格式化
│   ├── statistics.py               统计信息收集
│   └── README.md                   模块说明
│
└── 📁 examples/                    示例文件
    ├── input_sample.txt            输入示例
    └── output_sample.jsonl         输出示例
```

## 文件说明

### 根目录文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `process.py` | 主处理脚本，包含 17 个过滤规则 | ~28KB |
| `README.md` | 使用指南，快速上手文档 | ~5KB |
| `CHANGELOG.md` | 更新日志，版本历史 | ~4KB |
| `SKILL.md` | Skill 配置文件 | ~11KB |
| `PROJECT_OVERVIEW.md` | 项目总览 | ~3KB |
| `config.json` | 配置文件 | ~271B |

### 子目录

| 目录 | 说明 | 文件数 |
|------|------|--------|
| `docs/` | 详细文档和版本历史 | 5 个 |
| `tests/` | 测试文件和测试输出 | 11 个 |
| `archive/` | 旧版本文件归档 | 8 个 |
| `scripts/` | 工具脚本 | 3 个 |
| `utils/` | 工具模块 | 5 个 |
| `examples/` | 示例文件 | 2 个 |

## 快速导航

### 我想...

**开始使用**
→ 阅读 `README.md`

**查看更新历史**
→ 阅读 `CHANGELOG.md`

**了解详细规则**
→ 阅读 `docs/CHANGELOG_V2.4.md`

**查看完整项目总结**
→ 阅读 `docs/SUMMARY_FINAL_V2.4.md`

**运行测试**
→ 查看 `tests/README.md`

**查看旧版本**
→ 查看 `archive/README.md`

**了解工具模块**
→ 查看 `utils/README.md`

## 项目统计

- **版本**: V2.4
- **规则数**: 17 个
- **测试用例**: 31 个（100% 通过率）
- **代码行数**: ~780 行
- **文档文件**: 清晰分类，易于查找
- **开发时间**: 2026-03-24（1天）

---

**最后更新**: 2026-03-24
**作者**: Claude
**用户**: liliz (zhaolili08)
