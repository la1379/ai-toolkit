# 安全说明

这个仓库只放提示词与流程规则，不需要任何密钥。

## 不要提交

- API key、token、Cookie、浏览器 profile
- `config.yaml`、`.env`、`settings.json`
- 会话导出、日志、含个人信息的截图

## 如果你发现了泄漏

请不要在公开 issue 里贴出密钥。用 GitHub 的 Security Advisory 私下报告，或直接开一个不含敏感信息的 issue 说明位置。

## 使用提醒

- 仓库里的 `ocr-vision` 会调用外部 API，费用由使用者自己承担。
- `investment-review` 只做流程核查与复盘，不构成投资建议。
- `bili-learn` 涉及 B 站账号操作时，先确认平台规则与版权边界。
