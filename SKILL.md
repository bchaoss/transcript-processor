---
name: interview-digest
description: Transforms raw interview or podcast transcripts into structured Q/A/commentary digests. Use this skill whenever the user provides a transcript (interview, podcast, earnings call, press conference) and wants it organized, summarized, or analyzed — especially when they say things like "organize this transcript", "summarize this interview", "what did X say about Y", "turn this into a digest", or "I want Q/A format". Also trigger when the user uploads a long conversation text and wants to extract key points or prepare it for sharing with others who haven't seen it. Handles both English and Chinese output. Always use this skill for transcripts longer than ~15 minutes of content.
---

# Interview Digest Skill

Turns raw transcripts into clean, structured digests with three layers per exchange:
- **Q** — original question, lightly cleaned (remove filler words only)
- **A** — speaker's answer, faithfully paraphrased
- **Commentary** — independent interpretation: what was avoided, what's verifiable, what's spin

---

## Step 0: Clarify before starting

Before writing anything, ask (or infer from context) two things:

1. **Who is the audience?** Options:
   - Self-reference (quick review) → shorter A, lighter commentary
   - Someone who hasn't seen the interview → full A, complete context
   - Research/writing material → deep commentary, cross-reference external facts

2. **Commentary depth?**
   - Light: flag evasions and contradictions only
   - Deep: add external verification, industry context, pattern analysis
   - Mixed (default): deep on important topics, light on minor ones

If the user hasn't said, default to: **full audience (hasn't seen it) + mixed commentary**.

---

## Step 1: Build the skeleton first (mandatory)

Do NOT start writing Q/A blocks directly. First:

```python
# Parse transcript by timestamp markers
# Split into segments
# Classify each segment: Q / A / QA-mixed
# Merge adjacent same-speaker segments
# Output: numbered list of topics with timestamps
```

Show the skeleton to the user (or just proceed if the task is clear). The skeleton prevents omissions — you're doing a traversal, not a retrieval.

**Typical split logic:**
- Segments starting with filler answers ("Look,", "I think", "No,", "Yes.") → A
- Segments ending in "?" or containing multiple questions → Q
- Long segments with both → QA-mixed (split at last "?" before the answer begins)

---

## Step 2: Clean the questions (Q)

Rules:
- Remove only filler words: `uh`, `um`, `you know`, `I mean`, `like`, `right` (standalone)
- Do NOT rephrase, reorder, or summarize
- Preserve the interviewer's framing, edge, and follow-up logic
- If multiple questions are chained, keep them all — the chain is intentional

---

## Step 3: Paraphrase the answers (A)

Rules:
- Faithful to meaning, not word-for-word
- Preserve specific numbers, named products, named people
- Remove repeated false starts and redundant hedges
- Do NOT editorialize — save that for Commentary
- If the answer spans multiple transcript segments, combine them

---

## Step 4: Write Commentary

Commentary is independent analysis, not a summary of A. Ask:

1. **Did they answer the question?** If not, what did they pivot to and why?
2. **What's the structural tension they avoided?** (e.g. answering "is revenue up?" with "costs are down")
3. **What's verifiable?** Label claims as `[verifiable]`, `[inference]`, or `[industry consensus]`
4. **Is there a better framing they didn't use?** The analogy they gave — does it actually hold?
5. **Pattern across the interview:** (add in meta-analysis section at the end)

For minor/transitional topics, commentary can be 1-2 sentences. For core topics, go deep.

---

## Step 5: Meta-analysis (end of document)

After all Q/A/Commentary blocks, add a section identifying recurring patterns:

- Deflection patterns (e.g. "always cites historical data when asked about future risk")
- Framing choices (e.g. "consistently reframes competitor gaps as 'different markets'")
- The 2-3 moments of genuine candor (these stand out and are high-signal)
- Claims that can be cross-checked against public records

---

## Output formats

**Default (mixed-language):** Q in original language, A paraphrased, Commentary in user's language  
**Full translation:** All three sections translated, technical terms kept in English  
**English only:** All sections in English

Specify at top of document:
```
> Source: [interview name / date if known]
> Note: Q = lightly cleaned original; A = faithful paraphrase; Commentary = independent analysis
> Labels: [verifiable] [inference] [industry consensus]
```

---

## File output

- Single `.md` file per transcript
- If user requests translation, produce two files: `_original.md` and `_cn.md` (or target language)
- Filename: `[interviewee]_[interviewer or publication]_digest.md`

---

## Common failure modes to avoid

| Failure | Fix |
|---|---|
| Skipping segments because they seem minor | Always traverse by timestamp, never by importance |
| Q becomes a summary instead of the original | Only remove filler words — nothing else |
| Commentary becomes a restatement of A | Commentary must add information A doesn't contain |
| All commentary is equally deep | Weight depth by topic importance |
| Missing meta-analysis | Always add the pattern section at the end |
| Treating "no direct answer" as a neutral fact | Name what was avoided and why it likely was |
