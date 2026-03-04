from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.dialects.postgresql import insert
from app.api.deps import get_db, get_current_user
from app.models import User, Habit, HabitLog
from app.schemas import HabitCreate, HabitUpdate, HabitResponse, HabitListResponse, SuccessMessageResponse, HabitLogCreate, HabitLogToggleResponse, HabitLogResponse, HabitLogBulkUpdate

router = APIRouter()

from datetime import datetime
from typing import Optional
from sqlalchemy import extract

@router.post("/logs/bulk", response_model=SuccessMessageResponse)
def bulk_update_habit_logs(
    payload: HabitLogBulkUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not payload.logs:
        return SuccessMessageResponse(success=True, message="No logs to update")

    # Fetch all habit IDs the user owns to ensure they aren't updating someone else's habits
    user_habit_ids = {str(h_id[0]) for h_id in db.query(Habit.id).filter(Habit.user_id == current_user.id).all()}
    
    # Filter out any logs that don't belong to this user
    valid_logs = [log for log in payload.logs if str(log.habitId) in user_habit_ids]
    
    if not valid_logs:
        raise HTTPException(status_code=403, detail="Not authorized to update these habits")

    # Prepare values for bulk upsert
    values = [{"habit_id": log.habitId, "date": log.date, "isCompleted": log.isCompleted} for log in valid_logs]
    
    stmt = insert(HabitLog).values(values)
    stmt = stmt.on_conflict_do_update(
        constraint='uq_habit_id_date',
        set_={"isCompleted": stmt.excluded.isCompleted}
    )
    
    db.execute(stmt)
    db.commit()
    
    return SuccessMessageResponse(success=True, message=f"Successfully processed {len(valid_logs)} logs")

@router.get("", response_model=HabitListResponse)
def get_habits(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Default to current month and year if not provided
    now = datetime.now()
    filter_month = month if month is not None else now.month
    filter_year = year if year is not None else now.year

    habits = db.query(Habit).options(
        joinedload(Habit.logs.and_(
            extract('month', HabitLog.date) == filter_month,
            extract('year', HabitLog.date) == filter_year
        ))
    ).filter(Habit.user_id == current_user.id).all()
    
    return HabitListResponse(
        success=True,
        data=[HabitResponse.model_validate(h) for h in habits]
    )

@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(habit_in: HabitCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    habit = Habit(
        user_id=current_user.id,
        title=habit_in.title,
        priority=habit_in.priority,
        duration=habit_in.duration,
        frequency=habit_in.frequency,
        customStartDate=habit_in.customStartDate,
        customEndDate=habit_in.customEndDate
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    habit.logs = [] # Explicitly set empty logs for the response logic
    return HabitResponse.model_validate(habit)

@router.patch("/{id}", response_model=HabitResponse)
def update_habit(id: UUID, habit_in: HabitUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    habit = db.query(Habit).filter(Habit.id == id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    update_data = habit_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
        
    db.commit()
    db.refresh(habit)
    return HabitResponse.model_validate(habit)

@router.delete("/{id}", response_model=SuccessMessageResponse)
def delete_habit(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    habit = db.query(Habit).filter(Habit.id == id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    db.delete(habit)
    db.commit()
    return SuccessMessageResponse(success=True, message="Habit removed successfully")

@router.post("/{id}/logs", response_model=HabitLogToggleResponse)
def toggle_habit_log(id: UUID, log_in: HabitLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify the habit belongs to the user
    habit = db.query(Habit).filter(Habit.id == id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    # Postgres specific upsert using ON CONFLICT logic
    stmt = insert(HabitLog).values(
        habit_id=id,
        date=log_in.date,
        isCompleted=log_in.isCompleted
    )
    
    # On conflict, update the isCompleted status
    stmt = stmt.on_conflict_do_update(
        constraint='uq_habit_id_date',
        set_={"isCompleted": log_in.isCompleted}
    )
    
    # Execute upsert statement
    db.execute(stmt)
    db.commit()
    
    # Fetch the inserted/updated log
    log = db.query(HabitLog).filter(HabitLog.habit_id == id, HabitLog.date == log_in.date).first()
    
    return HabitLogToggleResponse(
        success=True,
        data=HabitLogResponse.model_validate(log)
    )
