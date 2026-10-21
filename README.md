# AI Toolkit

我每天在用的 Claude Code skills 和提示词。规则都写成文件，换台机器、换个客户端，拷过去就能用。

仓库按「单 skill 一目录」组织，每个 `SKILL.md` 都能单独取用。手机端如果只认 raw 链接，读根目录的 [`manifest.json`](manifest.json) 即可拿到全部路径。

## 手机端怎么取

直接转发给手机 DSH 的说明见 [`PHONE.md`](PHONE.md)。速查：

| 方式 | 地址 |
|---|---|
| 清单 | `https://raw.githubusercontent.com/la1379/ai-toolkit/main/manifest.json` |
| 单个 skill | `https://raw.githubusercontent.com/la1379/ai-toolkit/main/skills/<name>/SKILL.md` |
| 整仓克隆 | `git clone https://github.com/la1379/ai-toolkit.git` |

`manifest.json` 里每一项都有 `path`、`raw`、`raw_proxy` 三个字段；客户端不支持枚举时，先拉清单再按 `path` 取。

### 国内网络

本机实测 `raw.githubusercontent.com` 和 jsDelivr 都不通，`gh-proxy.com` 可直取。所有 raw 地址前加
`https://gh-proxy.com/` 即可：

```text
https://gh-proxy.com/https://raw.githubusercontent.com/la1379/ai-toolkit/main/manifest.json
```

`manifest.json` 的 `raw_proxy` 字段已经是拼好的代理地址。代理是第三方公共服务，失效时回退到官方 raw 或 `git clone`。

## 公开与私有

本仓库只放通用技能。带本机路径、个人背景、账号习惯的内容在私有仓库 `ai-toolkit-private`。

2026-10-19 做过一次拆分：个人画像、含本机路径的踩坑记录、代理工具名从本仓库移除，
公开版里保留的是抹掉路径后的通用说法。

## 目录

```text
skills/
  new-project/              做项目的 SOP：骨架、核实、流水线、断言、收尾
  bili-learn/               B 站收藏 → 可消化的学习条目（scripts/ 带 3 个零 token 脚本）
  shuorenhua-slop/          严格去 AI 腔的避雷清单
  investment-review/        炒股流程核查与交易复盘（不荐股）
  hamiji/                   哈基米聊天风格（仅显式触发）
  big-assignment-format/    车辆/机械类课程文档格式
  exam-review-color/        彩色重点版复习资料
  exam-review-closed-book/   闭卷简答题模拟题集
```

## Skills 一览

| Skill | 解决什么 | 触发词 |
|---|---|---|
| `new-project` | 把新需求拆成可验收的项目流程，控制 token 成本 | 开新项目、做项目、按流程来 |
| `bili-learn` | 把 B 站收藏/链接变成带分级的学习条目 | 学习待办、收割收藏、这条归哪级 |
| `shuorenhua-slop` | 清掉卖点堆叠、小剧场、否定递进等 AI 腔 | 避雷、严格去 AI 味 |
| `investment-review` | 查公告、做交易复盘、识别荐股套路 | 复盘、这只票、这消息真假 |
| `hamiji` | 短句、带梗的聊天人格 | 哈基米、hamiji 模式 |
| `big-assignment-format` | 课程设计/实验报告/说明书的格式规范 | 大作业、课程设计、排版 |
| `exam-review-color` | 彩色重点版复习资料，10 段固定结构 | 彩色重点版、分层精讲版 |
| `exam-review-closed-book` | 闭卷简答题模拟题集 + 旧资料补全 | 闭卷简答题、模拟题集 |

## 安装

Linux / macOS / Git Bash：

```bash
git clone https://github.com/la1379/ai-toolkit.git
cp -r ai-toolkit/skills/* ~/.claude/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/la1379/ai-toolkit.git
Copy-Item -Recurse -Force ai-toolkit\skills\* "$HOME\.claude\skills\"
```

只想用某一个：把对应目录整个拷进 `~/.claude/skills/` 即可，skill 名就是目录名。

## 使用前提

- `bili-learn` 需要 `@xzxzzx/bilibili-mcp` 和 B 站 Cookie。
- `exam-review-*` 和 `big-assignment-format` 只依赖模型本身；生成 Word 时需要 `docx` 能力或 python-docx。

## 设计原则

1. 规则写进文件，执行期不靠记忆。
2. 先定验收标准，再动手；没有断言的结果不算完成。
3. 能脚本做的零 token，模型只做判断和写作。
4. 密钥、Cookie、绝对路径、真实姓名、学号不入库。

## 没有收录什么

第三方 skill（docx / pptx / xlsx / pdf / ppt-master / agent-reach / humanizer-zh 等）有各自的许可证，这里只放链接指路，不复制正文。

## License

- 脚本与代码：MIT，见 [`LICENSE`](LICENSE)。
- Skills 与提示词正文：CC BY 4.0，见 [`LICENSE-prompts`](LICENSE-prompts)。
