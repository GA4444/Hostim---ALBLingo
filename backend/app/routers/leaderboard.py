from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from ..database import get_db
from .. import models
from pydantic import BaseModel

router = APIRouter()

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    total_points: int
    total_correct: int
    total_attempts: int
    accuracy: float
    completed_courses: int
    level: int

    class Config:
        from_attributes = True

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db), limit: int = 50):
    """Get leaderboard with top users ranked by total points"""
    
    # Get all users with their statistics
    users = db.query(models.User).all()
    leaderboard_data = []
    
    for user in users:
        # Calculate total points from attempts
        total_points_result = db.query(func.sum(models.Attempt.score_delta)).filter(
            and_(
                models.Attempt.user_id == str(user.id),
                models.Attempt.score_delta > 0
            )
        ).scalar()
        total_points = int(total_points_result) if total_points_result else 0
        
        # Calculate total attempts and correct answers
        total_attempts = db.query(func.count(models.Attempt.id)).filter(
            models.Attempt.user_id == str(user.id)
        ).scalar() or 0
        
        total_correct = db.query(func.count(models.Attempt.id)).filter(
            and_(
                models.Attempt.user_id == str(user.id),
                models.Attempt.is_correct == True
            )
        ).scalar() or 0
        
        # Calculate accuracy
        accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
        
        # Count completed courses
        completed_courses = db.query(func.count(models.CourseProgress.id)).filter(
            and_(
                models.CourseProgress.user_id == user.id,
                models.CourseProgress.is_completed == True
            )
        ).scalar() or 0
        
        # Calculate level based on points (similar to frontend logic)
        level = (total_points // 100) + 1
        
        leaderboard_data.append({
            'user_id': user.id,
            'username': user.username,
            'total_points': total_points,
            'total_correct': total_correct,
            'total_attempts': total_attempts,
            'accuracy': round(accuracy, 1),
            'completed_courses': completed_courses,
            'level': level
        })
    
    # Sort by total points (descending), then by accuracy, then by completed courses
    leaderboard_data.sort(
        key=lambda x: (x['total_points'], x['accuracy'], x['completed_courses']),
        reverse=True
    )
    
    # Add rank and limit results
    result = []
    for idx, entry in enumerate(leaderboard_data[:limit], start=1):
        result.append(LeaderboardEntry(
            rank=idx,
            user_id=entry['user_id'],
            username=entry['username'],
            total_points=entry['total_points'],
            total_correct=entry['total_correct'],
            total_attempts=entry['total_attempts'],
            accuracy=entry['accuracy'],
            completed_courses=entry['completed_courses'],
            level=entry['level']
        ))
    
    return result

@router.get("/leaderboard/{user_id}/rank")
def get_user_rank(user_id: int, db: Session = Depends(get_db)):
    """Get current user's rank in the leaderboard"""
    leaderboard = get_leaderboard(db=db, limit=1000)
    
    for entry in leaderboard:
        if entry.user_id == user_id:
            return {
                "rank": entry.rank,
                "total_users": len(leaderboard),
                "percentile": round((1 - (entry.rank - 1) / len(leaderboard)) * 100, 1) if leaderboard else 0
            }
    
    return {
        "rank": len(leaderboard) + 1,
        "total_users": len(leaderboard),
        "percentile": 0
    }

