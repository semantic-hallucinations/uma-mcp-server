from sqlalchemy import (
    MetaData, Table, Column, BigInteger, String, Integer, 
    Time, Date, ForeignKey, TIMESTAMP, Identity, Text
)
from sqlalchemy.dialects.postgresql import ARRAY, JSON, TSVECTOR, JSONB


metadata = MetaData()


employees = Table(
    "employees", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("first_name", String),
    Column("last_name", String),
    Column("middle_name", String),
    Column("degree", String),
    Column("rank", String),
    Column("photo_link", String),
    Column("calendar_id", String),
    Column("url_id", String, unique=True, nullable=False),
)


faculties = Table(
    "faculties", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String, unique=True, nullable=False),
    Column("abbr", String, unique=True, nullable=False),
)


departments = Table(
    "departments", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String, unique=True, nullable=False),
    Column("abbr", String, unique=True, nullable=False),
    Column("url_id", String, unique=True, nullable=False),
)


departments_employees = Table(
    "departments_employees", metadata,
    Column("department_id", BigInteger, ForeignKey("departments.id"), primary_key=True),
    Column("employee_id", BigInteger, ForeignKey("employees.id"), primary_key=True),
)


system_state = Table(
    "system_state", metadata,
    Column("key", String, primary_key=True),
    Column("value", String, nullable=False),
    Column("updated_at", TIMESTAMP),
)


specialities = Table(
    "specialities", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String, nullable=False),
    Column("abbr", String, nullable=False),
    Column("code", String, nullable=False),
    Column("education_form", String, nullable=False),
    Column("faculty_id", BigInteger, ForeignKey("faculties.id"), nullable=False),
)


student_groups = Table(
    "student_groups", metadata,
    Column("surrogate_id", Integer, Identity(), primary_key=True),
    Column("id", BigInteger, nullable=False),
    Column("name", String, nullable=False),
    Column("course", Integer),
    Column("calendar_id", String),
    Column("education_degree", Integer, nullable=False),
    Column("number_of_students", Integer),
    Column("specialty_id", BigInteger, ForeignKey("specialities.id"), nullable=False),
    Column("valid_from", TIMESTAMP, nullable=False),
    Column("valid_to", TIMESTAMP),
)


auditories = Table(
    "auditories", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String, nullable=False),
    Column("building_number", String),
    Column("note", String),
    Column("capacity", Integer),
    Column("auditory_type", String),
    Column("department_id", BigInteger, ForeignKey("departments.id")),
)


occupancy_index = Table(
    "occupancy_index", metadata,
    Column("id", BigInteger, Identity(), primary_key=True),
    Column("day_of_week", String, nullable=False),
    Column("week_number", Integer, nullable=False),
    Column("start_time", Time, nullable=False),
    Column("end_time", Time, nullable=False),
    Column("auditory_id", BigInteger, ForeignKey("auditories.id"), nullable=False),
    Column("groups", ARRAY(Text), nullable=False), 
)


schedule_storage = Table(
    "schedule_json_storage", metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("group_name", String), 
    Column("employee_id", BigInteger, ForeignKey("employees.id")),
    Column("entity_type", String, nullable=False),
    Column("data", JSON, nullable=False),
    Column("api_last_update_ts", TIMESTAMP),
    Column("valid_from", TIMESTAMP, nullable=False),
    Column("valid_to", TIMESTAMP),
)


schedule_events = Table(
    "schedule_events", metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("entity_name", String, nullable=False), 
    Column("entity_type", String, nullable=False),
    Column("subject", String, nullable=False),
    Column("subject_full", String),
    Column("auditories", ARRAY(Text), nullable=False),
    Column("day_of_week", Integer), 
    Column("start_time", Time, nullable=False),
    Column("end_time", Time, nullable=False),
    Column("week_numbers", ARRAY(Integer), nullable=False),
    Column("exact_date", Date),
    Column("related_groups", JSONB),
    Column("related_employees", JSONB),
    Column("subgroup", Integer),
    Column("search_vector", TSVECTOR), 
)