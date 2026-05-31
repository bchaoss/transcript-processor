#!/usr/bin/env python3
"""
parse_transcript.py
-------------------
Splits a raw transcript into structured segments by timestamp.
Classifies each segment as Q, A, or QA-mixed.
Outputs a numbered skeleton for review before writing digest.

Usage:
    python scripts/parse_transcript.py <transcript_file>

Input format expected:
    0:02 · Speaker text here...
    1:11 · More text...

Output:
    JSON list of segments with timestamp, type, and preview
"""

import re
import json
import sys


ANSWER_STARTERS = [
    "No, look", "Look,", "It's a good", "Obviously", "I'll answer",
    "I think we", "We are", "They are", "Yes.", "I do think",
    "There's a lot", "Absolutely", "Well,", "Sure,", "Great question",
    "That's a", "So,", "Right,",
]

FILLER_PATTERN = re.compile(
    r'\b(uh|um)\b,?\s*', flags=re.IGNORECASE
)


def parse_segments(text):
    """Split transcript text into (timestamp, content) pairs."""
    pattern = r'(\d+:\d+(?::\d+)?)\s*[·•]\s*'
    parts = re.split(pattern, text)

    segments = []
    i = 1
    while i < len(parts) - 1:
        ts = parts[i].strip()
        content = parts[i + 1].strip()
        if content:
            segments.append({'timestamp': ts, 'text': content})
        i += 2
    return segments


def classify_segment(text):
    """Classify a segment as Q, A, or QA."""
    # Starts like an answer
    for starter in ANSWER_STARTERS:
        if text.startswith(starter):
            return 'A'

    # Has questions and is long enough to contain both Q and A
    has_question = '?' in text
    is_long = len(text) > 300

    if has_question and is_long:
        return 'QA'

    if has_question:
        return 'Q'

    return 'QA'  # default to mixed if unclear


def split_qa_mixed(text):
    """Split a QA-mixed segment at the last question mark before the answer."""
    last_q = text.rfind('?')
    if last_q > 0 and last_q < len(text) - 50:
        return text[:last_q + 1].strip(), text[last_q + 1:].strip()
    return text, ''


def clean_filler(text):
    """Remove uh/um filler words only."""
    cleaned = FILLER_PATTERN.sub(' ', text)
    return re.sub(r'\s+', ' ', cleaned).strip()


def build_skeleton(segments):
    """Classify and preview all segments."""
    result = []
    for i, seg in enumerate(segments):
        seg_type = classify_segment(seg['text'])
        preview = seg['text'][:120].replace('\n', ' ')
        result.append({
            'index': i + 1,
            'timestamp': seg['timestamp'],
            'type': seg_type,
            'preview': preview + ('...' if len(seg['text']) > 120 else ''),
            'text': seg['text'],
        })
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/parse_transcript.py <transcript_file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        raw = f.read()

    segments = parse_segments(raw)
    skeleton = build_skeleton(segments)

    print(f"Found {len(skeleton)} segments:\n")
    for s in skeleton:
        print(f"[{s['timestamp']}] ({s['type']}) {s['preview']}")

    out_path = sys.argv[1].replace('.txt', '_skeleton.json')
    with open(out_path, 'w') as f:
        json.dump(skeleton, f, ensure_ascii=False, indent=2)

    print(f"\nSkeleton saved to: {out_path}")
    print(f"Q segments:  {sum(1 for s in skeleton if s['type'] == 'Q')}")
    print(f"A segments:  {sum(1 for s in skeleton if s['type'] == 'A')}")
    print(f"QA segments: {sum(1 for s in skeleton if s['type'] == 'QA')}")


if __name__ == '__main__':
    main()
