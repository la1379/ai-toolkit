# -*- coding: utf-8 -*-
"""识图/OCR —— 小米 MiMo V2.5 读图（ocr-vision 方案 A 的实现）

为什么单独一个脚本、而不是 SKILL.md 里塞内联代码：
  1. 内联代码没法测；这个文件可以直接 `python ocr_mimo.py 图.jpg` 验证
  2. 多图批处理、失败留痕、写文件这些逻辑放脚本里更稳

凭证优先级：
  1. 环境变量 MIMO_API_KEY + MIMO_BASE_URL（推荐，跨平台）
  2. cc-switch 的 SQLite（Windows 本机可选；按供应商名字取，跟着当前激活供应商无关）

用法:
    python ocr_mimo.py 图1.jpg [图2.png ...]
    python ocr_mimo.py --prompt "只提取表格" 图.jpg
    python ocr_mimo.py --model mimo-v2.5-pro 图.jpg   # 注意：pro 不支持图片，会 404
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

CC_DB = os.path.expanduser('~/.cc-switch/cc-switch.db')
MODEL = 'mimo-v2.5'          # 多模态是 v2.5；v2.5-pro 是纯文本，发图会 404
MAX_TOKENS = 8000

PROMPT = ('请把这张图片里的所有文字完整、原样读出，特别是数字、金额、表格内容。'
          '用文字列表输出，不要漏任何数字。')


def creds_from_env():
    token = os.environ.get('MIMO_API_KEY', '').strip()
    base = os.environ.get('MIMO_BASE_URL', 'https://api.xiaomimimo.com/anthropic').strip()
    if token:
        return base.rstrip('/'), token
    return None


def creds_from_cc_switch():
    """按名字从 cc-switch 取小米的 (base_url, token)。只返回，绝不打印。"""
    if not os.path.exists(CC_DB):
        return None
    import sqlite3
    c = sqlite3.connect(CC_DB)
    c.row_factory = sqlite3.Row
    for r in c.execute("select * from providers where name like '%iMo%'"):
        env = (json.loads(r['settings_config'] or '{}').get('env') or {})
        base, tok = env.get('ANTHROPIC_BASE_URL'), env.get('ANTHROPIC_AUTH_TOKEN')
        if base and tok:
            return base.rstrip('/'), tok
    return None


def creds():
    pair = creds_from_env() or creds_from_cc_switch()
    if not pair:
        raise SystemExit(
            '未找到 MiMo 凭证。设置环境变量 MIMO_API_KEY（可选 MIMO_BASE_URL），'
            '或在 cc-switch 里配置 name 含 "MiMo" 的供应商。'
        )
    return pair


def read_image(path):
    if not os.path.isfile(path):
        raise SystemExit('图片不存在：%s' % path)
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
        raise SystemExit('不认的图片格式：.%s' % ext)
    return {'type': 'image',
            'source': {'type': 'base64',
                       'media_type': 'image/' + ('jpeg' if ext in ('jpg', 'jpeg') else ext),
                       'data': b64}}


def ocr_one(base, token, path, prompt, model, max_tokens=MAX_TOKENS):
    """读一张图，返回识别文本。异常一律抛出，由调用方决定要不要兜底。"""
    body = {
        'model': model,
        'max_tokens': max_tokens,
        # 关思维链：这是「看一眼抄下来」的活，不需要推理。实测开着会多烧一倍输出 token，
        # 且对抄写准确率没有帮助（合成 PPT 6/6 真值，开关两种状态都对）。
        'thinking': {'type': 'disabled'},
        'messages': [{'role': 'user', 'content': [read_image(path), {'type': 'text', 'text': prompt}]}],
    }
    req = urllib.request.Request(
        base + '/v1/messages', data=json.dumps(body).encode(),
        headers={'content-type': 'application/json',
                 'anthropic-version': '2023-06-01',
                 'x-api-key': token, 'authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        detail = ''
        try:
            detail = e.read().decode('utf-8', 'replace')[:300]
        except Exception:
            pass
        raise RuntimeError('HTTP %s %s' % (e.code, detail))
    return '\n'.join(b.get('text', '') for b in (d.get('content') or [])
                     if b.get('type') == 'text').strip()


def main():
    # Windows 控制台默认 GBK，中文输出会直接抛 UnicodeEncodeError
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description='小米 MiMo V2.5 识图 / OCR')
    ap.add_argument('images', nargs='+')
    ap.add_argument('--prompt', default=PROMPT)
    ap.add_argument('--model', default=MODEL)
    ap.add_argument('--out', default=None, help='结果写入文件（多图时按图分节），默认打到 stdout')
    args = ap.parse_args()

    base, token = creds()
    chunks = []
    for i, p in enumerate(args.images, 1):
        head = '' if len(args.images) == 1 else '===== [%d] %s =====\n' % (i, os.path.basename(p))
        try:
            chunks.append(head + ocr_one(base, token, p, args.prompt, args.model))
        except Exception as e:
            # 单张失败不拖垮整批，但要在结果里留痕 —— 静默跳过会让人以为「这图没字」
            chunks.append(head + '!! 识别失败：%s' % e)
    text = '\n\n'.join(chunks)

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(text)
        print('已写入 %s（%d 字）' % (args.out, len(text)))
    else:
        print(text)


if __name__ == '__main__':
    main()
