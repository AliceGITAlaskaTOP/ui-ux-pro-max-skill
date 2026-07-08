import re, base64, urllib.request, os

HTTPS_PROXY = os.environ.get('HTTPS_PROXY')
proxy_handler = urllib.request.ProxyHandler({'https': HTTPS_PROXY, 'http': HTTPS_PROXY}) if HTTPS_PROXY else urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

with open('fonts.css','r',encoding='utf-8') as f:
    css = f.read()

# Split into blocks: each preceded by a /* label */ comment
pattern = re.compile(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})', re.S)
blocks = pattern.findall(css)

KEEP = {'cyrillic','cyrillic-ext','latin','latin-ext'}
out = []
seen = 0
kept = 0
for label, block in blocks:
    seen += 1
    if label not in KEEP:
        continue
    m = re.search(r'url\((https://[^)]+\.woff2)\)', block)
    if not m:
        continue
    url = m.group(1)
    try:
        data = opener.open(url, timeout=40).read()
    except Exception as e:
        print("FAIL", url, e)
        continue
    b64 = base64.b64encode(data).decode('ascii')
    datauri = f"data:font/woff2;base64,{b64}"
    newblock = block.replace(url, datauri)
    out.append(f"/* {label} */\n{newblock}")
    kept += 1

with open('fonts-embedded.css','w',encoding='utf-8') as f:
    f.write("\n".join(out))

print(f"blocks seen={seen} kept={kept}")
print(f"fonts-embedded.css size = {os.path.getsize('fonts-embedded.css')} bytes")
