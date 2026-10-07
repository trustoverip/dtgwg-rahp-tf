# Repository validation and reproduction evidence

The workflow in [`.github/workflows/validate.yml`](../.github/workflows/validate.yml) replaces the inactive root workflow template. It runs on pull requests, pushes to `main`, and manual dispatch once available on the default branch.

It checks repository integrity and reproduction. A successful run is not evidence that a target specification or deployment passed assurance, nor that an independent human review occurred.

## Checks

1. Install the repository requirements under Python 3.11.
2. Record the actual checked-out revision, run/attempt, interpreter and dependency versions. On a pull request this revision may be GitHub's synthetic merge commit, rather than the author's branch head.
3. Run `python3 tools/validate.py --json` against canonical records. Errors fail the job. Warnings are retained in the report and summary; they are not promoted to errors by this contribution.
4. Run all repository and specification-review unit tests, including negative fixtures.
5. Validate the existing minimal specification-review example.
6. Build into the runner's temporary directory, retain the generated bundle, and record SHA-256 file digests. Check that tracked source files did not change.

After a check fails, independent checks still run if dependency installation succeeded. Evidence upload and summary are attempted even on failure. Missing, incomplete, failed or skipped evidence must not be treated as success.

## Preserved evidence

Each run publishes `rahp-validation-<run-id>-<attempt>` with 14-day retention:

- `rahp-validation/execution.json`: revision and runtime provenance;
- `rahp-validation/corpus-validation.json`: full corpus errors, warnings and counts;
- regression, review and build logs;
- `rahp-validation/generated-files.json`: generated-file digests; and
- `rahp-build/`: the generated views and local JSON-LD context.

Artifacts are available for successful and failed runs when files were produced. Run links and artifact digests should be preserved separately when long-term evidence is needed; a short-lived Actions artifact is not a permanent qualification record. GitHub retains the execution logs according to repository settings.

## Local reproduction

From a checkout with the repository requirements installed:

```bash
python3 tools/validate.py --summary
python3 -m unittest discover -s tests -v
python3 review/validate_spec_review.py review/examples/minimal-review.yaml
python3 tools/build.py --out /tmp/rahp-build
```

The validator and build commands run from `tools/`; canonical instance data is under `data/`, and method contracts are under `method/`. Generated output stays separate from canonical input. Existing published root artifacts are not rewritten or deployed by this workflow.

## Execution boundary

The workflow has read-only repository permissions, uses commit-pinned actions, does not persist checkout credentials, and does not deploy, create releases, merge PRs or modify repository settings. This contribution does not make its check a required branch-protection rule; upstream maintainers own that policy decision.

This contribution was reconciled onto current `main` after the layout restoration in #16. Its workflow and reproduction commands use the canonical `tools/`, `data/`, `method/`, and `context/` layout.
