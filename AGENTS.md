# Project Guidelines

## Product Goal

Build a desktop application for creating targeted email recipient lists for a healthcare organization of more than 12,000 employees. Users must be able to combine organization, person, role, and position criteria, inspect the matches, and export usable recipient addresses.

Use Finnish for user-facing text unless a task explicitly requires another language. Prefer clear healthcare-administration terminology over internal implementation terms.

## Current State

- `app.html` and `index.js` are a graphical prototype only. They are not the final architecture, data model, or implementation. Preserve useful interaction ideas when appropriate, but replace or restructure them freely when implementing production features.
- `example_data.csv` is the current employee data source and source of truth for the development schema. It contains synthetic development data.
- There is no tag file yet. Do not invent tag records, a join key, or a tag-server contract. Keep future tag enrichment behind a clear data-source boundary so it can be added once the file format and shared key are known.
- Production Entra and tag-server integrations are out of scope until explicitly requested. Development must work with local CSV or JSON files.

## Required Recipient Filters

Support combining multiple selected values and text searches for at least:

- business area (`BusinessArea`, Toimiala)
- responsibility area (`ResponsibilityArea`, Vastuualue)
- service area (`ServiceArea`, Palvelualue)
- service unit (`ServiceUnit`, Palveluyksikkö)
- office / lowest organization level (`Office`, Toimipiste)
- primary work city (`City`, Paikkakunta)
- workplace location and address (`WorkLocation` and `StreetAddress`)
- job title (`Title`, Ammattinimike)
- supervisor role
- person fields such as `DisplayName`, `EmployeeId`, and `EmailAddress`

Treat selections within one field as OR and selections across different fields as AND unless the UI explicitly communicates different behavior. Make active criteria visible and easy to clear.

The CSV has no explicit supervisor-role column. Derive supervisor status by checking whether an employee's `EmployeeId` is referenced by another row's `Manager` field. Treat `Manager` as a direct manager relationship; do not silently expand it to all indirect reports. Keep this derivation isolated so a future authoritative role or tag can replace it.

## Data Handling

- Parse CSV with a standards-compliant CSV library; quoted fields contain commas and semicolon-delimited organization text.
- Preserve the original CSV field names at the ingestion boundary. Map rows into a documented internal employee model before filtering.
- Match identifiers exactly after safe whitespace normalization. Do not use names or email addresses as relationship keys.
- Handle missing values, malformed rows, duplicate employee IDs, duplicate email addresses, unknown manager IDs, and invalid email addresses explicitly.
- Filtering and previewing may show data-quality issues, but recipient exports must not silently include blank or invalid addresses. Deduplicate exported addresses case-insensitively and report excluded rows to the user.
- Do not mutate `example_data.csv` as part of normal application behavior or tests.
- Keep data processing efficient for at least 12,000 employee rows. Avoid reparsing the file or rebuilding all indexes on every filter interaction; paginate or virtualize large result previews.

## Exports

At minimum, provide:

- Windows-compatible clipboard output containing valid, unique email addresses in a form that can be pasted into mail recipient fields
- CSV export suitable for systems such as Creamailer, with explicit UTF-8 encoding and deterministic headers

Outlook draft creation and To/Cc/Bcc selection are future work unless explicitly requested. Keep export logic separate from filtering so additional destinations can be added without changing recipient matching.

## Architecture And Security

- Keep file access and privileged Electron operations outside the renderer. Use context isolation, no renderer Node integration, a narrow preload API, and validated IPC messages.
- Separate data ingestion and normalization, recipient filtering, data-quality validation, export formatting, and UI rendering.
- Treat future real employee data as sensitive personal data. Do not send it over the network, persist it unexpectedly, expose unrestricted file-system APIs, or log complete employee rows and recipient lists.
- Make the selected source, row count, filter criteria, match count, exclusions, and export count visible so users can verify why a list was produced.
- Prefer deterministic, explainable matching over fuzzy or implicit rules. A user should be able to inspect why each recipient matched.

## Testing And Validation

Add focused automated tests as functional code is introduced. Cover at least:

- parsing quoted CSV values and Finnish characters
- every required filter and combinations of filters
- direct-manager and supervisor derivation
- missing, invalid, and duplicate email handling
- clipboard and CSV export formatting
- behavior with empty files, missing columns, unknown managers, and datasets of at least 12,000 rows

Keep pure filtering, validation, and export functions independent of Electron so they can be unit tested. Add working `package.json` scripts for tests, linting, and other checks when those tools are introduced. Do not treat the current placeholder `npm test` script as a valid test run.

Current prototype command:

```sh
npm install
npm start
```

After changes, run the narrowest relevant automated checks and then exercise the affected Electron workflow. Document any validation that cannot be run.
