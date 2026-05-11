# Skill Registry

Generated: 2026-05-10
Source: ~/.config/opencode/skills/
Project: nutristore

> Auto-resolved by sdd-init. Skip `sdd-*`, `_shared`, and `skill-registry` skills.

---

## User-Level Skills

### work-unit-commits
- **Path**: ~/.config/opencode/skills/work-unit-commits/SKILL.md
- **Trigger**: implementation, commit splitting, chained PRs, or keeping tests and docs with code
- **Compact Rules**:
  - Commit by work unit (deliverable behavior), NOT by file type
  - Keep tests & docs with the code they verify — same commit
  - Each commit must be a reviewable story with clear start/end/rollback
  - If SDD forecasts >400 lines, group into chained PRs before implementing
  - Use Conventional Commits: `type(scope): description`
  - Future PR-ready: each commit should be a candidate chained PR slice

### comment-writer
- **Path**: ~/.config/opencode/skills/comment-writer/SKILL.md
- **Trigger**: PR feedback, issue replies, reviews, Slack messages, or GitHub comments
- **Compact Rules**:
  - Start with the actionable point — do NOT recap the whole context
  - Be warm + direct like a thoughtful teammate, not a corporate bot
  - 1–3 short paragraphs max; explain WHY when asking for a change
  - Match thread language; use Rioplatense voseo in Spanish (`podés`, `fijate`)
  - No em dashes — use commas/periods/parentheses instead
  - Avoid pile-ons: comment on the highest-value issue only

### cognitive-doc-design
- **Path**: ~/.config/opencode/skills/cognitive-doc-design/SKILL.md
- **Trigger**: writing guides, READMEs, RFCs, onboarding, architecture, or review-facing docs
- **Compact Rules**:
  - Lead with the answer: put the decision/outcome first, context after
  - Progressive disclosure: happy path first, then edge cases and details
  - Chunk info into small sections with clear signposting headings
  - Prefer tables, checklists, and examples over prose that must be remembered
  - Design for review empathy: make verification intent obvious

### chained-pr
- **Path**: ~/.config/opencode/skills/chained-pr/SKILL.md
- **Trigger**: PRs over 400 lines, stacked PRs, review slices
- **Compact Rules**:
  - Split PRs over **400 changed lines** unless maintainer accepts `size:exception`
  - Each PR must be reviewable in ~≤60 minutes with one work unit
  - State start/end/dependencies/out-of-scope in every chained PR
  - Include dependency diagram marked with `📍` in child PRs
  - Feature Branch Chain: draft/no-merge tracker PR; child PR #1 targets tracker, later children target immediate parent
  - Do not mix chain strategies after user chooses one

### issue-creation
- **Path**: ~/.config/opencode/skills/issue-creation/SKILL.md
- **Trigger**: creating GitHub issues, bug reports, or feature requests
- **Compact Rules**:
  - MUST use a template (bug_report or feature_request) — blank issues disabled
  - Every issue gets `status:needs-review` on creation automatically
  - Maintainer MUST add `status:approved` before any PR can be opened
  - Questions go to Discussions, NOT issues
  - Search for duplicates before creating a new issue

### branch-pr
- **Path**: ~/.config/opencode/skills/branch-pr/SKILL.md
- **Trigger**: creating, opening, or preparing PRs for review
- **Compact Rules**:
  - Every PR MUST link an approved issue (label: `status:approved`)
  - Branch naming: `type/description` with `a-z0-9._-` chars only
  - PR body MUST include: linked issue, PR type, summary, changes table, test plan
  - Exactly one `type:*` label per PR
  - Use Conventional Commits: `type(scope): description`
  - Automated checks must pass before merge

### skill-creator
- **Path**: ~/.config/opencode/skills/skill-creator/SKILL.md
- **Trigger**: new skills, agent instructions, documenting AI usage patterns
- **Compact Rules**:
  - A skill is an LLM runtime instruction contract, NOT human documentation
  - Frontmatter MUST have: name, description, license, metadata.author, metadata.version
  - `description`: one physical line, quoted, ≤250 chars, trigger words first
  - Keep body 180–450 tokens (max 700); move detail to `references/` or `assets/`
  - Section order: Activation Contract → Hard Rules → Decision Gates → Execution Steps → Output Contract → References

### go-testing
- **Path**: ~/.config/opencode/skills/go-testing/SKILL.md
- **Trigger**: Go tests, go test coverage, Bubbletea teatest, golden files
- **Compact Rules**:
  - Prefer table-driven tests with `t.Run(tt.name, ...)` for multiple cases
  - Test behavior and state transitions, NOT implementation trivia
  - Use `t.TempDir()` for filesystem tests — never rely on real home dir
  - Integration tests MUST be skippable with `testing.Short()`
  - Bubbletea: test `Model.Update()` directly; teatest only for interactive flows
  - Golden files must be deterministic; update via `-update` flag only

### judgment-day
- **Path**: ~/.config/opencode/skills/judgment-day/SKILL.md
- **Trigger**: judgment day, dual review, adversarial review, juzgar
- **Compact Rules**:
  - Always launch TWO blind judges in parallel with identical target/criteria
  - NEVER review code yourself; NEVER accept a partial verdict
  - `WARNING (real)` only when normal intended use can trigger it; else downgrade to INFO
  - Ask before fixing Round 1 confirmed issues
  - After fixes, re-judge before commit/push/done
  - Terminal states: `JUDGMENT: APPROVED` or `JUDGMENT: ESCALATED`
  - After 2 fix iterations with remaining issues, ask user whether to continue

---

## Project Convention Files

No project-level AGENTS.md or convention files detected.
