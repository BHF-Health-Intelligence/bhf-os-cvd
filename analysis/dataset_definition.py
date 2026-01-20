from ehrql import codelist_from_csv, show
from ehrql.tables.core import patients, practice_registrations, clinical_events, medications

index_date = "2024-03-31"

diabetes_codes = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-dm_cod.csv", column="code")

show(clinical_events.where(clinical_events.snomedct_code.is_in(diabetes_codes)))