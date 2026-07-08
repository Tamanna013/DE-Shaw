from enum import Enum

class Role(str, Enum):
    ADMIN = "Admin"
    ENGINEERING_MANAGER = "Engineering Manager"
    PLATFORM_ENGINEER = "Platform Engineer"
    SDET = "SDET"
    DEVELOPER = "Developer"
    READ_ONLY = "Read-Only"
