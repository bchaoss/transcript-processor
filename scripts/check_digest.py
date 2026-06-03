#!/usr/bin/env python3
"""
check_digest.py
---------------
Validates a completed digest .md file for completeness.
Checks that every Q block has a corresponding A and Commentary.
Reports any empty sections.

Supports multilingual digests — detects Q/A/Commentary labels in any language
by matching all known variants plus a generic bold-label pattern.

Usage:
    python scripts/check_digest.py <digest_file.md>
"""

import re
import sys


# All known Q label variants (full-width and half-width colon)
Q_LABELS = [r'\*\*Q[：:]\*\*']

# All known A label variants
A_LABELS = [r'\*\*A[：:]\*\*']

# All known Commentary label variants across languages
# Add new languages here — pattern matches **<word>:** or **<word>：**
COMMENTARY_LABELS = [
    r'\*\*Commentary[：:]\*\*',   # English
    r'\*\*实话[：:]\*\*',          # Chinese
    r'\*\*解説[：:]\*\*',          # Japanese
    r'\*\*Commentaire[：:]\*\*',  # French
    r'\*\*Kommentar[：:]\*\*',    # German/Norwegian
    r'\*\*Comentario[：:]\*\*',   # Spanish
]

# All known meta-analysis section headers
META_HEADERS = [
    '## Meta-analysis',   # English
    '## 元分析',           # Chinese
    '## メタ分析',         # Japanese
    '## Méta-analyse',    # French
    '## Metaanalyse',     # German
    '## Metaanálisis',    # Spanish
]


def count_pattern(content, patterns):
    total = 0
    for p in patterns:
        total += len(re.findall(p, content))
    return total


def find_empty(content, label_patterns):
    """Find label immediately followed by a newline and the next bold label."""
    empty = []
    for p in label_patterns:
        # Match label followed only by whitespace then another bold marker
        matches = re.findall(p + r'\s*\n\s*\*\*', content)
        empty.extend(matches)
    return empty


def check_digest(path):
    with open(path) as f:
        content = f.read()

    q_count = count_pattern(content, Q_LABELS)
    a_count = count_pattern(content, A_LABELS)
    c_count = count_pattern(content, COMMENTARY_LABELS)
    meta = any(h in content for h in META_HEADERS)

    empty_a = find_empty(content, A_LABELS)
    empty_c = find_empty(content, COMMENTARY_LABELS)

    # Detect which commentary label is in use (for reporting)
    detected_label = 'none'
    for p in COMMENTARY_LABELS:
        if re.search(p, content):
            detected_label = p
            break

    print(f"Digest: {path}")
    print(f"  Q blocks:            {q_count}")
    print(f"  A blocks:            {a_count}")
    print(f"  Commentary blocks:   {c_count}  (label: {detected_label})")
    print(f"  Meta-analysis:       {'yes' if meta else 'MISSING'}")
    print(f"  Empty A sections:    {len(empty_a)}")
    print(f"  Empty Commentary:    {len(empty_c)}")

    if q_count == a_count == c_count and meta and not empty_a and not empty_c:
        print("\n  OK - digest is complete")
        return True
    else:
        print("\n  WARNING - digest has issues")
        if q_count != a_count:
            print(f"    Q/A mismatch: {q_count} Q vs {a_count} A")
        if q_count != c_count:
            print(f"    Commentary mismatch: {q_count} Q vs {c_count} Commentary")
            if c_count == 0:
                print("    (No commentary labels matched — check language or label format)")
        if not meta:
            print(f"    Missing meta-analysis section (checked: {META_HEADERS})")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_digest.py <digest_file.md>")
        sys.exit(1)
    ok = check_digest(sys.argv[1])
    sys.exit(0 if ok else 1)
