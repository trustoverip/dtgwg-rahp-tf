# Repository rulesets

GitHub does not read these files automatically. They are the JSON form of the
rules that protect this repository, kept here so that changes to them can be
reviewed in a pull request and applied by import. Import a file in the web UI
at Settings > Rules > Rulesets > New ruleset > Import a ruleset, or with the
API:

```sh
gh api -X POST repos/trustoverip/dtgwg-rahp-tf/rulesets --input .github/rulesets/main.json
```

Settings exported from the UI or read back from the API carry extra fields
(`id`, `node_id`, `source`, `source_type`, timestamps, `_links`,
`current_user_can_bypass`). They are not needed for import and are left out
here. With those fields removed, `main.json` carries exactly the same values
as the live API response, so a key-sorted diff against the API is a meaningful
check and should print nothing:

```sh
gh api repos/trustoverip/dtgwg-rahp-tf/rulesets/26625043 \
  | jq -S 'del(.id, .node_id, .source, .source_type, .created_at, .updated_at, ._links, .current_user_can_bypass)' \
  | diff - <(jq -S . .github/rulesets/main.json)
```

Sort the keys on both sides: the API orders object keys differently from this
file, and an unsorted diff reports that as a change.

## Current state (read 2026-11-05, ruleset last updated 07:35 -0800)

Two rulesets apply to this repository, one of which this directory tracks.
There is no classic branch protection on any branch:
`GET /repos/trustoverip/dtgwg-rahp-tf/branches/main/protection` returns
`404 Branch not protected`.

| File | Ruleset | Level | Target | Rules | Bypass |
| --- | --- | --- | --- | --- | --- |
| `main.json` | 26625043 `main` | repository | `refs/heads/main` | restrict deletions, block force pushes, require a pull request, require the `EasyCLA`, `DCO` and `validate` checks (strict, not on create) | none |
| none | 20033814 `no creations` | organization | every `trustoverip` repository | block repository creation, deletion and transfer | `clowarden` app, `lfstaff` team |

Ruleset 20033814 has no file here because it is an organization-wide policy
owned by `trustoverip`: it is read-only from this repository and cannot be
imported into it, and the same ruleset applies to every other org repository
(verified against `trustoverip/dtgwg-trust-tasks-spec`). Changing it means
changing org policy, not this repository. Its bypass actors are the
`clowarden` GitHub App (app id 306394, the Linux Foundation's
access-management bot) and the `lfstaff` team (id 18369261), both with
`bypass_mode: always`. Read it with
`gh api repos/trustoverip/dtgwg-rahp-tf/rulesets/20033814`.

### What `main.json` enforces

- **Restrict deletions** — `main` cannot be deleted.
- **Block force pushes** — `main` cannot be force-pushed or otherwise moved
  non-fast-forward.
- **Require a pull request** — every change to `main` must be associated with
  a pull request. Approval is a separate setting and is not required; see
  below.
- **Require status checks** — three checks must pass on the head commit, each
  pinned by `integration_id` to the app that reports it:

  | Context | Required from | App id | Kind |
  | --- | --- | --- | --- |
  | `EasyCLA` | `linux-foundation-easycla` | 17893 | commit status |
  | `DCO` | `dco-2` | 974774 | check run |
  | `validate` | `github-actions` | 15368 | check run |

  `validate` is the job of that name in `.github/workflows/validate.yml`
  (workflow "RAHP validation"). Because each entry names an app id, a check
  reporting the same context from a different app does not satisfy the rule.

  `strict_required_status_checks_policy: true` additionally requires the pull
  request branch to be up to date with `main` before it can merge.
  `do_not_enforce_on_create: true` exempts branch creation, which has no
  effect here because the target is an existing branch.
- **Allowed merge methods** — merge, squash and rebase, all three of which the
  repository also allows, so the ruleset pins the current behaviour rather
  than changing it.
- **Empty bypass list** — `bypass_actors` is `[]`. This was read with a token
  holding repository admin, and the same read returns
  `current_user_can_bypass: "never"`, so the empty list is real and not the
  placeholder a read-only token would see. The `dtgwg-admins` team holds admin
  on this repository and gets no exemption.

### What `main.json` does not enforce

Each of these is a one-line change to the file if the task force wants it
later. None is in force today.

