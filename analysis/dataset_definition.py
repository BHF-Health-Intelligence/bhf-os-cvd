from ehrql import codelist_from_csv, create_dataset, show
from ehrql.tables.core import patients
from ehrql.tables.tpp import emergency_care_attendances, addresses


#For reference on emergency_care (ECDS):
#https://docs.opensafely.org/ehrql/reference/schemas/tpp/#emergency_care_attendances


# Instantiation
dataset = create_dataset()

dataset.configure_dummy_data(population_size=1000)

#CVD codes of-interest
cvd_codes = codelist_from_csv("codelists/cvd-ae-cod.csv", column="code")

#Known sex:
is_female_or_male = patients.sex.is_in(["female", "male"])

#Restrict events to those within date range
date_start="2017-04-01"
date_end = "2025-05-01"

#Ages 
age_at_start = patients.age_on(date_start)
age_filter = (age_at_start >= 0) & (age_at_start <= 110)

#Has diagnosis in codelist:
# codelist_filter=emergency_care_attendances.diagnosis_01.is_in(cvd_codes)


dataset.cvd_admission = emergency_care_attendances.where(
    emergency_care_attendances.diagnosis_01.is_in(cvd_codes)
).where(
    emergency_care_attendances.arrival_date .is_on_or_between(date_start, date_end)
).exists_for_patient()



#Implement filters
dataset.define_population(age_filter & 
                          is_female_or_male )

#Define columns
dataset.age = age_at_start
# dataset.code = codelist_filter
# dataset.imd = addresses.for_patient_on(date_start).imd_rounded
# dataset.ethnicity=emergency_care_attendances.ethnicity_from_sus