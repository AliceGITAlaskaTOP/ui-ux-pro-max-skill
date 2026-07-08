#!/usr/bin/env python3
"""Build self-contained @font-face CSS from Fontsource STATIC woff2 (base64 data URIs)."""
import base64, subprocess, sys

CDN = "https://cdn.jsdelivr.net/fontsource/fonts/{id}@latest/{subset}-{weight}-normal.woff2"

RANGES = {
    "cyrillic": "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116",
    "cyrillic-ext": "U+0460-052F, U+1C80-1C88, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F",
    "latin": ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, "
              "U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, "
              "U+2193, U+2212, U+2215, U+FEFF, U+FFFD"),
    "latin-ext": ("U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, "
                  "U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, "
                  "U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF, U+FB00-FB06"),
}
SUBSETS = ["cyrillic", "cyrillic-ext", "latin", "latin-ext"]

# (fontsource id, css font-family, [weights])
FONTS = [
    ("montserrat", "Montserrat", [400, 500, 600, 700, 800]),
    ("prata", "Prata", [400]),
]

def fetch(url):
    r = subprocess.run(["curl", "-sSL", "-w", "%{http_code}", "-o", "/tmp/_f.woff2", url],
                       capture_output=True)
    code = r.stdout.decode().strip()[-3:]
    if code != "200":
        return None
    data = open("/tmp/_f.woff2", "rb").read()
    return data if data[:4] == b"wOF2" else None

def main():
    out, n, total = [], 0, 0
    for fid, fam, weights in FONTS:
        for w in weights:
            for sub in SUBSETS:
                data = fetch(CDN.format(id=fid, subset=sub, weight=w))
                if not data:
                    sys.stderr.write(f"  skip {fam} {w} {sub} (missing)\n")
                    continue
                b64 = base64.b64encode(data).decode()
                out.append(
                    f"/* {fam.lower()}-{sub}-{w} */\n@font-face{{"
                    f"font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;"
                    f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
                    f"unicode-range:{RANGES[sub]};}}"
                )
                n += 1; total += len(data)
                sys.stderr.write(f"  ok {fam:11s} {w} {sub:12s} {len(data)//1024}KB\n")
    css = "\n".join(out)
    open("fonts.css", "w").write(css)
    sys.stderr.write(f"\nDONE: {n} faces, {total//1024}KB raw, css {len(css)//1024}KB\n")

if __name__ == "__main__":
    main()
