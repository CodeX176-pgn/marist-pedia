# These are the roles that users can have in Marist Pedia.
# Using an Enum prevents accidental spelling differences such as
# "Teacher", "teacher", and "TEACHER".

from enum import Enum


class UserRole(str, Enum):
    """Available user roles in Marist Pedia."""

    TEACHER = "teacher"
    STUDENT = "student"