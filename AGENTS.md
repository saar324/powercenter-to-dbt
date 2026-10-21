# Assignment documentation

The submission requirements are in `docs/assignment.md`. During authorized BMAD work, capture the required evidence as it occurs. These instructions concern documentation only; they do not select a solution, start a workflow, or authorize implementation or submission.

## Use existing BMAD records

- Keep requirements, assumptions, exclusions, and decisions in the normal BMAD specification, companions, and memory log.
- Keep implementation notes, actual verification commands/results, and review findings in the normal BMAD implementation and review records.
- Use those records and Git history for the short account of the process followed. Do not create a parallel work log, decision log, or test-results document with the same content.

## Capture the assignment-specific evidence

- Preserve actual task-related prompts when they are received or dispatched, starting with the initial prompt. Use `docs/agent-prompts.md` unless a shareable task conversation export already preserves them. Keep exact wording, identify user versus agent-written prompts, and include the date and relevant artifact links. If an exact prompt is already stored in a transcript or BMAD artifact, reference its location instead of copying it again. Do not reconstruct unavailable text or claim a partial log is complete.
- If the host can export the full task conversation, include that export as the brief requests. Keep a single prompt source and link to it. Exclude credentials, unrelated personal context, and the private submission URL; identify any redactions. If export is unavailable, state that accurately.
- When an actual agent mistake is caught, preserve what was wrong, who or what caught it, the concrete detection evidence, and the correction. Use the existing review or implementation record when it already contains this information. Add only the missing detection/correction detail there. Never invent an incident or describe an unresolved assumption as a proven mistake.
- The setup scope error is already documented in README.md under "Agent error caught during setup". Reference that entry; do not duplicate it.

## Keep the README current

As working behaviour and evidence become available, maintain a short submission summary covering: actual run instructions; assumptions and deliberately unsupported cases; where incorrect output is most likely and why; an actual agent mistake and how it was caught; a link to the prompts or conversation export; and a short account of the process actually followed.

Link to the authoritative BMAD records instead of repeating their contents. Do not invent commands, limitations, decisions, test results, or completed stages. Before finishing a work unit, update only the documentation affected by that unit. At final review, check every item in the assignment's "What to submit" list and state any missing evidence honestly.
