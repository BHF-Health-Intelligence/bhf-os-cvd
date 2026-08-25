from datetime import date
from pathlib import Path
from ehrql import INTERVAL, case, codelist_from_csv, create_measures, months, when
from ehrql.tables.core import patients
from ehrql.tables.tpp import (
    addresses,
    emergency_care_attendances,
    ethnicity_from_sus,
    practice_registrations,
)


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
was_registered = (
    practice_registrations.exists_for_patient_on(INTERVAL.start_date)
    & practice_registrations.where(
        practice_registrations.practice_systmone_go_live_date <= INTERVAL.start_date
    ).exists_for_patient()
)
was_alive = patients.is_alive_on(INTERVAL.start_date)
age_filter = (age_at_start >= 0) & (age_at_start <= 110) & was_registered
age_group = case(
    #Age bands - to fit with European standard population
    when((age_at_start >= 0) & (age_at_start <= 4)).then("0-4"),
    when((age_at_start >= 5) & (age_at_start <= 9)).then("5-9"),
    when((age_at_start >= 10) & (age_at_start <= 14)).then("10-14"),
    when((age_at_start >= 15) & (age_at_start <= 19)).then("15-19"),
    when((age_at_start >= 20) & (age_at_start <= 24)).then("20-24"),
    when((age_at_start >= 25) & (age_at_start <= 29)).then("25-29"),
    when((age_at_start >= 30) & (age_at_start <= 34)).then("30-34"),
    when((age_at_start >= 35) & (age_at_start <= 39)).then("35-39"),
    when((age_at_start >= 40) & (age_at_start <= 44)).then("40-44"),
    when((age_at_start >= 45) & (age_at_start <= 49)).then("45-49"),
    when((age_at_start >= 50) & (age_at_start <= 54)).then("50-54"),
    when((age_at_start >= 55) & (age_at_start <= 59)).then("55-59"),
    when((age_at_start >= 60) & (age_at_start <= 64)).then("60-64"),
    when((age_at_start >= 65) & (age_at_start <= 69)).then("65-69"),
    when((age_at_start >= 70) & (age_at_start <= 74)).then("70-74"),
    when((age_at_start >= 75) & (age_at_start <= 79)).then("75-79"),
    when((age_at_start >= 80) & (age_at_start <= 84)).then("80-84"),
    when((age_at_start >= 85) & (age_at_start <= 89)).then("85-89"),
    when((age_at_start >= 85) & (age_at_start <= 89)).then("85-89"),
    when((age_at_start >= 90) & (age_at_start <= 94)).then("90-94"),
    when(age_at_start >= 95).then("95+"),
    otherwise="Unknown",
)

sex=patients.sex

#Count attendances and convert to flag 
has_cvd_attendance = cvd_attendances_in_interval.exists_for_patient()
attendance_count = cvd_attendances_in_interval.count_for_patient()
# attendance_flag = attendance_count > 0

#Get IMDs - imd_rounded is rounded to the nearest 100, ranging 0 to IMD_MAX
IMD_MAX = 32800
imd_rounded = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
imd_decile = (imd_rounded * 10 // (IMD_MAX + 1)) + 1
imd_quintile = case(
    when(imd_rounded.is_not_null()).then(imd_decile),
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


filters=age_filter & is_female_or_male & was_alive & was_registered


# Denominator: total CVD attendance events for patients satisfying age and sex filters
# Using an integer series causes ehrQL to sum counts across patients (total events)
total_attendances = case(
    when(filters).then(attendance_count),
    otherwise=0,
)

#Or - slicker? 
# total_attendances = attendance_count * (age_filter & is_female_or_male).as_int()


# Numerator: unique patients (not events) with a CVD attendance, satisfying the same filters
# Boolean series causes ehrQL to count patients where True
unique_attenders = has_cvd_attendance & filters

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
    name="cvd_attendances_monthly_sex",
    group_by={"sex": sex},
)

measures.define_measure(
    name="cvd_attendances_monthly_imd",
    group_by={"imd_quintile": imd_quintile},
)

measures.define_measure(
    name="cvd_attendances_monthly_ethnicity",
    group_by={"ethnicity_group": ethnicity_group},
)




#Add in the sex as a variable in the measures, so we can stratify by that too.

#We can add the practice code too so we can see the distribution of attendances by practice


