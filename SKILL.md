---
name: transcript-processor
description: >-
  Transforms raw interview or podcast transcripts into structured Q/A digests, with optional commentary layer. Use this skill whenever the user provides a transcript (interview, podcast, earnings call, press conference) and wants it cleaned, organized, or analyzed. Trigger words include: "organize this transcript", "clean up this interview", "Q/A format", "digest", "summarize this interview", "what did X say about Y". Also trigger when the user uploads a long conversation text and wants to extract key points or prepare it for sharing. Handles any output language. Always use this skill for transcripts longer than ~15 minutes of content.
tags: [claude-skills, transcript-processor, podcast-tools, interview-analysis]
when_to_use: When the user provides a raw transcript file (interview, podcast, meeting notes) and wants to clean up filler words, structure it into a Q&A format, or generate a deep digest/analysis without losing original context.
---

# Transcript Processor Skill

## Modes

This skill has three modes. Infer from the user's request; ask only if genuinely ambiguous.

| Mode | When to use | Output |
|---|---|---|
| **clean** | "clean this up", "Q/A format", "文稿清洗", "整理成对话格式" | Q + A only, no commentary |
| **digest** | "digest", "analyze", "what did X avoid", "实话实说", "深度整理" | Q + A + Commentary + Meta-analysis |
| **upgrade** | "upgrade this clean file", "add commentary", "把clean升级为digest", user provides an existing clean .md | Commentary + Meta-analysis added to existing clean file; Q and A untouched |

Default to **clean** unless the user explicitly asks for analysis or commentary.

**Upgrade mode is a separate entry point — skip to the Upgrade section if the user provides an existing clean file.**

---

## Before doing anything: state the plan and wait for confirmation

Before running any script or writing any output, state the execution plan in this exact format and stop:

```
**Plan**
- Mode: clean / digest
- Output language: [e.g. English / Chinese / bilingual: EN transcript, ZH commentary]
- Translation: yes / no — [Q and A will / will not be translated to target language]
- Steps: 1. save transcript → 2. run parser → 3. clean Q/A → 4. if translation: translate Q/A → 5. if digest: add commentary per block → 6. if digest: add meta-analysis → 7. write file

Confirm to proceed.
```

For upgrade mode, use this plan format instead:
```
**Plan**
- Mode: upgrade (clean → digest)
- Input file: [filename]
- Commentary language: [e.g. Chinese]
- Steps: 1. read clean file → 2. add commentary per block → 3. add meta-analysis → 4. write digest file

Confirm to proceed.
```

Do not start executing until the user confirms. This catches mismatches in language, translation intent, and mode before any work is done.

---

## Main flow (clean and digest modes)

### Step 1: Run the parser

**Before writing any Q/A blocks, always run the transcript parser script.**

This is not optional. The script does mechanical timestamp-based segmentation that prevents omissions. Do not rely on reading and remembering — traverse, don't retrieve.

```bash
python3 scripts/parse_transcript.py <transcript_file>
```

The script outputs a numbered skeleton of all segments with timestamps and types (Q / A / QA-mixed). Review the skeleton, correct any misclassifications manually if needed, then proceed to cleaning.

If the transcript file is not yet saved to disk, write it first:

```bash
cat << 'TRANSCRIPT' > /tmp/transcript.txt
[paste transcript content]
TRANSCRIPT
python3 scripts/parse_transcript.py /tmp/transcript.txt
```

---

### Step 2: Clean Q (questions)

Q is cleaned original speech. Remove only:
- Filler words: `uh`, `um`, `you know`, `I mean`, `like`, `right` (standalone)

Do NOT:
- Rephrase, reorder, or summarize
- Merge separate questions into one
- Remove the interviewer's framing, edge, or follow-up logic
- Drop the timestamp

Format:
```
**[timestamp]**

**Q:** Cleaned question text here.
```

---

### Step 3: Clean A (answers)

A is cleaned original speech — not a summary, not a paraphrase. The speaker's own words must be preserved.

Remove only:
- Filler words: `uh`, `um`, `you know`, `I mean`, `like`, `right` (standalone)
- Repeated false starts: `"I think I think I think"` → `"I think"`
- Redundant hedges that repeat within the same sentence

Do NOT:
- Rephrase, reorder, or substitute words
- Compress or summarize
- Drop specific numbers, named products, or named people
- Editorialize (save that for Commentary in digest mode)

