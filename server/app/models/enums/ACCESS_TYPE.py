from enum import Enum

class UserAccessType(Enum):
    TRAVELLERS = "travellers"
    ADMINS = "administrators"
    MAINTAINERS = "developers"