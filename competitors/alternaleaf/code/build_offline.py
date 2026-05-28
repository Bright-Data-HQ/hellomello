#!/usr/bin/env python3
"""
Build a fully self-contained offline version of presentation.html.

- Downloads the Google Fonts used by the deck and inlines them as
  base64-encoded woff2 @font-face rules.
- Inlines data.js.
- Base64-embeds every screenshot referenced by the deck.

Output: presentation/presentation-offline.html  (one file, no network needed)
"""
import os, re, base64, urllib.request, mimetypes, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRES = os.path.join(ROOT, 'presentation')
DATA = os.path.join(ROOT, 'data')
SHOTS = os.path.join(DATA, 'screenshots')

SRC = os.path.join(PRES, 'presentation.html')
OUT = os.path.join(PRES, 'presentation-offline.html')
DATA_JS = os.path.join(PRES, 'data.js')

# Pretend to be a modern browser so Google Fonts serves woff2.
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')

FONT_CSS_URL = (
    'https://fonts.googleapis.com/css2'
    '?family=Fraunces:opsz,wght@9..144,400;9..144,500'
    '&family=Inter:wght@400;500;600'
    '&family=JetBrains+Mono:wght@400;500'
    '&display=swap'
)


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def build_inline_fonts():
    """Fetch the Google Fonts CSS, then fetch each woff2 it references and inline as base64."""
    css = fetch(FONT_CSS_URL).decode('utf-8')
    urls = sorted(set(re.findall(r'url\((https://[^)]+\.woff2)\)', css)))
    print(f'  fetching {len(urls)} woff2 files...')
    cache = {}
    for u in urls:
        data = fetch(u)
        b64 = base64.b64encode(data).decode('ascii')
        cache[u] = f'data:font/woff2;base64,{b64}'
    # rewrite all URLs in the css to data: URIs
    def repl(m):
        return f'url({cache[m.group(1)]}) format("woff2")'
    css = re.sub(r'url\((https://[^)]+\.woff2)\)\s*format\([^)]+\)', repl, css)
    return css


def inline_image(path):
    mt, _ = mimetypes.guess_type(path)
    mt = mt or 'image/png'
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    return f'data:{mt};base64,{b64}'


def main():
    with open(SRC, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1) inline fonts (replace the <link> + preconnects with a <style> block)
    print('Inlining fonts...')
    font_css = build_inline_fonts()
    html = re.sub(
        r'<link rel="preconnect"[^>]*>\s*'
        r'<link rel="preconnect"[^>]*>\s*'
        r'<link href="https://fonts\.googleapis\.com/css2[^"]+" rel="stylesheet">',
        f'<style>\n{font_css}\n</style>',
        html,
        count=1,
    )

    # 2) inline data.js
    print('Inlining data.js...')
    with open(DATA_JS, 'r', encoding='utf-8') as f:
        data_js = f.read()
    html = html.replace('<script src="data.js"></script>', f'<script>\n{data_js}\n</script>')

    # 3) inline screenshots — replace data/<file>.png references with data: URIs
    print('Inlining screenshots...')
    shots = re.findall(r'"(CleanShot [^"]+\.png)"', html)
    shots = sorted(set(shots))
    print(f'  {len(shots)} screenshots')
    # Find loader pattern: <img src="data/${encodeURI(s)}" ...> and switch to a JS-side lookup.
    embed_map = {}
    for s in shots:
        p = os.path.join(SHOTS, s)
        if not os.path.exists(p):
            print(f'  WARN missing: {s}', file=sys.stderr)
            continue
        embed_map[s] = inline_image(p)

    # Replace the array of filenames with the array of data URIs directly.
    def list_replace(m):
        new = ',\n    '.join(f'"{embed_map.get(s, s)}"' for s in shots if s in embed_map)
        return '[\n    ' + new + '\n  ]'

    html = re.sub(
        r'\[\s*(?:"CleanShot [^"]+\.png",?\s*)+\]',
        list_replace,
        html,
        count=1,
    )
    # Now change the loader to not prepend "data/"
    html = html.replace('src="data/${encodeURI(s)}"', 'src="${s}"')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f'\nWrote {OUT}  ({size_mb:.1f} MB)')


if __name__ == '__main__':
    main()
