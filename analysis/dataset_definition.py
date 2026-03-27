from ehrql import case, codelist_from_csv, create_dataset, show
from ehrql.tables.core import patients
from ehrql.tables.tpp import emergency_care_attendances, addresses, practice_registrations, when, ethnicity_from_sus


#For reference on emergency_care (ECDS):
#https://docs.opensafely.org/ehrql/reference/schemas/tpp/#emergency_care_attendances



# Define study dates 
study_date_start="2017-04-01"
study_date_end = "2025-05-01"


# Instantiation
dataset = create_dataset()
#Set pop size for dummy data
dataset.configure_dummy_data(population_size=1000)

#### Codelists ####

#CVD codes of-interest
cvd_codes = codelist_from_csv("codelists/cvd-ae-cod.csv", column="code")

#### Dataset definitions ####

# Known sex
is_female_or_male = patients.sex.is_in(["female", "male"])

# Ages 
age_at_start = patients.age_on(study_date_start)
age_filter = (age_at_start >= 0) & (age_at_start <= 110)

# Has primary diagnosis in codelist:
codelist_filter=emergency_care_attendances.diagnosis_01.is_in(cvd_codes)

# Has an IMD score 
has_deprivation_index = addresses.for_patient_on(
    study_date_start
).imd_rounded.is_not_null()

# Has a region
has_region = practice_registrations.for_patient_on(
    study_date_start
).practice_nuts1_region_name.is_not_null()

# Has an ethnicity 
ethnicity = ethnicity_from_sus.code.is_not_null()

#Arrival date in the study
#arrival_dates=emergency_care_attendances.arrival_date
#dates_within_study = (arrival_dates >= study_date_start) & (arrival_dates <= study_date_end)


first_attendance=emergency_care_attendances.where(
    emergency_care_attendances.arrival_date.is_on_or_between(study_date_start, study_date_end)
).sort_by(emergency_care_attendances.arrival_date).first_for_patient()


has_diagnosis=first_attendance.diagnosis_01.is_not_null()



# Bin deprivation into quintiles
imd_rounded = addresses.for_patient_on(study_date_start).imd_rounded
max_imd = 32844
imd_quintile = case(
    when((imd_rounded >= 0) & (imd_rounded <= int(max_imd * 1 / 5))).then(1),
    when(imd_rounded <= int(max_imd * 2 / 5)).then(2),
    when(imd_rounded <= int(max_imd * 3 / 5)).then(3),
    when(imd_rounded <= int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
    otherwise=99,
)


# Implement filters
dataset.define_population(age_filter & 
                          is_female_or_male & 
                          has_deprivation_index & 
                          has_region & 
                          ethnicity)


#TODO: implement codelist_filter and arrival_dates and diagnosis code 


# Define columns
dataset.age = age_at_start
dataset.imd = addresses.for_patient_on(study_date_start).imd_rounded
dataset.imd_quintile=imd_quintile
dataset.ethnicity=ethnicity_from_sus.code
# dataset.arrival_date=first_attendance.arrival_date
dataset.primary_diag = first_attendance.diagnosis_01
# dataset.arrival_date=arrival_dates
# dataset.diagnosis = emergency_care_attendances.diagnosis_01