from datetime import date
from pathlib import Path
from ehrql import INTERVAL, case, codelist_from_csv, create_measures, months, when
from ehrql.tables.core import patients
from ehrql.tables.tpp import addresses, emergency_care_attendances, ethnicity_from_sus


def _load_config(path: Path) -> dict[str, str]:
    """Load the flat key:value settings used by analysis/config.yaml."""
    config: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip().strip('"').strip("'")
    return config

#Load config settings
config = _load_config(Path(__file__).with_name("config.yaml"))
study_date_start = date.fromisoformat(config["study_date_start"])
study_date_end = date.fromisoformat(config["study_date_end"])

#Calculate monthly intervals between study dates
total_months = (
    (study_date_end.year - study_date_start.year) * 12
    + (study_date_end.month - study_date_start.month)
)
monthly_intervals = months(total_months).starting_on(study_date_start)


#Initialize measures
measures = create_measures()
measures.configure_dummy_data(population_size=int(config["dummy_population_size"]))


#Read codelist
cvd_codes = codelist_from_csv(config["codelist_path"], column="code")

#Get data for this interval and codelist
attendances_in_interval = emergency_care_attendances.where(
    emergency_care_attendances.arrival_date.is_during(INTERVAL)
)
cvd_attendances_in_interval = attendances_in_interval.where(
    attendances_in_interval.diagnosis_01.is_in(cvd_codes)
)

#Define columns and filters
age_at_start = patients.age_on(INTERVAL.start_date)
is_female_or_male = patients.sex.is_in(["female", "male"])
age_filter = (age_at_start >= 0) & (age_at_start <= 110)
age_group = case(
    when((age_at_start >= 0) & (age_at_start <= 4)).then("0-4"),
    when((age_at_start >= 5) & (age_at_start <= 11)).then("5-11"),
    when((age_at_start >= 12) & (age_at_start <= 17)).then("12-17"),
    when((age_at_start >= 18) & (age_at_start <= 25)).then("18-25"),
    when((age_at_start >= 26) & (age_at_start <= 34)).then("26-34"),
    when((age_at_start >= 35) & (age_at_start <= 49)).then("35-49"),
    when((age_at_start >= 50) & (age_at_start <= 69)).then("50-69"),
    when((age_at_start >= 70) & (age_at_start <= 79)).then("70-79"),
    when((age_at_start >= 80) & (age_at_start <= 89)).then("80-89"),
    when(age_at_start >= 90).then("90+"),
    otherwise="Unknown",
)

#Count attendances and convert to flag 
has_cvd_attendance = cvd_attendances_in_interval.exists_for_patient()
attendance_count = cvd_attendances_in_interval.count_for_patient()
# attendance_flag = attendance_count > 0

#Get IMDs
imd_rounded = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
max_imd = 32844
imd_quintile = case(
    when((imd_rounded >= 0) & (imd_rounded <= int(max_imd * 1 / 5))).then(1),
    when(imd_rounded <= int(max_imd * 2 / 5)).then(2),
    when(imd_rounded <= int(max_imd * 3 / 5)).then(3),
    when(imd_rounded <= int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
    otherwise=99,
)

ethnicity_group = ethnicity_from_sus.code.map_values(
    {
        "A": "White",
        "B": "White",
        "C": "White",
        "D": "Mixed",
        "E": "Mixed",
        "F": "Mixed",
        "G": "Mixed",
        "H": "Asian",
        "J": "Asian",
        "K": "Asian",
        "L": "Asian",
        "M": "Black",
        "N": "Black",
        "P": "Black",
        "R": "Other",
        "S": "Other",
        "Z": "Not stated",
    },
    default="Unknown",
)



# Denominator: total CVD attendance events for patients satisfying age and sex filters
# Using an integer series causes ehrQL to sum counts across patients (total events)
total_attendances = case(
    when(age_filter & is_female_or_male).then(attendance_count),
    otherwise=0,
)

#Or - slicker? 
# total_attendances = attendance_count * (age_filter & is_female_or_male).as_int()


# Numerator: unique patients (not events) with a CVD attendance, satisfying the same filters
# Boolean series causes ehrQL to count patients where True
unique_attenders = has_cvd_attendance & age_filter & is_female_or_male

measures.define_defaults(
    denominator=total_attendances,
    numerator=unique_attenders,
    intervals=monthly_intervals,
)

measures.define_measure(
    name="cvd_attendances_monthly_ages",
    group_by={"age_group": age_group},
)

measures.define_measure(
    name="cvd_attendances_monthly_imd",
    group_by={"imd_quintile": imd_quintile},
)

measures.define_measure(
    name="cvd_attendances_monthly_ethnicity",
    group_by={"ethnicity_group": ethnicity_group},
)