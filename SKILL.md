---
name: gn-claude-dns
description: 为 macOS 上搭配 Shadowrocket 使用 Claude 的用户检查和准备本地环境：按范围清理 Claude 登录状态、历史与缓存，配置 DNS、WebRTC 和域名分流，核对 Claude Code 防直连及实际出口。适用于使用前准备、旧配置整理和泄露排查；不含云服务器运维，不承诺删除云端设备关联或保证账号安全。
---

# gn-claude-dns

把 Claude 的本地残留、域名解析、浏览器网络和应用分流分开处理，最终交付可回退的配置与逐项证据。默认面向 **macOS + Shadowrocket**；浏览器、Claude Desktop、Claude Code 是三个独立验收对象。iOS/iPadOS 只采用适用的 Shadowrocket/浏览器步骤，不执行 Mac 文件或终端操作；Windows 上使用其他代理软件需要重新适配，不能照抄。

## 开始前

1. 识别用户要处理的入口、系统/应用版本、浏览器配置文件、当前已选节点、当前生效配置、本机代理协议与端口。不要假定配置叫 `dns-fixed.conf`、端口为 1082、网卡为 en0。
2. 将目标区分为检查、清理、修复、完整准备。只检查就不改配置；不把清理作为修复 DNS 的前提。完整准备中的清理先列出具体项目、影响和保留项；已有明确授权就继续，永久删除等需要按当前环境权限规则处理。
3. 保存当前配置副本/相关文件指纹到用户本机私有目录，记录回退方法。凭据文件的副本也属于敏感数据，不放进分享包。不得复制订阅地址、账号、节点认证、Cookie、令牌到报告。
4. 保持正在使用的 Shadowrocket 连接。现有规则、其他应用、远程控制、局域网和开发工具默认保留。先验证新路径可用，再在可接受的窗口关闭旧 Claude 会话/目标浏览器；不要中断承载本次操作的唯一连接。

可运行本技能目录下的只读检查（需要 Python 3，无第三方包）。将以下 `{skillDir}` 替换为当前读取的 SKILL.md 所在目录，不依赖用户项目的工作目录：

```sh
python3 {skillDir}/scripts/audit.py
python3 {skillDir}/scripts/audit.py --conf '/absolute/path/to/exported.conf'
python3 {skillDir}/scripts/audit.py --proxy 'http://127.0.0.1:LOCAL_PORT' --probe
```

将 `LOCAL_PORT` 替换为现场端口。脚本默认不发网络请求；`--probe` 只经指定本机 HTTP 代理请求无认证检测端点，不使用账号或模型额度。它不会执行删除、修改配置或验证浏览器 DNS/WebRTC。`--conf` 输出仅是静态线索，活跃配置与实际路线必须另外验证。详细参数用 `--help`。

## 执行顺序与参考

- **本地清理**：读 [references/local-cleanup.md](references/local-cleanup.md)。区分缓存、历史、登录凭据、应用生成的本地标识与硬件/云端身份。先完成清单，再按用户范围处理；不复制过去主机的整目录删除命令。
- **DNS 与分流**：读 [references/shadowrocket.md](references/shadowrocket.md)。在当前配置副本里合并 DNS 与规则；重新加载后回读。核心规则见 [assets/claude-rules.conf](assets/claude-rules.conf)，国内站点按需取 [assets/domestic-direct-rules.conf](assets/domestic-direct-rules.conf)。两者都是片段，不是可覆盖原配置的完整订阅。
- **浏览器与 WebRTC**：读 [references/browser.md](references/browser.md)。在实际使用 Claude 的同一浏览器配置文件内设置与检测；普通浏览器、独立环境和系统登录窗口不能互相替代。
- **Claude Code / Desktop**：读 [references/claude-clients.md](references/claude-clients.md)。保留有效保护，新增保护时限定应用范围；不要将代理环境变量说成运行时强制隔离。
- **验收与交付**：读 [references/verification.md](references/verification.md)，按层记录通过/失败/未测/不适用。参考依据与历史经验边界见 [references/evidence-and-sources.md](references/evidence-and-sources.md)。

## 必须保持的判断边界

- 清理本地标识不等于清除硬件身份、服务器记录或账号关联。不要伪造设备 UUID、MAC 地址、序列号或浏览器指纹；不承诺“变成新设备”“不封号”。
- `DIRECT/PROXY` 匹配、实际连接路线、DNS/WebRTC 检测、登录、模型响应分别验收。匹配成功不代表目标端口可达；HTTP 401 只可能证明网络和服务响应，不能证明登录成功。
- `PROXY` 随当前节点/策略组变化，不天然是固定出口。主代理断开、备用 DNS 和 IPv6 都要单独考虑。
- 不把第三方检测服务远端抓取的结果当成本机结果；不为让测试全绿只改检测域名的路线。
- 不顺带改服务器、云安全组、公众号出口或 SSH 配置；用户指定的单 IP 规则另行处理，不携带历史主机地址。

## 交付方式

先给结论、改动与证据，再给简短“人话决策版”。说明哪些入口可以用、剩余缺口、推荐下一步和回退入口；没有待决项就不额外询问。报告保存在当前任务目录，分享前去掉凭据、私有地址和本机用户名。完成后清理本次无用的临时文件，保留明确需要的回退副本。

示例调用：`用 $gn-claude-dns 检查我的 Mac 和 Shadowrocket，先只读检查，不清历史。` 或 `用 $gn-claude-dns 准备 Claude 浏览器和 Code 环境，保留项目与其他软件；列清理清单后实施并验收。`
