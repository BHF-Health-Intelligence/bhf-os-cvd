from ehrql import codelist_from_csv, create_dataset, show
from ehrql.tables.core import patients, practice_registrations, clinical_events, medications
from ehrql.tables.tpp import emergency_care_attendances

# Instantiation
dataset = create_dataset()


dataset.configure_dummy_data(population_size=1000)

#CVD codes of-interest
cvd_codes = codelist_from_csv("codelists/cvd-ae-cod.csv", column="code")

#Diabetes codes - for testing
#cvd_codes = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-dm_cod.csv", column="code")

#Known sex:
was_female_or_male = patients.sex.is_in(["female", "male"])

#Restrict events to those within date range
date_start="2017-04-01"
date_end = "2025-05-01"

#Ages 
age_at_start = patients.age_on(date_start)
age_filter = (age_at_start >= 0) & (age_at_start <= 110)


show(emergency_care_attendances.where(emergency_care_attendances.diagnosis_01.is_in(cvd_codes)))

dataset.define_population(age_filter)