# gn-claude-dns

为 **macOS + Shadowrocket** 用户准备 Claude 使用环境的 Agent Skill（让 AI 助手按步骤检查和操作的技能）。覆盖本地状态清理、DNS 防泄露、WebRTC 检查、域名分流，以及 Claude Code 防直连的适配与验收。

## 能做什么

| 环节 | 内容 |
| --- | --- |
| 本地整理 | 发现 Claude 登录状态、应用生成的本地标识、历史与缓存，按授权范围定向处理 |
| DNS | 检查主/备用解析、系统回退、浏览器解析设置与实际路径 |
| 浏览器 | 在实际使用的浏览器配置文件中检查 WebRTC 与 IPv6 |
| 分流 | 合并 Claude 代理规则和按需选择的国内网站直连规则 |
| Claude Code | 检查代理配置、启动检查与运行时防直连的覆盖范围 |
| 验收 | 分别记录配置、规则、真实路线、泄露测试和 Claude 功能结果，并提供回退方法 |

DNS 是把域名转换成网络地址的服务；WebRTC 是浏览器音视频通信机制，可能产生独立于普通网页请求的连接。两者需要分别检查。

## 安装

需要支持 `SKILL.md` 的 AI 工具。Codex 用户可在终端执行以下命令；目标目录已存在时 `git clone` 会停止，不会覆盖原技能：

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/lindsaysendra86-sys/gn-claude-dns.git ~/.codex/skills/gn-claude-dns
```

也可以下载 [发布包](https://github.com/lindsaysendra86-sys/gn-claude-dns/releases/latest)，解压后把 `gn-claude-dns` 文件夹放入工具的技能目录。已有同名技能时先比较和备份。其他支持技能的工具按各自的安装方式处理。

刷新技能列表或新开会话，确认技能可见。

## 使用

先只读检查：

```text
使用 $gn-claude-dns 检查我的 Mac 和 Shadowrocket，先只读检查，保留 Claude 历史、其他应用和当前连接。
```

需要完整准备：

```text
使用 $gn-claude-dns 准备 Claude 浏览器和 Claude Code 环境。先列出本地清理范围，保留项目代码、技能和其他工具，再实施 DNS、WebRTC 与分流配置，并分项验收。
```

技能入口：[SKILL.md](SKILL.md)。它引导助手根据实际版本、配置和授权执行，不会在安装时自动清理电脑或修改网络。

## 只读检查脚本

需要 Python 3，无第三方依赖。在本仓库目录运行：

```sh
python3 scripts/audit.py
python3 scripts/audit.py --conf '/absolute/path/to/exported.conf'
python3 scripts/audit.py --help
```

默认不联网、不修改文件，只输出候选路径存在性、配置线索等信息，不输出认证值。可选网络探测必须显式指定实际本机 HTTP 代理端口：

```sh
python3 scripts/audit.py --proxy 'http://127.0.0.1:LOCAL_PORT' --probe
```

把 `LOCAL_PORT` 替换为现场端口。探测只发送未认证请求，不使用模型额度；不能替代浏览器 DNS/WebRTC、登录或模型响应验收。

## 文件导航

- [本地状态清理](references/local-cleanup.md)
- [Shadowrocket DNS 与分流](references/shadowrocket.md)
- [浏览器、WebRTC 与 IPv6](references/browser.md)
- [Claude Code 与 Desktop](references/claude-clients.md)
- [验收与故障判断](references/verification.md)
- [经验依据与官方参考](references/evidence-and-sources.md)
- [Claude 规则片段](assets/claude-rules.conf)
- [国内网站直连片段](assets/domestic-direct-rules.conf)

两份 `.conf` 都是合并片段，不能直接覆盖现有完整配置。保留原节点、订阅和其他应用规则，加载后验证实际效果。

## 适用范围

主要适用于 macOS + Shadowrocket。iOS/iPadOS 仅采用适用的界面步骤；其他系统或代理软件需要重新适配。

清理应用本地状态不代表删除硬件身份、云端设备关联或服务端记录，也不保证账号结果。浏览器、Desktop 和 Code 分别验收；规则匹配成功不代表实际连接、DNS 或 WebRTC 都已通过。

仓库不包含作者的账号、代理节点、个人服务器地址、凭据或配置备份，也不包含阿里云等云服务器运维流程。严格运行时防直连需要在目标机器适配和验证。

## 反馈

可在 [Issues](https://github.com/lindsaysendra86-sys/gn-claude-dns/issues) 提交系统与应用版本、复现步骤、预期和实际结果。分享前移除账号、节点认证、订阅链接、Cookie、令牌、私人地址和本机路径；不要上传完整代理配置或浏览器数据库。
