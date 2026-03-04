from sqlalchemy.orm import Session
from uuid import UUID
from app.models import Habit
from app.schemas import PriorityEnum
import logging

logger = logging.getLogger(__name__)

def _seed_default_habits(db: Session, user_id: UUID):
    """
    Seeds a default set of habits for a newly registered user.
    """
    default_habits_data = [
        {
            "title": "DSA / Problem Solving",
            "priority": PriorityEnum.High,
            "duration": "all-time",
            "frequency": [1, 2, 3, 4, 5]  # Weekdays
        },
        {
            "title": "Running / Exercise",
            "priority": PriorityEnum.Medium,
            "duration": "all-time",
            "frequency": [0, 2, 4, 6]  # Alternating days
        },
        {
            "title": "Read a Book",
            "priority": PriorityEnum.Low,
            "duration": "all-time",
            "frequency": [0, 1, 2, 3, 4, 5, 6]  # Every day
        }
    ]

    try:
        habits_to_insert = []
        for habit_data in default_habits_data:
            habit = Habit(
                user_id=user_id,
                title=habit_data["title"],
                priority=habit_data["priority"],
                duration=habit_data["duration"],
                frequency=habit_data["frequency"],
            )
            habits_to_insert.append(habit)
        
        db.add_all(habits_to_insert)
        db.commit()
    except Exception as e:
        # We catch the exception to prevent the entire registration flow from failing 
        # just because habit seeding failed. We rollback this specific transaction instead.
        db.rollback()
        logger.error(f"Failed to seed default habits for user {user_id}: {str(e)}")
