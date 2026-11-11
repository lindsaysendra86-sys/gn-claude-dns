# 经验依据与复核入口

整理日期：2026-11-11。内容来自一次 macOS + Shadowrocket 的实际排查与配置经验，并对照当前公开网络文档。所有旧机器的节点、账号、服务器 IP、设备标识、日志与认证信息均不随技能分发。

## 历史证据如何使用

- 曾发现系统 DNS/备用 DNS 与浏览器环境混用本地运营商解析；正常路径修复后，目标独立浏览器两轮 DNS 测试均仅见预期公共解析服务，WebRTC 测试未出现本机公网地址。此结果仅属于该独立环境，不能推广为所有 Shadowrocket 用户自动通过。
- 专用浏览器代理停机后曾确认页面代理连接失败，恢复后出口恢复；共享 Shadowrocket 配置的所有故障回退路径没有被等价证明。
- 曾出现“IPv4 路径固定，但双栈检测返回代理节点 IPv6”。这不是本机 IPv6 泄露的充分证据，也不满足固定单一 IPv4。
- 本地 Claude 清理、重装、终端代理闸门与子进程网络限制曾分别验证；历史浏览器/隐藏登录状态并没有全部证明清除，真实模型响应曾受额度限制而未通过。
- 国内域名经验覆盖主站之外的测试资源，特别是抖音和飞书资源地址。使用者应重新读取自己测试页/真实页面的地址。

## 官方与测试来源

- [Claude Code 网络设置](https://code.claude.com/docs/en/network-config)：代理环境、依赖域名、提供方差异；部署前重新查阅。
- [Claude Desktop 网络要求](https://code.claude.com/docs/en/desktop#network-access-requirements)：主站与动态内容域覆盖。
- [Claude Code 安装](https://code.claude.com/docs/en/setup)：仅需要重装时使用当前官方入口。
- [Chrome privacy API](https://developer.chrome.com/docs/extensions/reference/api/privacy)：WebRTC IP handling 设置与扩展控制状态。
- [Chromium WebRTC IP handling 常量](https://chromium.googlesource.com/chromium/src/+/HEAD/third_party/blink/common/peerconnection/webrtc_ip_handling_policy.cc)：核对实现名称；不代表其他浏览器同样支持。
- [Shadowrocket 官方商店页](https://apps.apple.com/app/shadowrocket/id932747118)：产品身份；具体配置键优先核对安装版本内置说明。DNS 合并示例来自历史实测，不标成厂商跨版本保证。
- [BrowserLeaks DNS](https://browserleaks.com/dns)、[WebRTC](https://browserleaks.com/webrtc)、[IP](https://browserleaks.com/ip)：在用户本机目标浏览器执行的观测工具，不是保证账号状态的认证。

官方清单会变化。新增依赖优先从官方文档与真实请求发现，不导入不明来源的“万能防封规则”。
