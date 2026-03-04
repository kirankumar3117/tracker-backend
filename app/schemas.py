from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class PriorityEnum(str, Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirmPassword: str = Field(..., min_length=6)

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirmPassword:
            raise ValueError('Passwords do not match')
        return self

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    token: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: EmailStr

class AuthResponseData(BaseModel):
    user: UserResponse
    token: str

class AuthResponse(BaseModel):
    success: bool = True
    data: AuthResponseData

class HabitLogBase(BaseModel):
    date: datetime
    isCompleted: bool

class HabitLogCreate(HabitLogBase):
    pass

class HabitLogBulkItem(HabitLogBase):
    habitId: UUID

class HabitLogBulkUpdate(BaseModel):
    logs: List[HabitLogBulkItem]

class HabitLogResponse(HabitLogBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: UUID
    habitId: UUID = Field(alias="habit_id")

class HabitLogToggleResponse(BaseModel):
    success: bool = True
    data: HabitLogResponse

class HabitBase(BaseModel):
    title: str = Field(..., min_length=1)
    priority: PriorityEnum
    duration: str # "1-week", "all-time", "custom"
    frequency: List[int] # [0, 6] etc

    customStartDate: Optional[datetime] = None
    customEndDate: Optional[datetime] = None

class HabitCreate(HabitBase):
    @model_validator(mode='after')
    def validate_custom_dates(self):
        if self.duration == "custom":
            if not self.customStartDate or not self.customEndDate:
                raise ValueError('customStartDate and customEndDate are required when duration is "custom"')
        return self

class HabitUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    frequency: Optional[List[int]] = None
    customStartDate: Optional[datetime] = None
    customEndDate: Optional[datetime] = None
    duration: Optional[str] = None

class HabitResponse(HabitBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: UUID
    userId: UUID = Field(alias="user_id")
    createdAt: datetime
    logs: List[HabitLogResponse] = []

class HabitListResponse(BaseModel):
    success: bool = True
    data: List[HabitResponse]

class SuccessMessageResponse(BaseModel):
    success: bool = True
    message: str
