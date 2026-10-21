# 手机端接入（DSH / 任意能联网读文本的客户端）

这个仓库不是 App，不需要安装。它是一组文本文件；手机端只要能读 URL 或 clone，就能用。

## 先确认能读到清单

把下面这段直接发给手机上的 DSH：

```text
请读取这个清单并确认能访问：
https://gh-proxy.com/https://raw.githubusercontent.com/la1379/ai-toolkit/main/manifest.json

规则：
1. 清单里的 skills 数组每项有 name、path、raw_proxy。
2. 我点名某个 skill 时，你按 raw_proxy 取它的 SKILL.md，按里面的规则执行。
3. 一次只取一个，不要全量下载，不要把清单原文打印给我。
4. gh-proxy 取不到就换官方 raw 地址；都不通就直说，不要猜。

现在告诉我：一共几个 skill，分别叫什么。
```

读到清单后，`skills` 里是这 8 个：`new-project`、`bili-learn`、`shuorenhua-slop`、`investment-review`、`hamiji`、`big-assignment-format`、`exam-review-color`、`exam-review-closed-book`。

## 只用一个 skill

如果 DSH 不支持清单，直接让它读单个文件：

```text
请读取这个 skill，并按里面的规则工作：
https://gh-proxy.com/https://raw.githubusercontent.com/la1379/ai-toolkit/main/skills/new-project/SKILL.md
```

把 `new-project` 换成你要的那个名字。常用的：

```text
new-project              做项目流程
shuorenhua-slop          严格去 AI 味
investment-review        股票复盘
big-assignment-format    课程文档格式
exam-review-color        彩色复习资料
exam-review-closed-book  闭卷简答题
bili-learn               B 站收藏整理
hamiji                   哈基米聊天风格
```

## 如果 DSH 支持 git

```bash
git clone https://github.com/la1379/ai-toolkit.git
```

然后把 `skills/<name>/SKILL.md` 指给它。用 tag 可以固定版本：

```bash
git clone --branch v1.0.1 https://github.com/la1379/ai-toolkit.git
```

## 手机上哪些能真跑

| 类型 | Skill | 条件 |
|---|---|---|
| 只读文本就能用 | `new-project`、`shuorenhua-slop`、`investment-review`、`hamiji`、`big-assignment-format`、`exam-review-color`、`exam-review-close-book` | 模型能读中文指令即可 |
| 需要运行环境 | `bili-learn` | B 站 MCP、Node.js、B 站 Cookie |

拿不准就先从 `new-project` 或 `shuorenhua-slop` 试：这两个不依赖任何脚本。

## 网络不通时

本机实测 `raw.githubusercontent.com` 和 jsDelivr 不通，`gh-proxy.com` 通。所有地址前面加：

```text
https://gh-proxy.com/
```

代理是第三方公共服务，失效时换回官方 raw 或 `git clone`。
