#!/usr/bin/env python3
"""
check_digest.py
---------------
Validates a completed digest .md file for completeness.
Checks that every Q block has a corresponding A and Commentary.
Reports any empty sections.

Usage:
    python scripts/check_digest.py <digest_file.md>
"""

import re
import sys


def check_digest(path):
    with open(path) as f:
        content = f.read()

    q_count = content.count('**Q:**') + content.count('**Q：**')
    a_count = content.count('**A:**') + content.count('**A：**')
    c_count = (content.count('**Commentary:**') +
               content.count('**实话:**') +
               content.count('**实话：**'))
    meta = '## Meta-analysis' in content or '## 元分析' in content

    # Find empty sections (label immediately followed by newline and next label)
    empty_a = re.findall(r'\*\*A[：:]\*\*\s*\n\s*\*\*', content)
    empty_c = re.findall(r'\*\*(Commentary|实话)[：:]\*\*\s*\n\s*\*\*', content)

    print(f"Digest: {path}")
    print(f"  Q blocks:          {q_count}")
    print(f"  A blocks:          {a_count}")
    print(f"  Commentary blocks: {c_count}")
    print(f"  Meta-analysis:     {'yes' if meta else 'MISSING'}")
    print(f"  Empty A sections:  {len(empty_a)}")
    print(f"  Empty Commentary:  {len(empty_c)}")

    if q_count == a_count == c_count and meta and not empty_a and not empty_c:
        print("\n  OK - digest is complete")
        return True
    else:
        print("\n  WARNING - digest has issues")
        if q_count != a_count:
            print(f"    Q/A mismatch: {q_count} Q vs {a_count} A")
        if q_count != c_count:
            print(f"    Commentary mismatch: {q_count} Q vs {c_count} Commentary")
        if not meta:
            print("    Missing meta-analysis section")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_digest.py <digest_file.md>")
        sys.exit(1)
    ok = check_digest(sys.argv[1])
    sys.exit(0 if ok else 1)
