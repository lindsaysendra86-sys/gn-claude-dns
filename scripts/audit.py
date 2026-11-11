#!/usr/bin/env python3
"""Read-only local clues; never a runtime DNS/WebRTC/egress certification."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from urllib.parse import urlsplit

TARGETS = {
    'claude.ai': 'PROXY', 'api.anthropic.com': 'PROXY',
    'platform.claude.com': 'PROXY', 'claude.app': 'PROXY',
    'bridge.claudeusercontent.com': 'PROXY', 'claudemcpcontent.com': 'PROXY',
    'www.deepseek.com': 'DIRECT', 'www.douyin.com': 'DIRECT',
    'lf3-static.bytednsdoc.com': 'DIRECT', 'www.bilibili.com': 'DIRECT',
    'www.jd.com': 'DIRECT', 'www.qq.com': 'DIRECT', 'mat1.gtimg.com': 'DIRECT',
    'res.wx.qq.com': 'DIRECT', 'www.feishu.cn': 'DIRECT',
    'lf-package-cn.feishucdn.com': 'DIRECT', 'www.xiaohongshu.com': 'DIRECT',
    'fe-static.xhscdn.com': 'DIRECT', 'www.baidu.com': 'DIRECT',
    'weibo.com': 'DIRECT', 'tva1.sinaimg.cn': 'DIRECT',
    'www.taobao.com': 'DIRECT', 'gw.alicdn.com': 'DIRECT', 'www.mi.com': 'DIRECT',
}
DNS_KEYS = {'dns-server', 'fallback-dns-server', 'dns-direct-system',
            'dns-fallback-system', 'dns-direct-fallback-proxy',
            'udp-policy-not-supported-behaviour'}
ENV_KEYS = ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy',
            'all_proxy', 'NO_PROXY', 'no_proxy', 'CLAUDE_CONFIG_DIR',
            'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_BASE_URL')
AUTH_KEYS = ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_BASE_URL')


def dns_hint(value):
    """Allow only public example resolvers/boolean options; redact arbitrary URLs."""
    parts = []
    for item in value.split(','):
        item = item.strip()
        if item.lower() in {'system', 'true', 'false', 'reject', 'direct', 'proxy'}:
            parts.append(item.lower())
        elif item in {'https://1.1.1.1/dns-query#proxy',
                      'https://1.0.0.1/dns-query#proxy'}:
            parts.append(item)
        else:
            parts.append('[custom resolver/value redacted; inspect locally]')
    return parts


def config_summary(text):
    section = ''
    rules, dns, unsupported = [], {}, []
    for line_no, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith(('#', ';')):
            continue
        if s.startswith('[') and s.endswith(']'):
            section = s[1:-1].strip().lower()
            continue
        if section == 'general' and '=' in s:
            key, value = [x.strip() for x in s.split('=', 1)]
            if key.lower() in DNS_KEYS:
                dns.setdefault(key.lower(), []).append({'line': line_no, 'hint': dns_hint(value)})
        if section == 'rule':
            # Never print raw policies, custom domains, subscription URLs or rule text.
            parts = [x.strip() for x in s.split(',')]
            kind = parts[0].upper()
            if kind in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD'} and len(parts) >= 3:
                rules.append((line_no, kind, parts[1].lower(), parts[2]))
            else:
                unsupported.append(line_no)
    hints = {}
    for host, expected in TARGETS.items():
        match = next((r for r in rules if
                      (r[1] == 'DOMAIN' and host == r[2]) or
                      (r[1] == 'DOMAIN-SUFFIX' and (host == r[2] or host.endswith('.' + r[2]))) or
                      (r[1] == 'DOMAIN-KEYWORD' and r[2] in host)), None)
        if match:
            policy = match[3] if match[3] in {'DIRECT', 'PROXY', 'REJECT'} else '[custom policy]'
            hints[host] = {'expected_if_selected': expected, 'domain_rule_line': match[0],
                           'domain_rule_policy': policy,
                           'earlier_uninterpreted_rule': any(n < match[0] for n in unsupported)}
        else:
            hints[host] = {'expected_if_selected': expected, 'domain_rule': 'not found'}
    return {'dns_hints': dns, 'duplicate_general_keys': [k for k, v in dns.items() if len(v) > 1],
            'domain_rule_hints': hints,
            'limits': 'Static exported file only. Does not evaluate modules, RULE-SET, IP/GEOIP, FINAL, '
                      'policy groups or active configuration. No runtime pass/fail inferred. '
                      'Domestic targets apply only if user selected them.'}


def local_summary():
    home = Path.home()
    paths = ['.claude', '.claude.json', 'Library/Application Support/Claude',
             'Library/Caches/com.anthropic.claudefordesktop']
    settings = home / '.claude/settings.json'
    result = {'platform': sys.platform, 'candidate_paths': {
        '~/' + p: {'exists': (home / p).exists(), 'symlink': (home / p).is_symlink()} for p in paths},
        'environment_presence_only': {k: k in os.environ for k in ENV_KEYS},
        'custom_config_dir': 'set; not traversed automatically' if os.environ.get('CLAUDE_CONFIG_DIR') else 'unset',
        'limits': 'Candidate paths only; not exhaustive, no deletion plan inferred. No Keychain/History/Cookie contents read.'}
    # Read only standard settings fields; never echo values or arbitrary keys.
    if settings.is_file() and not settings.is_symlink() and not settings.parent.is_symlink():
        try:
            d = json.loads(settings.read_text())
            if not isinstance(d, dict):
                raise ValueError()
            env = d.get('env', {})
            result['claude_settings_presence_only'] = {
                'apiKeyHelper': 'apiKeyHelper' in d,
                'auth_override_keys': [k for k in AUTH_KEYS if isinstance(env, dict) and k in env]}
        except (OSError, ValueError):
            result['claude_settings'] = 'unreadable or invalid; inspect locally'
    return result


def loopback_proxy(value):
    try:
        p = urlsplit(value)
        port = p.port
        address = ipaddress.ip_address(p.hostname or '')
    except ValueError:
        raise argparse.ArgumentTypeError('Use http://127.0.0.1:PORT or an explicit IPv6 loopback address.') from None
    if (p.scheme != 'http' or not address.is_loopback or port is None or
            p.username is not None or p.password is not None or p.path or p.query or p.fragment):
        raise argparse.ArgumentTypeError('Only an explicit loopback HTTP proxy without credentials/path is accepted.')
    return value


def probe(proxy):
    curl = shutil.which('curl')
    if not curl:
        return {'status': 'not run', 'reason': 'curl unavailable'}
    env = dict(os.environ)
    env.pop('SSLKEYLOGFILE', None)
    for k in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        env[k] = proxy
    env['NO_PROXY'] = env['no_proxy'] = ''
    cmd = [curl, '--disable', '--proxy', proxy, '--noproxy', '', '--proto', '=https',
           '--connect-timeout', '5', '--max-time', '15', '--silent', '--show-error',
           '--output', os.devnull, '--write-out', '%{http_code} %{http_connect} %{ssl_verify_result}',
           'https://api.anthropic.com/v1/models']
    try:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=20)
        # No response body, stderr, secret or account information is emitted.
        m = re.fullmatch(r'(\d{3}) (\d{3}) (\d+)', r.stdout.strip())
        fields = list(m.groups()) if m else None
        ok = r.returncode == 0 and fields is not None and fields[0] in {'200', '401'} and fields[1:] == ['200', '0']
        return {'network_probe_observed': ok, 'curl_exit_code': r.returncode,
                'http_status_connect_certificate': fields,
                'limits': 'Unauthenticated explicit-proxy reachability only. Does not prove listener identity, '
                          'public exit IP, routing policy, DNS/WebRTC, account login or model access.'}
    except subprocess.TimeoutExpired:
        return {'network_probe_observed': False, 'reason': 'bounded probe timeout; no direct retry'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--conf', type=Path, help='Explicit exported Shadowrocket text configuration, read-only')
    parser.add_argument('--proxy', type=loopback_proxy, help='Actual loopback HTTP endpoint; never assumed')
    parser.add_argument('--probe', action='store_true', help='Send one unauthenticated HTTPS probe through --proxy')
    args = parser.parse_args()
    if args.probe and not args.proxy:
        parser.error('--probe requires --proxy')
    result = {'local': local_summary()}
    if args.conf:
        try:
            info = args.conf.stat()
            if args.conf.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_size > 5_000_000:
                parser.error('Use a regular non-symlink exported config under 5 MB.')
            result['configuration'] = config_summary(args.conf.read_text(encoding='utf-8-sig'))
        except (OSError, UnicodeError):
            parser.error('Cannot read exported text configuration; no raw file/error content emitted.')
    if args.probe:
        result['probe'] = probe(args.proxy)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