- **No approving review is required.** `required_approving_review_count` is
  `0`. GitHub's wording for the pull request rule is that "the pull request
  doesn't necessarily have to be approved, but it must be opened", which is
  the state here: a pull request is mandatory, an approval is not. The
  related review settings are consequently inert — stale approvals are not
  dismissed on push (`dismiss_stale_reviews_on_push: false`), the most recent
  push does not need approval (`require_last_push_approval: false`), there are
  no required reviewer teams, no dismissal restriction, and conversation
  resolution is not required.
- **`require_extra_approval_for_unattributed_changes` is `true` but has no
  effect.** This is the "Require an additional approval for unattributed
  Copilot pull requests" setting, which GitHub enables by default on new and
  existing rulesets. It asks for one approval more than the configured count
  when Copilot opens a pull request not attributed to a person, and GitHub
  documents that it "has no effect if the ruleset requires zero approvals".
  With the count at `0` it does nothing; it would start mattering the moment
  the count is raised.
- **No code owner review.** The repository has no `CODEOWNERS` file.
- **No linear history requirement**, and merge commits remain an allowed merge
  method, so the two do not conflict.
- **No signed-commit requirement.**

### Direct pushes to `main`

Settled by the pull request rule. GitHub's documentation for it does not use
the words "blocks direct pushes" — it says "all changes to the target branch
be associated with a pull request" — but the practical effect is that work
reaches `main` through a pull request and not by pushing to it. The one case
the page does spell out is that hand-building a merge commit locally and
pushing it fails unless its contents exactly match the merge GitHub would
generate.

This closes a gap that existed before 07:35: with only a required-status-check
rule and no pull request rule, nothing in the ruleset required a pull request,
and GitHub's own documentation does not settle whether a required status check
gates non-pull-request pushes. That ambiguity no longer affects this
repository.

## How changes actually land

The pull-request workflow was already the practice before the rule required
it. `main` carries 25 first-parent commits:

| Origin | Commits |
| --- | --- |
| Pull request merge commits | 22 |
| Squash merges of a pull request (#16, #27) | 2 |
| Initial commit, 2026-03-11 | 1 |

Nobody has pushed a non-initial commit directly to `main`.

Approvals remain the one thing the ruleset leaves open. Of the 24 pull
requests merged into `main` so far:

| Approving reviews at merge | Pull requests |
| --- | --- |
| 0 | 16 |
| 1 | 8 |

Every approval on record came from `NickyHickman` (7) or
`sankarshanmukhopadhyay` (1), and five pull requests were merged by their own
author. All of those merges would still be permitted under the current rules,
because the required count is `0`. Raising it to `1` would have blocked 16 of
the 24 until a second person clicked approve — that is the number to weigh if
the task force considers it, and it is the cost of the change rather than an
argument against it.

Repository access is held by two teams and no direct collaborators:
`dtgwg-admins` (admin) and `dtgwg-maintainers` (maintain).

What does change day to day is CI: `validate`, `DCO` and `EasyCLA` now all
have to pass, where previously a pull request could merge with RAHP
validation failing. Combined with the strict up-to-date policy, a pull request
that falls behind `main` needs "Update branch" and a fresh `validate` run
before it can merge, so a queue of pull requests merges one at a time rather
than in parallel.

## Verifying and changing the ruleset

Read the live state:

```sh
gh api repos/trustoverip/dtgwg-rahp-tf/rulesets
gh api repos/trustoverip/dtgwg-rahp-tf/rulesets/26625043
gh api repos/trustoverip/dtgwg-rahp-tf/rules/branches/main   # no admin needed
```

To change the ruleset, edit `main.json` in a pull request, then apply it:

```sh
gh api -X PUT repos/trustoverip/dtgwg-rahp-tf/rulesets/26625043 \
  --input .github/rulesets/main.json
```

A `PUT` that changes nothing produces no entry in the organization audit log,
so an absent `repository_ruleset.update` event is the proof that a sync was a
no-op.

The organization is on the GitHub Enterprise plan, so rulesets support
`evaluate` enforcement and rule insights. Any further tightening — raising the
approval count, requiring linear history — can be imported as a second ruleset
with `enforcement` set to `evaluate` first, left for a week, and reviewed at
Settings > Rules > Insights, which lists what it would have blocked without
blocking anything. Rulesets targeting the same branch are aggregated and the
most restrictive version of a rule wins, so an `evaluate` ruleset alongside
the active one does not weaken anything.

Rulesets govern git operations, not settings: any repository admin can still
edit or disable this ruleset at Settings > Rules > Rulesets. Doing so is
recorded in the organization audit log as a `repository_ruleset` event, which
makes turning it off a reviewable act rather than a silent bypass.
