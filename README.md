# Transcript Processor Skill

A precise workflow tool designed to clean, structure, and optionally analyze raw interview or podcast transcripts into high-fidelity Q&A digests without losing original context.

## Workflow

1. **State the Plan:** Infer mode and target language, present the execution plan, and wait for explicit user confirmation.
2. **Run Parser:** Execute `python3 scripts/parse_transcript.py <file>` to generate a timestamp skeleton to prevent missing any segments. Skipped in upgrade mode.
3. **Clean & Format:** Clean filler words/false starts while strictly preserving the speaker's original words (no paraphrasing/summarizing).
4. **Translate (if applicable):** Translate Q/A into target language after cleaning. Skipped if output language matches transcript language.
5. **Analysis (Digest Mode Only):** Append hard-hitting commentary for each exchange and a final meta-analysis section.

## Modes

- **Clean Mode (Default):** Outputs strict `Q (with timestamp)` and `A` blocks only. No external summary or commentary.
- **Digest Mode:** Adds deep analysis layer (`Commentary`) identifying avoided tensions, verifiable claims, and a concluding `Meta-analysis` of recurring patterns.
- **Upgrade Mode:** Takes an existing clean `.md` file and adds Commentary and Meta-analysis directly. Skips parser and clean steps entirely; Q and A text is read-only.

## File Output
Saves results into `[interviewee]_[source]_[mode].md` and runs `scripts/check_digest.py` before completion.