If the answer spans multiple transcript segments, combine them in order.

---

### Step 4 (digest mode only): Write Commentary

Skip entirely in clean mode.

Commentary is independent analysis — not a restatement of A. For each exchange, ask:

1. **Did they answer the question?** If not, what did they pivot to, and why?
2. **What structural tension did they avoid?** (e.g. answering "is revenue up?" with "costs are down")
3. **What's verifiable?** Label claims: `[verifiable]` / `[inference]` / `[industry consensus]`
4. **Does their analogy actually hold?** Name it if it doesn't.

Depth: 1-2 sentences for minor topics, full paragraph for core topics.

---

### Step 5 (digest mode only): Meta-analysis

Skip entirely in clean mode.

After all Q/A/Commentary blocks, add a final section identifying recurring patterns:

- Deflection patterns (e.g. "always cites historical data when asked about future risk")
- Framing choices (e.g. "consistently reframes competitor gaps as 'different markets'")
- The 2-3 moments of genuine candor (high-signal, stand out against the baseline)
- Claims that can be cross-checked against public records

---

## Upgrade mode (separate entry point)

Use this path when the user provides an existing clean `.md` file and asks to add commentary or upgrade to digest. **Do not run the parser. Do not touch Q or A text.**

1. Read the existing clean file directly. Treat each Q/A block as a completed segment.
2. Add Commentary after each A block (same rules as Step 4 above).
3. Add Meta-analysis at the end (same rules as Step 5 above).
4. Write the result as a new file: `[original_name]_digest.md`

---

## Output language, translation, and section labels

### Translation rule

If the user specifies an output language different from the transcript language, **translate Q and A into the target language** after cleaning. Translation comes after cleaning — clean first in the original language, then translate.

- "中文 clean" → clean English transcript, then translate Q and A to Chinese
- "bilingual" → keep original language for Q and A, target language for Commentary only
- "English clean" on an English transcript → no translation needed

When in doubt, include `Translation: yes/no` explicitly in the plan step and confirm with the user.

### Section labels

Match labels to output language. Do not hardcode any single language.

| Section | English | Chinese | Japanese |
|---|---|---|---|
| Question | `**Q:**` | `**Q：**` | `**Q：**` |
| Answer | `**A:**` | `**A：**` | `**A：**` |
| Commentary | `**Commentary:**` | `**实话：**` | `**解説：**` |
| Meta section | `## Meta-analysis` | `## 元分析` | `## メタ分析` |
| Verification | `[verifiable]` `[inference]` `[industry consensus]` | `【可验证】` `【推断】` `【行业共识】` | translate |

For bilingual output (e.g. EN transcript + ZH commentary):
- Q and A: original language label + original language text
- Commentary: target language label + target language text

Document header:
```
> Source: [name / date]
> Mode: clean / digest
> Output language: [e.g. English / Chinese / bilingual: EN transcript, ZH commentary]
> Translation: yes / no
> Note: Q and A = cleaned original speech (fillers and false starts removed only)
```

---

## File output

- Filename: `[interviewee]_[source]_[mode].md` — e.g. `sundar_allin_digest.md`, `sundar_allin_clean_zh.md`
- One file per mode/language combination
- Run `scripts/check_digest.py` on the output before presenting to the user

---

## Common failure modes

| Failure | Fix |
|---|---|
| Skip parser script, go straight to writing | Never. Always run `parse_transcript.py` first in clean/digest mode |
| A becomes a summary | A is cleaning only — preserve all words except fillers and false starts |
| Q loses the timestamp | Every Q block must have its timestamp |
| Commentary added in clean mode | Clean mode has no commentary. None. |
| Skipping segments that seem minor | Traverse by timestamp — importance is irrelevant at this step |
| "No direct answer" treated as neutral | In digest mode: name what was avoided and why |
| Meta-analysis missing in digest mode | Always required in digest mode, never in clean mode |
| Output language ≠ transcript language but no translation done | If output language differs from transcript, translate Q and A after cleaning |
| Executing before user confirms plan | Always state plan and wait for explicit confirmation first |
| Modifying Q or A text in upgrade mode | Upgrade mode only adds Commentary and Meta-analysis; Q and A are read-only |
| Running parser in upgrade mode | Upgrade mode skips parser entirely; input is already a clean .md file |
