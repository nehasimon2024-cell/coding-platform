with open('problem_dataset_new.json', 'r', encoding='utf-8') as f:
    content = f.read()

# These are literal text sequences in the JSON
fixes = [
    ('\\u00e2\\u2020\\u2019', '\\u2192'),  # → (arrow)
    ('\\u00e2\\u2030\\u00a5', '\\u2265'),  # ≥
    ('\\u00e2\\u20ac\\u201d', '\\u2014'),  # —
    ('\\u00e2\\u20ac\\u2122', '\\u2019'),  # '
    ('\\u00e2\\u20ac\\u0153', '\\u201c'),  # "
    ('\\u00c2\\u00b2', '\\u00b2'),         # ²
    ('\\u00cf\\u20ac', '\\u03c0'),         # π
]

total = 0
for bad, good in fixes:
    count = content.count(bad)
    if count > 0:
        content = content.replace(bad, good)
        total += count
        print(f"Fixed {count}x: {bad} -> {good}")

with open('problem_dataset_new.json', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal: {total} fixes")
print("Done!")