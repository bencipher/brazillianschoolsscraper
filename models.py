from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ProgramEnum(Enum):
    mtech = "Master's"
    phd = 'PhD'


class CourseType(BaseModel):
    title: str
    level: ProgramEnum


class School(BaseModel):
    school: str
    courses: Optional[list[CourseType]]


class UserInput(BaseModel):
    cv: str
