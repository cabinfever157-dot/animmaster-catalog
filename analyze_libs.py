import json, os

with open('manifest.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

libs = {}
for key, val in data.items():
    if 'cdn_video' not in val and 'demo_html' not in val:
        code = val.get('local_code', val.get('local_tsx', ''))
        lc = code.lower()
        if 'aceternity' in lc: lib = 'Aceternity'
        elif 'magicui' in lc: lib = 'MagicUI'
        elif 'originui' in lc: lib = 'OriginUI'
        elif 'hyperui' in lc: lib = 'HyperUI'
        elif 'daisyui' in lc: lib = 'DaisyUI'
        elif 'smoothui' in lc: lib = 'SmoothUI'
        elif 'cultui' in lc: lib = 'CultUI'
        elif 'seraui' in lc: lib = 'SeraUI'
        else: lib = 'Other'
        if lib not in libs:
            libs[lib] = []
        if len(libs[lib]) < 5:
            fname = code.replace('\\', '/').split('/')[-1]
            libs[lib].append((key, fname))

for lib in sorted(libs.keys()):
    print(f'\n=== {lib} ===')
    for key, fname in libs[lib]:
        print(f'  {key} -> {fname}')