from sqlalchemy import MetaData, Table, Column, BigInteger, String, Integer, Time, ForeignKey, TIMESTAMP, JSON, Identity

metadata = MetaData()

system_state = Table(
    "system_state", metadata,
    Column("key", String, primary_key=True),
    Column("value", String),
    Column("updated_at", TIMESTAMP),
)

faculties = Table(
    "faculties", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String),
    Column("abbr", String),
)

departments = Table(
    "departments", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String),
    Column("abbr", String),
    Column("url_id", String),
)

specialities = Table(
    "specialities", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String),
    Column("faculty_id", BigInteger, ForeignKey("faculties.id")),
)

student_groups = Table(
    "student_groups", metadata,
    Column("surrogate_id", Integer, Identity(), primary_key=True),
    Column("id", BigInteger),
    Column("name", String),
    Column("specialty_id", BigInteger, ForeignKey("specialities.id")),
    Column("valid_from", TIMESTAMP),
    Column("valid_to", TIMESTAMP),
)

employees = Table(
    "employees", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("first_name", String),
    Column("last_name", String),
    Column("middle_name", String),
    Column("url_id", String),
    Column("photo_link", String),
    Column("degree", String),
    Column("rank", String),
)

departments_employees = Table(
    "departments_employees", metadata,
    Column("department_id", BigInteger, ForeignKey("departments.id"), primary_key=True),
    Column("employee_id", BigInteger, ForeignKey("employees.id"), primary_key=True),
)

auditories = Table(
    "auditories", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String),
    Column("building_number", String),
    Column("capacity", Integer),
    Column("auditory_type", String),
)

occupancy_index = Table(
    "occupancy_index", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("auditory_id", BigInteger, ForeignKey("auditories.id")),
    Column("day_of_week", String),
    Column("week_number", Integer),
    Column("start_time", Time),
    Column("end_time", Time),
)

schedule_storage = Table(
    "schedule_json_storage", metadata,
    Column("id", Integer, Identity(), primary_key=True),    
    Column("group_id", BigInteger), 
    Column("employee_id", BigInteger),
    Column("data", JSON),
    Column("api_last_update_ts", TIMESTAMP),    
    Column("valid_from", TIMESTAMP),
    Column("valid_to", TIMESTAMP), 
)