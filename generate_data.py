#!/usr/bin/env python3
"""Generate synthetic, decoded directory data for Keski-Suomen hyvinvointialue.

The generated CSV represents the post-processing stage: organisational numeric
codes are already decoded into readable hierarchy fields. No real employee
records or deliverable email addresses are included.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from random import Random
from typing import Sequence


COMPANY = "Keski-Suomen hyvinvointialue"
OFFICE_NAME = "KESKI-SUOMEN HYVINVOINTIALUE"
ORGANIZATION = "Hyvinvointialue, Keski-Suomi"
BUSINESS_AREA = "Konsernipalvelut"
STATE_OR_PROVINCE = "Keski-Suomi"
COUNTRY = "Suomi"
EMAIL_DOMAIN = "example.invalid"
DEFAULT_ROWS = 1_000
DEFAULT_SEED = 2026_0917
DEFAULT_OUTPUT = Path("data/keski_suomen_hyvinvointialue_users.csv")
SNAPSHOT_DATE = date(2026, 9, 17)


FIELDNAMES = [
    "City",
    "Company",
    "Department",
    "DisplayName",
    "EmailAddress",
    "EmployeeId",
    "EmployeeType",
    "EmployeeHireDate",
    "HierarchyLevel",
    "Organization",
    "BusinessArea",
    "ResponsibilityArea",
    "ServiceArea",
    "ServiceUnit",
    "WorkLocation",
    "EmployeeOrgData",
    "Office",
    "physicalDeliveryOfficeName",
    "PostalCode",
    "StreetAddress",
    "StateOrProvince",
    "CountryOrRegion",
    "Title",
    "BusinessPhone",
    "MobilePhone",
    "MailNickname",
    "Manager",
    "Sponsors",
    "OtherEmails",
    "ProxyAddresses",
    "FaxNumber",
    "IMAddresses",
    "PreferredLanguage",
    "AccountStatus",
    "DataOrigin",
]


@dataclass(frozen=True)
class Location:
    """A synthetic office location used for development data."""

    city: str
    postal_code: str
    street_address: str

    @property
    def display(self) -> str:
        return f"{self.street_address}, {self.postal_code} {self.city}"


@dataclass(frozen=True)
class OrgUnit:
    """Readable form of one organisational branch.

    The source screenshots show codes such as 113, 1133 and 11025. Those
    values are deliberately not written to the output; this catalog stores
    their decoded labels instead.
    """

    responsibility_area: str
    service_area: str
    service_unit: str
    locations: tuple[Location, ...]
    titles: tuple[str, ...]
    weight: int


@dataclass(frozen=True)
class HierarchySpec:
    """One management position in the six-level organisational tree."""

    key: str
    parent_key: str | None
    hierarchy_level: str
    business_area: str
    responsibility_area: str
    service_area: str
    service_unit: str
    location: Location
    title: str


JYVASKYLA_TECH = Location("Jyväskylä", "40620", "HOITAJANTIE 1")
JYVASKYLA_CENTRE = Location("Jyväskylä", "40100", "HYVINVOINTIKATU 12")
JAMSA = Location("Jämsä", "42100", "SAIRAALANTIE 8")
AANEKOSKI = Location("Äänekoski", "44100", "KESKUSKATU 14")
LAUKAA = Location("Laukaa", "41340", "TERVEYSTIE 5")
KEURUU = Location("Keuruu", "42700", "PALVELUTIE 3")
KARSTULA = Location("Karstula", "43500", "HYVINVOINTITIE 6")
VIITASAARI = Location("Viitasaari", "44500", "TERVEYSKESKUKSENTIE 2")


ORG_UNITS: tuple[OrgUnit, ...] = (
    OrgUnit(
        responsibility_area="Tietohallinto",
        service_area="Tietohallinto yhteiset",
        service_unit="Tietohallinto yhteiset",
        locations=(JYVASKYLA_TECH, JYVASKYLA_CENTRE),
        titles=(
            "Tietohallintojohtaja",
            "Hallinnon asiantuntija",
            "Tietohallinnon suunnittelija",
            "Johdon assistentti",
        ),
        weight=7,
    ),
    OrgUnit(
        responsibility_area="Tietohallinto",
        service_area="Tietohallintopalvelut",
        service_unit="Tietohallintopalvelut",
        locations=(JYVASKYLA_TECH, JAMSA, AANEKOSKI, LAUKAA),
        titles=(
            "Tietohallinnon asiantuntija",
            "Käyttäjätukiasiantuntija",
            "Palvelupäällikkö",
            "Järjestelmäasiantuntija",
            "Laitetukiasiantuntija",
        ),
        weight=16,
    ),
    OrgUnit(
        responsibility_area="Tietohallinto",
        service_area="Projektit ja kehittäminen",
        service_unit="Projektit ja kehittäminen",
        locations=(JYVASKYLA_TECH, JYVASKYLA_CENTRE),
        titles=(
            "Projektipäällikkö",
            "Kehittämispäällikkö",
            "Projektisuunnittelija",
            "Palvelumuotoilija",
            "Tuoteomistaja",
        ),
        weight=12,
    ),
    OrgUnit(
        responsibility_area="Tietohallinto",
        service_area="Teknologiapalvelut",
        service_unit="Teknologiapalvelut",
        locations=(JYVASKYLA_TECH, JYVASKYLA_CENTRE, JAMSA, AANEKOSKI),
        titles=(
            "Teknologiapäällikkö",
            "Teknologia-asiantuntija",
            "Järjestelmäasiantuntija",
            "Verkkoasiantuntija",
            "Tietoturva-asiantuntija",
            "Palveluarkkitehti",
            "Konesaliasiantuntija",
        ),
        weight=22,
    ),
    OrgUnit(
        responsibility_area="Tietohallinto",
        service_area="Palveluprosessien digitalisaatio",
        service_unit="Palveluprosessien digitalisaatio",
        locations=(JYVASKYLA_TECH, JYVASKYLA_CENTRE, LAUKAA),
        titles=(
            "Digitalisaatiopäällikkö",
            "Digitalisaatioasiantuntija",
            "Prosessikehittäjä",
            "Integraatioasiantuntija",
            "Tietoasiantuntija",
        ),
        weight=12,
    ),
    OrgUnit(
        responsibility_area="Viestintäpalvelut",
        service_area="Viestintäpalvelut",
        service_unit="Viestintäpalvelut",
        locations=(JYVASKYLA_TECH, JYVASKYLA_CENTRE, JAMSA),
        titles=(
            "Viestintäpäällikkö",
            "Viestintäasiantuntija",
            "Graafinen suunnittelija",
            "Sisällöntuottaja",
            "Verkkoviestinnän asiantuntija",
        ),
        weight=10,
    ),
    OrgUnit(
        responsibility_area="Tilapalvelut",
        service_area="Tilapalveluiden johtaminen",
        service_unit="Tilapalveluiden johtaminen",
        locations=(JYVASKYLA_CENTRE, JAMSA, AANEKOSKI, KEURUU, KARSTULA, VIITASAARI),
        titles=(
            "Tilapalvelupäällikkö",
            "Toimitilapäällikkö",
            "Rakennuttajapäällikkö",
            "Kiinteistöasiantuntija",
            "Huoltoinsinööri",
        ),
        weight=9,
    ),
)


FIRST_NAMES = (
    "Aino",
    "Anni",
    "Anu",
    "Eeva",
    "Elina",
    "Emilia",
    "Heli",
    "Henna",
    "Johanna",
    "Kaisa",
    "Katri",
    "Laura",
    "Leena",
    "Liisa",
    "Marika",
    "Meri",
    "Minna",
    "Nina",
    "Outi",
    "Paula",
    "Riikka",
    "Saara",
    "Sanna",
    "Sari",
    "Satu",
    "Tiina",
    "Tuula",
    "Veera",
    "Viivi",
    "Jaana",
    "Antti",
    "Janne",
    "Jere",
    "Juha",
    "Jukka",
    "Kimmo",
    "Lauri",
    "Matti",
    "Mika",
    "Mikael",
    "Olli",
    "Pekka",
    "Riku",
    "Sami",
    "Sampo",
    "Sakari",
    "Teemu",
    "Timo",
    "Tomi",
    "Tuomas",
    "Ville",
    "Vesa",
    "Kalle",
    "Eemeli",
    "Joonas",
    "Markus",
    "Heikki",
)

LAST_NAMES = (
    "Aaltonen",
    "Ahonen",
    "Heikkilä",
    "Hämäläinen",
    "Jokinen",
    "Järvinen",
    "Kallio",
    "Karjalainen",
    "Koskinen",
    "Laakso",
    "Lahtinen",
    "Lehtinen",
    "Mäkelä",
    "Mäkinen",
    "Niemi",
    "Nieminen",
    "Ojala",
    "Peltonen",
    "Pitkänen",
    "Rantanen",
    "Räsänen",
    "Salminen",
    "Salo",
    "Saarinen",
    "Savolainen",
    "Seppälä",
    "Sillanpää",
    "Sipilä",
    "Suomalainen",
    "Toivonen",
    "Tuominen",
    "Vainio",
    "Virtanen",
    "Vuorinen",
    "Ylitalo",
    "Koskela",
    "Lindholm",
    "Mattila",
    "Miettinen",
    "Moilanen",
    "Nykänen",
    "Paananen",
    "Repo",
    "Rinne",
    "Roiha",
    "Takala",
    "Uusitalo",
    "Väisänen",
    "Kinnunen",
    "Manninen",
    "Hakala",
    "Hirvonen",
    "Kolehmainen",
    "Leppänen",
    "Nurminen",
    "Rautio",
    "Salonen",
    "Törmänen",
)


def positive_int(value: str) -> int:
    """Parse a positive command-line integer."""

    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def slugify(value: str) -> str:
    """Create an ASCII-safe local-part for a synthetic email address."""

    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", ".", ascii_value).strip(".")


def weighted_choice(rng: Random, values: Sequence[tuple[str, int]]) -> str:
    choices, weights = zip(*values)
    return rng.choices(choices, weights=weights, k=1)[0]


def hire_date(rng: Random) -> str:
    start = date(1998, 1, 1)
    days = (SNAPSHOT_DATE - start).days
    return (start + timedelta(days=rng.randrange(days))).isoformat()


def phone_numbers(index: int, rng: Random) -> tuple[str, str]:
    """Return Finnish-looking but non-routable development numbers."""

    business = f"+35814{2_000_000 + index:07d}"
    mobile_prefix = rng.choice(("40", "44", "45", "50"))
    mobile = f"+358{mobile_prefix}{100_000 + index:06d}"
    return business, mobile


def make_email(first_name: str, last_name: str, used: dict[str, int]) -> tuple[str, str]:
    base = slugify(f"{first_name}.{last_name}")
    occurrence = used.get(base, 0) + 1
    used[base] = occurrence
    local_part = base if occurrence == 1 else f"{base}{occurrence}"
    return f"{local_part}@{EMAIL_DOMAIN}", local_part


HIERARCHY_LEVELS = (
    "Hyvinvointialue",
    "Toimiala",
    "Vastuualue",
    "Palvelualue",
    "Palveluyksikkö",
    "Toimipiste",
)

RESPONSIBILITY_MANAGER_TITLES = {
    "Tietohallinto": "Tietohallintojohtaja",
    "Viestintäpalvelut": "Viestintäjohtaja",
    "Tilapalvelut": "Tilapalvelujohtaja",
}

SERVICE_MANAGER_TITLES = {
    "Tietohallinto yhteiset": "Tietohallinnon palvelupäällikkö",
    "Tietohallintopalvelut": "Tietohallintopalveluiden päällikkö",
    "Projektit ja kehittäminen": "Kehittämispäällikkö",
    "Teknologiapalvelut": "Teknologiapäällikkö",
    "Palveluprosessien digitalisaatio": "Digitalisaatiopäällikkö",
    "Viestintäpalvelut": "Viestintäpäällikkö",
    "Tilapalveluiden johtaminen": "Tilapalvelupäällikkö",
}


def build_manager_specs() -> tuple[HierarchySpec, ...]:
    """Build manager positions from the six readable hierarchy levels."""

    specs: list[HierarchySpec] = [
        HierarchySpec(
            key="organization",
            parent_key=None,
            hierarchy_level="Hyvinvointialue",
            business_area="Koko hyvinvointialue",
            responsibility_area="Hyvinvointialueen johto",
            service_area="Hyvinvointialueen johto",
            service_unit="Hyvinvointialueen johto",
            location=JYVASKYLA_CENTRE,
            title="Hyvinvointialuejohtaja",
        ),
        HierarchySpec(
            key="business:konsernipalvelut",
            parent_key="organization",
            hierarchy_level="Toimiala",
            business_area=BUSINESS_AREA,
            responsibility_area="Konsernipalvelut",
            service_area="Konsernipalveluiden johto",
            service_unit="Konsernipalveluiden johto",
            location=JYVASKYLA_CENTRE,
            title="Konsernipalvelujohtaja",
        ),
    ]

    responsibility_keys: dict[str, str] = {}
    for unit in ORG_UNITS:
        responsibility = unit.responsibility_area
        if responsibility in responsibility_keys:
            continue
        key = f"responsibility:{slugify(responsibility)}"
        responsibility_keys[responsibility] = key
        specs.append(
            HierarchySpec(
                key=key,
                parent_key="business:konsernipalvelut",
                hierarchy_level="Vastuualue",
                business_area=BUSINESS_AREA,
                responsibility_area=responsibility,
                service_area=f"{responsibility} johtaminen",
                service_unit=f"{responsibility} johtaminen",
                location=unit.locations[0],
                title=RESPONSIBILITY_MANAGER_TITLES[responsibility],
            )
        )

    for unit in ORG_UNITS:
        specs.append(
            HierarchySpec(
                key=f"service:{slugify(unit.service_area)}",
                parent_key=responsibility_keys[unit.responsibility_area],
                hierarchy_level="Palvelualue",
                business_area=BUSINESS_AREA,
                responsibility_area=unit.responsibility_area,
                service_area=unit.service_area,
                service_unit=unit.service_unit,
                location=unit.locations[0],
                title=SERVICE_MANAGER_TITLES[unit.service_area],
            )
        )

    for unit in ORG_UNITS:
        service_key = f"service:{slugify(unit.service_area)}"
        for location in unit.locations:
            location_key = slugify(location.display)
            specs.append(
                HierarchySpec(
                    key=f"unit:{slugify(unit.service_area)}:{location_key}",
                    parent_key=service_key,
                    hierarchy_level="Palveluyksikkö",
                    business_area=BUSINESS_AREA,
                    responsibility_area=unit.responsibility_area,
                    service_area=unit.service_area,
                    service_unit=unit.service_unit,
                    location=location,
                    title="Palveluyksikköpäällikkö",
                )
            )

    return tuple(specs)


def make_record(
    index: int,
    rng: Random,
    used_emails: dict[str, int],
    *,
    hierarchy_level: str,
    business_area: str,
    responsibility_area: str,
    service_area: str,
    service_unit: str,
    location: Location,
    title: str,
    manager_id: str | None,
) -> dict[str, str]:
    first_name = rng.choice(FIRST_NAMES)
    last_name = rng.choice(LAST_NAMES)
    display_name = f"{last_name} {first_name}"
    email, mail_nickname = make_email(first_name, last_name, used_emails)
    business_phone, mobile_phone = phone_numbers(index, rng)
    work_location = location.display
    employee_org_data = (
        f"Toimiala={business_area}; "
        f"Vastuualue={responsibility_area}; "
        f"Palvelualue={service_area}; "
        f"Palveluyksikkö={service_unit}; "
        f"Toimipiste={work_location}"
    )

    return {
        "City": location.city,
        "Company": COMPANY,
        "Department": service_area,
        "DisplayName": display_name,
        "EmailAddress": email,
        "EmployeeId": f"SYN-HYVAKS-{index:06d}",
        "EmployeeType": weighted_choice(
            rng,
            (
                ("Vakituinen", 78),
                ("Määräaikainen", 12),
                ("Osa-aikainen", 6),
                ("Sijainen", 4),
            ),
        ),
        "EmployeeHireDate": hire_date(rng),
        "HierarchyLevel": hierarchy_level,
        "Organization": ORGANIZATION,
        "BusinessArea": business_area,
        "ResponsibilityArea": responsibility_area,
        "ServiceArea": service_area,
        "ServiceUnit": service_unit,
        "WorkLocation": work_location,
        "EmployeeOrgData": employee_org_data,
        "Office": OFFICE_NAME,
        "physicalDeliveryOfficeName": OFFICE_NAME,
        "PostalCode": location.postal_code,
        "StreetAddress": location.street_address,
        "StateOrProvince": STATE_OR_PROVINCE,
        "CountryOrRegion": COUNTRY,
        "Title": title,
        "BusinessPhone": business_phone,
        "MobilePhone": mobile_phone,
        "MailNickname": mail_nickname,
        "Manager": manager_id or "",
        "Sponsors": "",
        "OtherEmails": "",
        "ProxyAddresses": f"SMTP:{email}",
        "FaxNumber": "",
        "IMAddresses": "",
        "PreferredLanguage": weighted_choice(
            rng, (("fi-FI", 94), ("sv-FI", 2), ("en-US", 4))
        ),
        "AccountStatus": weighted_choice(
            rng, (("Aktiivinen", 96), ("Poistuva", 2), ("Passiivinen", 2))
        ),
        "DataOrigin": "synthetic-development-data",
    }


def staff_titles(unit: OrgUnit) -> tuple[str, ...]:
    """Exclude leadership titles when creating level-six staff records."""

    candidates = tuple(
        title
        for title in unit.titles
        if "johtaja" not in title.lower() and "päällikkö" not in title.lower()
    )
    return candidates or unit.titles


def generate_records(row_count: int, seed: int) -> list[dict[str, str]]:
    rng = Random(seed)
    used_emails: dict[str, int] = {}
    records: list[dict[str, str]] = []
    manager_ids: dict[str, str] = {}
    manager_specs = build_manager_specs()

    # Create management positions from the top down so every Manager value can
    # point to an already-created EmployeeId.
    for spec in manager_specs[:row_count]:
        manager_id = manager_ids.get(spec.parent_key) if spec.parent_key else None
        if spec.parent_key and manager_id is None:
            raise ValueError(f"missing parent manager for {spec.key}")
        record = make_record(
            len(records) + 1,
            rng,
            used_emails,
            hierarchy_level=spec.hierarchy_level,
            business_area=spec.business_area,
            responsibility_area=spec.responsibility_area,
            service_area=spec.service_area,
            service_unit=spec.service_unit,
            location=spec.location,
            title=spec.title,
            manager_id=manager_id,
        )
        records.append(record)
        manager_ids[spec.key] = record["EmployeeId"]

    if len(records) == row_count:
        return records

    available_offices: list[tuple[OrgUnit, Location, str]] = []
    for unit in ORG_UNITS:
        service_key = f"service:{slugify(unit.service_area)}"
        for location in unit.locations:
            unit_key = f"unit:{slugify(unit.service_area)}:{slugify(location.display)}"
            if service_key in manager_ids and unit_key in manager_ids:
                available_offices.append((unit, location, manager_ids[unit_key]))

    if not available_offices:
        raise ValueError("no level-five managers are available for staff records")

    office_weights = [unit.weight for unit, _, _ in available_offices]
    while len(records) < row_count:
        unit, location, manager_id = rng.choices(
            available_offices, weights=office_weights, k=1
        )[0]
        records.append(
            make_record(
                len(records) + 1,
                rng,
                used_emails,
                hierarchy_level="Toimipiste",
                business_area=BUSINESS_AREA,
                responsibility_area=unit.responsibility_area,
                service_area=unit.service_area,
                service_unit=unit.service_unit,
                location=location,
                title=rng.choice(staff_titles(unit)),
                manager_id=manager_id,
            )
        )

    return records


def validate_records(records: Sequence[dict[str, str]]) -> None:
    """Fail early if the generated development data is malformed."""

    if not records:
        raise ValueError("at least one record is required")

    required = {
        "City",
        "Company",
        "Department",
        "DisplayName",
        "EmailAddress",
        "EmployeeId",
        "HierarchyLevel",
        "Organization",
        "ResponsibilityArea",
        "ServiceArea",
        "ServiceUnit",
        "WorkLocation",
        "Title",
    }
    emails = [record["EmailAddress"] for record in records]
    if len(emails) != len(set(emails)):
        raise ValueError("generated email addresses are not unique")

    employee_ids = {record["EmployeeId"] for record in records}
    levels = {level: index for index, level in enumerate(HIERARCHY_LEVELS, start=1)}
    record_by_id = {record["EmployeeId"]: record for record in records}

    for record in records:
        missing = [field for field in required if not record.get(field)]
        if missing:
            raise ValueError(f"record is missing required values: {', '.join(missing)}")
        if record["Company"] != COMPANY:
            raise ValueError("record has an unexpected company")
        if not record["EmailAddress"].endswith(f"@{EMAIL_DOMAIN}"):
            raise ValueError("record contains a non-synthetic email domain")
        if any(field.startswith("extensionAttribute") for field in record):
            raise ValueError("raw numeric extension attributes must not be exported")
        if record["HierarchyLevel"] not in levels:
            raise ValueError(f"unknown hierarchy level: {record['HierarchyLevel']}")

        manager_id = record["Manager"]
        if record["HierarchyLevel"] == HIERARCHY_LEVELS[0]:
            if manager_id:
                raise ValueError("the top-level manager must not have a manager")
        else:
            if not manager_id:
                raise ValueError(
                    f"non-top-level record has no manager: {record['EmployeeId']}"
                )
            if manager_id not in employee_ids:
                raise ValueError(f"unknown manager EmployeeId: {manager_id}")
            manager_level = levels[record_by_id[manager_id]["HierarchyLevel"]]
            if manager_level >= levels[record["HierarchyLevel"]]:
                raise ValueError(
                    f"manager must be higher in the hierarchy: {record['EmployeeId']}"
                )

    if len(records) > len(build_manager_specs()):
        missing_levels = set(HIERARCHY_LEVELS) - {
            record["HierarchyLevel"] for record in records
        }
        if missing_levels:
            raise ValueError(f"six-level hierarchy is incomplete: {sorted(missing_levels)}")


def write_csv(records: Sequence[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=FIELDNAMES,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rows",
        type=positive_int,
        default=DEFAULT_ROWS,
        help=f"number of rows to generate (default: {DEFAULT_ROWS})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"random seed for reproducible output (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = generate_records(args.rows, args.seed)
    validate_records(records)
    write_csv(records, args.output)
    print(f"Generated {len(records):,} synthetic rows in {args.output}")


if __name__ == "__main__":
    main()