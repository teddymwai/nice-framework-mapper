# Team Guide: Test, Stage, Commit, and Promote Safely (`push2git.md`)

This guide defines the end-to-end review, verification, commit, and 3-tier release promotion workflow for **NICE Framework Mapper** (Lead: **Ted Mwai**): inspect the worktree, run the 7-check pre-commit gate, sanitize artifacts, author a blast-radius commit message, push to `beta/unstable-nightly` or `staging`, and fast-forward certified changes to `main`.

---

## 1. Foundational Release & SDLC Mandates

1. **3-Tier Branch Isolation & Promotion Pipeline**:
   ```text
   beta/unstable-nightly (or beta-<Feature>) ──(Regression Certification)──> staging ──(Fast-Forward GA)──> main
   ```
   - **`beta/unstable-nightly` (or `beta-<Feature>`)**: Rapid iteration of bleeding-edge orchestrators, experimental contracts, and new reporting engines. Verify `git branch --show-current` before committing experimental work.
   - **`staging`**: Pre-release integration and live staging certification.
   - **`main`**: Certified production baseline. **Never commit directly to `main`** and never run `git push --force` on shared branches (`beta/*`, `staging`, `main`).
2. **Environment & Mutation Safety**:
   - All tools and runners resolve target endpoints dynamically via `--deployment` / `-d`.
   - Production is strictly read-only by default. Mutating actions against production require explicit `--allow-mutation` on CLI runs and the affirmative `PROD-MUTATE` token on web dashboards.
