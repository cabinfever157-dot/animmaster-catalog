#!/usr/bin/env python3
"""Analyze uncategorized items."""
import json, os
from collections import Counter

with open(r"C:\Users\info\Dropbox\Projects\component-catalog\manifest.json", "r", encoding="utf-8") as f:
    d = json.load(f)

uc = [(k, v) for k, v in d.items() if v.get("category") == "Uncategorized"]
print(f"Total Uncategorized: {len(uc)}")

# Count by library folder
lib_counts = Counter()
for k, v in uc:
    path = v["local_tsx"].replace("\\", "/")
    parts = path.split("/")
    lib = "unknown"
    for i, p in enumerate(parts):
        if p == "components" and i > 0:
            lib = parts[i - 1]
            break
    if "AG_Backup" in path:
        lib = "AG"
    lib_counts[lib] += 1

print("By library:")
for lib, n in lib_counts.most_common():
    print(f"  {lib}: {n}")

print()
print("=== All Uncategorized filenames (sorted) ===")
for k, v in sorted(uc, key=lambda x: x[1]["local_tsx"]):
    bn = os.path.basename(v["local_tsx"])
    print(f"  {bn}")