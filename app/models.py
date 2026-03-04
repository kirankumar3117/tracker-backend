from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, UniqueConstraint, ARRAY, Integer
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime, timezone

Base = declarative_base()

class PriorityEnum(str, enum.Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    auth_provider = Column(String, default="email")

    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")

class Habit(Base):
    __tablename__ = "habits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    priority = Column(Enum(PriorityEnum), nullable=False)
    duration = Column(String, nullable=False) # "1-week", "all-time", "custom"
    frequency = Column(ARRAY(Integer), nullable=False) # [0, 1, 2, ..., 6]
    customStartDate = Column(DateTime(timezone=True), nullable=True)
    customEndDate = Column(DateTime(timezone=True), nullable=True)
    createdAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    isCompleted = Column(Boolean, default=False, nullable=False)

    habit = relationship("Habit", back_populates="logs")

    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_id_date'),
    )
