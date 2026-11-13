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

`tools/verify_migration.py` checks that nothing was lost when the v5 and v6
workbooks were migrated into `data/`. It needs `openpyxl`:

```bash
python3 tools/verify_migration.py \
  --risk-register archive/legacy-spreadsheets/DTG_RAHP_Risk_Register_v5.xlsx \
  --user-stories archive/legacy-spreadsheets/DTG_RAHP_User_Stories_Framework_v6.xlsx
```