3. **Interactive Dashboard & Dynamic Tool Architecture (Rule #4 & Rule #8)**:
   - Every tool under `tools/<tool>/` must include a 5-section senior-engineer `README.md` (*Architectural Overview*, *Deployment & Environment Resolution*, *Credential & Authentication Guide*, *How to Run*, *Output Artifacts*).
   - Every dashboard under `tools/<tool>/static/` must be named `<tool>_dashboard.html` (never naked `index.html`) and implement all 7 interactive capabilities (run creation deck, live event monitor, multi-session `409` one-click reset, state hydration on refresh, in-app report drawer with on-demand markdown synthesis, `--dashboard` in-tandem daemon lifecycle, and `file://` offline preview mode).
   - Historical or deprecated scripts must be quarantined under `tools/legacy/archive/` or archived via the **Commit-and-Purge Reference Pattern**.
4. **Tiered Docs-as-Code & Single Canonical Roadmap**:
   - Durable specifications (`specs/`), constitutions (`AGENTS.md`, `HARNESS.md`), release register (`docs/RELEASE_REGISTER.md`), paginated changelog (`CHANGELOG.md`), and the **single canonical roadmap** (`docs/UPCOMING_FEATURES.md`) are tracked in Git.
   - Volatile sprint scratchpads and daily manual QA logs are externalized to Notion (`docs/trackers/README.md`).
5. **Commit Subject Integrity**:
   - When the lead or operator specifies an exact commit subject line, preserve that requested first line **verbatim** while structuring the commit body with `Why:`, `Trade-off:`, and `Touches:`. Never `--amend` commits already pushed to remote.

---

## 2. Inspect Worktree Before Staging

From the repository root:

```bash
git status --short --branch
git branch -avv
git log -5 --oneline --decorate
git diff --stat
git diff
git diff --cached --stat
git ls-files --others --exclude-standard
```

Confirm the current branch and target remote before staging. Inspect all new and untracked files; never stage raw production HARs, `.session_cache.json`, `creds*.txt`, or runtime `output/` captures.

---

## 3. Execute the 7-Check Pre-Commit & Pre-Promotion Gate ("Forgotten Bits" Gate)

All seven validation gates must pass before staging or promoting branches:

```bash
# Gate 1: Full-Tree Bytecode & Syntax Compilation (100% of Python files)
python3 -m compileall -q lib tools tests templates 2>/dev/null || python3 -m compileall -q .

# Gate 2: Offline Harness Self-Test (1:1 Registry <-> Manifest <-> Physical Spec-on-Disk Parity & AST Import Boundaries)
python3 templates/tool_boilerplate.py --selftest
python3 templates/server_boilerplate.py --selftest
python3 templates/ultrared_reporting.py --selftest

# Gate 3: Unit, Orchestrator & Contract Resolution Tests
python3 -m unittest discover -s tests -p "test_*.py" 2>/dev/null || true

# Gate 4: TedRedCraft Tier 1 Fast Polyglot SAST (<1.5s pre-commit)
PYTHONPATH=/Users/ted/Development/TedRedCraft python3 -m redcraft audit --target . --mode pre-commit

# Gate 5: TedRedCraft Tier 2 Ephemeral Loopback DAST (<4s pre-push)
PYTHONPATH=/Users/ted/Development/TedRedCraft python3 -m redcraft audit --target . --mode pre-push
```

### Non-Negotiable Hygiene Invariants
1. **Tests & Docs Ship With the Feature**: Never defer invariant tests, `README.md` guides, `CHANGELOG.md` entries, or `docs/UPCOMING_FEATURES.md` updates to a follow-up commit.
2. **1:1 Registry, Manifest & Physical Spec Parity**: Every registered suite must exist in `manifest.toml` and have a physical markdown file under `specs/`.
3. **Contract Canonicalization**: All contracts follow `<suite_code_lower>.contract.toml` with `[needs]`, `[uses]`, `[produces]`, and `[decommission]` blocks and zero squashed duplicates (`mp01` vs `mp_01`).
4. **Web Surface Confinement (`SEC-01`..`SEC-04` & `SEC-JS-INNER-HTML`)**: Local dashboard servers bind `127.0.0.1`, enforce `MAX_BODY_BYTES = 1_048_576`, verify `hmac.compare_digest` CSRF tokens, confine paths with `.resolve().is_relative_to()`, and escape dynamic DOM strings.
5. **Release Register & SHA Synchronization**: `CHANGELOG.md`, `docs/RELEASE_REGISTER.md`, and `docs/releases/RELEASE_NOTES_*.md` must carry matching Ptarmigan (*Lagopus*) taxonomic tags, dates, and commit SHAs.

---

## 4. Stage Explicit Paths & Run Secret Interception Scans

Never use `git add -A` or `git add .`. Stage explicit file paths only:

```bash
git add <path/to/file1> <path/to/file2>
git diff --cached --stat
git diff --cached --check
```

Run the mandatory staged path and credential interception checks (both grep commands must yield **zero** matches):

```bash
# 1. Forbidden path check (secrets, session caches, raw HARs, runtime outputs, OS metadata)
git diff --cached --name-only | grep -E '(^|/)(creds([.]|$)|\.session_cache\.json|\.venv|output/.*/(responses|screenshots)|.*\.har$|.*\.zip$|\.DS_Store)'

# 2. Staged content credential scan
git diff --cached | grep -Ein 'authorization|bearer |set-cookie|password|access_token|refresh_token|sessionid'
```

If any forbidden path or token is detected, unstage immediately:
```bash
git restore --staged <forbidden-path>
```

---

## 5. Senior-Engineer Commit Protocol & Blast-Radius Audit

### 5.1 Commit Message Structure

```text
type(scope): imperative summary <= 72 chars

Why: 1-3 lines explaining what changed, the root cause, and what it replaces.
Trade-off: architectural forks, performance vs. memory trade-offs, or deferrals; omit if none.

Touches: AREA1, AREA2, AREA3
Refs: #PR or issue number
```

- **`type`**: `feat`, `fix`, `test`, `refactor`, `docs`, `perf`, `chore`.
- **`scope`**: Affected subsystem (`runner`, `safety`, `auth`, `dashboard`, `reporting`, `contracts`, `rules`).
- **Operator-Specified Subjects**: If the operator provides a custom first line, use it verbatim on line 1 and include `Why:`, `Trade-off:`, and `Touches:` in the body.

### 5.2 Blast-Radius Checklist (`Touches:`)

| Area | Target Files | Fire When |
|---|---|---|
| **Specs** | `specs/**/*.md` | Requirements, steps, assertions, or lifecycle contracts change. |
| **Framework Core** | `lib/framework/`, `redcraft/` | Safety guards, session manager, reporting engine, or SAST/DAST rules change. |
| **Test Suites** | `lib/suites/`, `tests/` | Suite logic, locators, payloads, or teardown assertions change. |
| **Deployments & Config** | `config/` | Deployment URLs, profiles, contracts, or manifest governance change. |
| **Operational Tools** | `tools/`, `templates/` | Standalone runners, control-plane servers, or CLI utilities change. |
| **UI & Dashboards** | `tools/**/static/*_dashboard.html` | Web dashboards change (verify `#0e3f2a` / `#0d1310` palette, Studio Curve canvas, zero emojis, 44px capsules, `TooltipManager`). |
| **HAR Wire Reference** | `reference/sanitized/*.har` | Sanitized wire archive updated (`--sanitize-to-file` verified). |
| **Docs & Release Notes** | `README.md`, `CHANGELOG.md`, `docs/` | Operator guides, `UPCOMING_FEATURES.md`, or `RELEASE_REGISTER.md` change. |

*(For purely internal refactors with zero external blast radius, write `Touches: none (internal)`.)*

---

## 6. Push to Nightly / Staging & Fast-Forward Promotion to Main

### 6.1 Pushing to Nightly or Staging
```bash
git fetch origin
git status --short --branch
git log --oneline --decorate origin/<branch>..<branch>
git push origin <branch>
```

### 6.2 Fast-Forward Promotion to `main` & Taxonomic Tagging
Once all 7 gates pass on `staging` and release sign-off is granted:

```bash
# 1. Fetch latest remote state and verify fast-forward ancestry
git fetch origin
git merge-base --is-ancestor origin/main origin/staging

# 2. Resolve and validate Ptarmigan (Lagopus) release tag
python3 templates/release_tagger.py --bump minor

# 3. Fast-forward merge into main
git switch main
git pull --ff-only origin main
git merge --ff-only origin/staging

# 4. Apply annotated Lagopus release tag and push with tags
git tag -a "<LagopusIdentifier>" -m "NICE Framework Mapper Platform <vX.Y.Z> - <Lagopus Species Subspecies>"
git push origin main --follow-tags

# 5. Publish verbose GitHub Release notes
gh release create "<LagopusIdentifier>" \
  --title "NICE Framework Mapper Platform <vX.Y.Z> - <Lagopus Species Subspecies>" \
  --notes-file docs/releases/RELEASE_NOTES_<vX.Y.Z>.md
```

---

## 7. Historical Legacy Quarantine & "Commit-and-Purge" Pattern

When legacy proof-of-concept scripts should be recorded in git history for lineage reference without remaining in the active working tree:
1. **Commit 1 (Restore Sanitized Archive)**: Redact all tokens/cookies to placeholders, strip executable bits, place under `tools/legacy/archive/`, and commit:
   ```text
   chore(archive): restore sanitized legacy sample scripts for historical reference

   Why: Preserve early proof-of-concept scripts in git lineage with all authentication tokens redacted.
   Trade-off: Adds historical lines to git object store before immediate working-tree removal.
   Touches: tools/legacy
   ```
2. **Commit 2 (Purge from Active Working Tree)**: Immediately remove `tools/legacy/` in the next commit, citing Commit 1's short SHA in the subject:
   ```text
   Cleaned up legacy files - see prev <short-sha> for legacy details.

   Why: Purge quarantined legacy scratchpads from the active working tree while preserving historical record in commit <short-sha>.
   Trade-off: Requires git checkout <short-sha> -- tools/legacy/ to inspect historical files.
   Touches: tools/legacy
   ```

---

## 8. Emergency Secret Scrubbing & Remote Tag Governance (`GH013`)

### 8.1 Deleting Protected Tags Tied to GitHub Releases (`GH013`)
If `git push origin --delete <tag>` fails with `remote: error: GH013: Repository rule violations found`, the tag is pinned to a published GitHub Release. Delete both the release and tag cleanly with GitHub CLI:

```bash
gh release list --repo <owner/repo>
gh release delete <tag_name> --repo <owner/repo> --yes --cleanup-tag
```

### 8.2 Clean-Slate Orphan History Reset
If historical commits across branches contain exposed secrets and rebasing causes intractable conflicts:

```bash
# 1. Backup .git directory
cp -R .git ../repo_git_backup

# 2. Create clean orphan root commit
git checkout --orphan clean-slate
git add <explicit-sanitized-files>
git commit -m "feat(release): initial clean-slate release of NICE Framework Mapper"

# 3. Synchronize branches
git branch -M main
git push origin main --force
git push origin main:staging --force
git push origin main:beta/unstable-nightly --force
```
