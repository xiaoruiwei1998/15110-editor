ROLE_MAP = {
    "AM": "admin",
    "IS": "instructor",
    "RS": "researcher",
    "ST": "student"
}

COURSE_ROLE_MAP = {
    "AM": "admins",
    "IS": "instructors",
    "RS": "researchers",
    "ST": "students"
}

COURSE_ROLE_MAP_REVERSE = {
    "admins": "AM",
    "instructors": "IS",
    "researchers": "RS",
    "students": "ST"
}

SURVEY_TYPE_ENUM = ["Pre", "Post"]
QUESTION_TYPE_ENUM = ["SCALE", "MULTIPLE_CHOICE"]

ROLE_MAP_ENUM = [role for role in ROLE_MAP.keys()]
USER_SELECTION_TYPE = [ "user_id", "utorid" ]