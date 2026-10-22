# Assignment documentation

The submission requirements are in `docs/assignment.md`. During authorized BMAD work, capture the required evidence as it occurs. These instructions concern documentation only; they do not select a solution, start a workflow, or authorize implementation or submission.

## Design discussions with Saar

Discuss the system design and meaningful trade-offs at the appropriate level: data flow, responsibilities, correctness, support boundaries and material scope or effort changes. Present a coherent recommendation and explain why. Handle routine file layout, settings and implementation details as engineering work; do not ask Saar to approve each small detail or answer terminology quizzes. Ask one clear question at a time, in simple ASD-STE100 English, when a real owner decision remains. Preserve existing decisions and avoid repeated approval questions for unchanged scope. This follows Saar's explicit correction in U72 and reminder in U73 in `docs/agent-prompts.md`.

## Use existing BMAD records

- Keep requirements, assumptions, exclusions, and decisions in the normal BMAD specification, companions, and memory log.
- Keep implementation notes, actual verification commands/results, and review findings in the normal BMAD implementation and review records.
- Use those records and Git history for the short account of the process followed. Do not create a parallel work log, decision log, or test-results document with the same content.
- The user's requested `reports/test-runs.csv` is the single machine-readable history of actual test runs; `reports/validation.md` summarizes it. Native verification records link the command, evidence and report instead of copying rows. The reporting contract is in the native SPEC's `validation-and-reporting.md` companion. Do not create results before tests run.

## Submission transparency

- Include the relevant development record in the submission: supplied materials and provenance, source and tests, BMAD framework and shared configuration, native requirements and memory, research, prompts, implementation and review evidence, measured reports, CI configuration, dependency manifests and lockfiles, and Git history when submitting a repository.
- Exclude installed dependencies (`node_modules/`, `.venv/`), generated tool caches, credentials and machine-only settings. Declare and lock dependencies so reviewers can restore them. Do not ignore relevant requirements, reviews or test evidence as temporary files.
- Preserve the specific confidentiality and redaction rules below. General transparency does not authorize disclosure of the earlier private project. Distinguish locally prepared evidence from committed or uploaded evidence; this policy does not authorize pushing or submitting the repository.

## Capture the assignment-specific evidence

- The earlier employer/project referenced privately by Saar is confidential. Do not include its identity, repository paths, code, architecture or implementation details in this repository, reports or submission. Do not copy its code. Preserve only generic conclusions grounded in public sources; redact private identifiers from the prompt record and any conversation export.
- Preserve actual task-related prompts when they are received or dispatched, starting with the initial prompt. Use `docs/agent-prompts.md` unless a shareable task conversation export already preserves them. Keep exact wording, identify user versus agent-written prompts, and include the date and relevant artifact links. If an exact prompt is already stored in a transcript or BMAD artifact, reference its location instead of copying it again. Do not reconstruct unavailable text or claim a partial log is complete.
- If the host can export the full task conversation, include that export as the brief requests. Keep a single prompt source and link to it. Exclude credentials, unrelated personal context, and the private submission URL; identify any redactions. If export is unavailable, state that accurately.
- When an actual agent mistake is caught, preserve what was wrong, who or what caught it, the concrete detection evidence, and the correction. Use the existing review or implementation record when it already contains this information. Add only the missing detection/correction detail there. Never invent an incident or describe an unresolved assumption as a proven mistake.
- The setup scope error is already documented in README.md under "Agent error caught during setup". Reference that entry; do not duplicate it.
- Capture relevant user directions as they arrive in the native memory, with the exact prompt or a link to its existing location. Distinguish user decisions from questions, agent proposals and researched facts. Record actual delegated prompts in the same prompt source. At the end of each work unit check that the latest direction, changed decisions, commands/results and actual agent corrections are recorded in their authoritative locations.

## Measured reporting and practical follow-up

- Keep test outcomes, complete-result checks and supported-path coverage separate, with explicit counts/denominators, tested revision, fixture and actual environment. A correctly rejected unsupported case can pass a test while remaining unsupported. Do not report one universal accuracy score or treat successful compilation as result equivalence.
- Keep the report minimal. Summarize verified strengths, observed failures, deliberate unsupported cases and untested risks; link native evidence. For remaining work state the evidence, concrete proposed change and acceptance test. Include researched source-product/version extension considerations without claiming those formats are supported.
- The final summary must identify its final tested revision. Preserve prior run history, but do not combine old and final runs into a claimed final correctness rate.

## Keep the README current

Every employer "What to submit" item is part of basic-stage completion, not optional or bonus work. Do not call the core complete based on SQL output alone. Required tests, reproducible run instructions, assumptions/exclusions, wrong-output risks, genuine agent-error evidence, prompts/export handling and the actual process outline must be ready with it. Preserve prompts, decisions and real failures as they occur rather than reconstructing them at the end.

As working behaviour and evidence become available, maintain a short submission summary covering: actual run instructions; assumptions and deliberately unsupported cases; where incorrect output is most likely and why; an actual agent mistake and how it was caught; a link to the prompts or conversation export; and a short account of the process actually followed.

Link to the authoritative BMAD records instead of repeating their contents. Do not invent commands, limitations, decisions, test results, or completed stages. Before finishing a work unit, update only the documentation affected by that unit. At final review, check every item in the assignment's "What to submit" list and state any missing evidence honestly.
