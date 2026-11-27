# Archive

**Historical artefacts. Do not edit.** Current canonical RAHP data is maintained
under `data/` and `method/`; current views are generated into `build/` by
`python3 tools/build.py`.

These files are kept for provenance and migration history.

| Folder | Contents |
|---|---|
| `legacy-spreadsheets/` | Risk Register v5 and User Stories Framework v6: the workbooks the YAML in `data/` was migrated from (August 2026). Also the earlier Risk Register v4 and User Stories Framework v3. All superseded by `data/`. |
| `legacy-documents/` | Personas and Priority Requirements Word documents, and the original workflow reference page |
| `historical-builds/` | Generated site pages, JSON-LD and exports committed with the v0.3 upload (`f74b8a4`). Regenerate rather than edit. |

## Checking the migration

`tools/verify_migration.py` checks key parts of the migration of the v5 and v6
workbooks into `data/`. It needs `openpyxl`:

```bash
python3 tools/verify_migration.py \
  --risk-register archive/legacy-spreadsheets/DTG_RAHP_Risk_Register_v5.xlsx \
  --user-stories archive/legacy-spreadsheets/DTG_RAHP_User_Stories_Framework_v6.xlsx
```

### What it checks, and what it doesn't

When it reports `PASS`, these checks passed:

- **Identifiers:** the sets of risk, control, guardrail, assurance test, user story,
  scenario and metric IDs in the workbooks match those in `data/`.
- **Text:** risk and control descriptions are identical.
- **Scores:** the overall counts of each severity and likelihood value match. Each
  risk's own score isn't compared.
- **Risk cross-references, one way:** every metric, guardrail, control, assurance test,
  user story and scenario that a risk names in the Risk Register also appears in that
  risk's list in `data/risks.yaml`.

It doesn't check:

- other fields (names, owners, rationale and so on);
- cross-references the other way: `data/` may hold links the workbook doesn't;
- cross-references held on records other than risks;
- risk-to-epic links. The "risk cross-reference edges" total it prints includes them,
  but they aren't compared with the workbook.

So `PASS — no data loss` means these checks passed. It isn't proof that the YAML is
equivalent to the workbooks in every field.

### The archived workbooks

SHA-256 of the files the check was last run against (27 November 2026):

| File | SHA-256 |
|---|---|
| `legacy-spreadsheets/DTG_RAHP_Risk_Register_v5.xlsx` | `9953fb0e04d8e1b51643a0ed9b9733d7b63ba8b671f67bcffc10fba8fd0fd9ae` |
| `legacy-spreadsheets/DTG_RAHP_User_Stories_Framework_v6.xlsx` | `1a3ab3119fb738a7ce57e19f547ab060c67e413bc65478e3fb9854e756329b50` |

Check them with `sha256sum archive/legacy-spreadsheets/*.xlsx`.
