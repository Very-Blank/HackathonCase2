Juhon branch mee pois

# Synthetic directory data

This workspace contains a deterministic generator for development data modeled
on the supplied Keski-Suomen hyvinvointialue directory examples.

## Generate the default dataset

```bash
python generate_data.py
```

The command creates `data/keski_suomen_hyvinvointialue_users.csv` with 15,000
synthetic rows. The output is already at the readable, post-processing stage:
the hierarchy is represented by `Organization`, `BusinessArea`,
`ResponsibilityArea`, `ServiceArea`, `ServiceUnit`, `WorkLocation`, and
`EmployeeOrgData`. The six hierarchy levels are `Hyvinvointialue`, `Toimiala`,
`Vastuualue`, `Palvelualue`, `Palveluyksikkö`, and `Toimipiste`.

`EmployeeId` is a synthetic person ID. The `Manager` field contains the
`EmployeeId` of the person's manager, not the manager's display name. Manager
links always point upwards one level, and the top-level `Hyvinvointialue`
record has an empty `Manager` value. Raw numeric `extensionAttribute` values
are intentionally not exported.

The generator uses only Python's standard library. It accepts:

```bash
python generate_data.py --rows 15000 --seed 20260917 --output data/example.csv
```

All names, phone numbers, and email addresses are synthetic. Email addresses
use the reserved `example.invalid` domain, so the dataset cannot accidentally
send mail. The company and organisational labels follow the supplied examples;
office addresses are plausible development values.