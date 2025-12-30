from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas


router = APIRouter()


@router.get("/ai/recommendations/{user_id}")
def get_ai_recommendations(user_id: str, db: Session = Depends(get_db)):
	"""Get AI-powered exercise recommendations based on user performance"""
	
	# Get user's performance data
	user_attempts = (
		db.query(models.Attempt)
		.filter(models.Attempt.user_id == user_id)
		.all()
	)
	
	if not user_attempts:
		# New user - recommend first course
		first_course = (
			db.query(models.Course)
			.filter(models.Course.order_index == 1)
			.first()
		)
		return {
			"recommendation_type": "new_user",
			"message": "Mirësevini! Fillo me kursin e parë për të mësuar bazat.",
			"recommended_course": first_course.id if first_course else None,
			"difficulty": "beginner"
		}
	
	# Analyze performance patterns
	correct_attempts = [a for a in user_attempts if a.is_correct]
	incorrect_attempts = [a for a in user_attempts if not a.is_correct]
	
	accuracy = len(correct_attempts) / len(user_attempts) if user_attempts else 0
	
	# Get user's current progress
	user_progress = (
		db.query(models.Progress)
		.filter(models.Progress.user_id == user_id)
		.all()
	)
	
	# Find areas for improvement
	weak_categories = []
	for progress in user_progress:
		if progress.errors > progress.points:
			weak_categories.append(progress.category)
	
	# AI recommendation logic
	if accuracy < 0.6:
		recommendation_type = "review_weak_areas"
		message = "Duhet të përmirësosh disa fusha. Fokusohu në ushtrimet e gabuara."
		difficulty = "easier"
	elif accuracy > 0.9:
		recommendation_type = "challenge_yourself"
		message = "Je duke bërë shumë mirë! Provo nivele më të vështira."
		difficulty = "harder"
	else:
		recommendation_type = "steady_progress"
		message = "Po eci mirë! Vazhdo me ritmin tënd."
		difficulty = "current"
	
	# Find next recommended exercise
	recommended_exercise = None
	if weak_categories:
		# Recommend exercise from weak category
		exercise = (
			db.query(models.Exercise)
			.filter(models.Exercise.category.in_(weak_categories))
			.filter(models.Exercise.enabled == True)
			.first()
		)
		if exercise:
			recommended_exercise = exercise.id
	
	return {
		"recommendation_type": recommendation_type,
		"message": message,
		"accuracy": accuracy,
		"weak_categories": [cat.value for cat in weak_categories],
		"difficulty": difficulty,
		"recommended_exercise": recommended_exercise,
		"total_attempts": len(user_attempts),
		"correct_attempts": len(correct_attempts)
	}


@router.get("/ai/adaptive-difficulty/{user_id}")
def get_adaptive_difficulty(user_id: str, db: Session = Depends(get_db)):
	"""Get adaptive difficulty settings based on user performance"""
	
	# Get recent performance (last 20 attempts)
	recent_attempts = (
		db.query(models.Attempt)
		.filter(models.Attempt.user_id == user_id)
		.order_by(models.Attempt.id.desc())
		.limit(20)
		.all()
	)
	
	if not recent_attempts:
		return {"difficulty": "normal", "multiplier": 1.0}
	
	recent_accuracy = sum(1 for a in recent_attempts if a.is_correct) / len(recent_attempts)
	
	# Adaptive difficulty logic
	if recent_accuracy < 0.4:
		difficulty = "easier"
		multiplier = 0.8  # Reduce difficulty
		message = "Duke u përmirësuar! Po e bëj më të lehtë për ty."
	elif recent_accuracy > 0.8:
		difficulty = "harder"
		multiplier = 1.2  # Increase difficulty
		message = "Je duke bërë shumë mirë! Po e bëj më të vështirë."
	else:
		difficulty = "normal"
		multiplier = 1.0
		message = "Ritmi i duhur! Vazhdo kështu."
	
	return {
		"difficulty": difficulty,
		"multiplier": multiplier,
		"message": message,
		"recent_accuracy": recent_accuracy,
		"attempts_analyzed": len(recent_attempts)
	}


@router.get("/ai/learning-path/{user_id}")
def get_learning_path(user_id: str, db: Session = Depends(get_db)):
	"""Get personalized learning path based on user's learning style and performance"""
	
	# Analyze learning patterns
	user_attempts = (
		db.query(models.Attempt)
		.filter(models.Attempt.user_id == user_id)
		.all()
	)
	
	if not user_attempts:
		return {"path": "standard", "message": "Fillo me rrugën standarde të mësimit."}
	
	# Analyze category preferences
	category_performance = {}
	for attempt in user_attempts:
		exercise = db.get(models.Exercise, attempt.exercise_id)
		if exercise:
			cat = exercise.category.value
			if cat not in category_performance:
				category_performance[cat] = {"correct": 0, "total": 0}
			category_performance[cat]["total"] += 1
			if attempt.is_correct:
				category_performance[cat]["correct"] += 1
	
	# Find strengths and weaknesses
	strengths = []
	weaknesses = []
	
	for cat, perf in category_performance.items():
		accuracy = perf["correct"] / perf["total"]
		if accuracy > 0.8:
			strengths.append(cat)
		elif accuracy < 0.5:
			weaknesses.append(cat)
	
	# Determine learning path
	if len(strengths) > len(weaknesses):
		path = "accelerated"
		message = "Je duke ecur shpejt! Mund të kalosh në nivele më të avancuara."
	elif len(weaknesses) > len(strengths):
		path = "foundational"
		message = "Fokusohu në bazat për të ndërtuar një themel të fortë."
	else:
		path = "balanced"
		message = "Ritmi i balancuar! Vazhdo me të gjitha kategoritë."
	
	return {
		"path": path,
		"message": message,
		"strengths": strengths,
		"weaknesses": weaknesses,
		"category_performance": category_performance
	}


@router.get("/ai/smart-hints/{exercise_id}/{user_id}")
def get_smart_hints(exercise_id: int, user_id: str, db: Session = Depends(get_db)):
	"""Get smart hints based on user's previous mistakes and learning patterns"""
	
	exercise = db.get(models.Exercise, exercise_id)
	if not exercise:
		raise HTTPException(status_code=404, detail="Exercise not found")
	
	# Get user's previous attempts on similar exercises
	similar_exercises = (
		db.query(models.Exercise)
		.filter(models.Exercise.category == exercise.category)
		.filter(models.Exercise.id != exercise_id)
		.all()
	)
	
	similar_exercise_ids = [ex.id for ex in similar_exercises]
	
	user_attempts_on_similar = (
		db.query(models.Attempt)
		.filter(models.Attempt.user_id == user_id)
		.filter(models.Attempt.exercise_id.in_(similar_exercise_ids))
		.all()
	)
	
	# Analyze common mistakes
	common_mistakes = []
	if user_attempts_on_similar:
		incorrect_attempts = [a for a in user_attempts_on_similar if not a.is_correct]
		if incorrect_attempts:
			# Find patterns in mistakes
			common_mistakes = [
				"Kontrollo drejtshkrimin e fjalëve të gjata",
				"Kujdes me përdorimin e ë/e",
				"Vërejtje me bashkëtingëlloret e dyfishta"
			]
	
	# Generate contextual hints
	contextual_hints = []
	if exercise.category == models.CategoryEnum.SPELLING:
		contextual_hints.append("Kujdes me shkronjat që mungojnë")
	elif exercise.category == models.CategoryEnum.GRAMMAR:
		contextual_hints.append("Kontrollo trajtën e shkurtrave")
	elif exercise.category == models.CategoryEnum.VOCABULARY:
		contextual_hints.append("Mendoni për kuptimin e fjalës")
	
	return {
		"exercise_id": exercise_id,
		"category": exercise.category.value,
		"common_mistakes": common_mistakes,
		"contextual_hints": contextual_hints,
		"similar_exercises_attempted": len(user_attempts_on_similar),
		"accuracy_on_similar": sum(1 for a in user_attempts_on_similar if a.is_correct) / len(user_attempts_on_similar) if user_attempts_on_similar else 0
	}


@router.get("/ai/progress-insights/{user_id}")
def get_progress_insights(user_id: str, db: Session = Depends(get_db)):
	"""Get AI-generated insights about user's learning progress"""
	
	# Get comprehensive user data
	user_progress = (
		db.query(models.Progress)
		.filter(models.Progress.user_id == user_id)
		.all()
	)
	
	user_attempts = (
		db.query(models.Attempt)
		.filter(models.Attempt.user_id == user_id)
		.all()
	)
	
	if not user_attempts:
		return {"insights": ["Je duke filluar udhëtimin tënd!"]}
	
	# Calculate insights
	insights = []
	
	total_attempts = len(user_attempts)
	correct_attempts = sum(1 for a in user_attempts if a.is_correct)
	overall_accuracy = correct_attempts / total_attempts
	
	# Learning streak analysis
	recent_attempts = user_attempts[-10:] if len(user_attempts) >= 10 else user_attempts
	recent_accuracy = sum(1 for a in recent_attempts if a.is_correct) / len(recent_attempts)
	
	if recent_accuracy > overall_accuracy:
		insights.append("Je duke përmirësuar! Performanca jote e fundit është më e mirë se mesatarja.")
	elif recent_accuracy < overall_accuracy:
		insights.append("Mund të kesh nevojë për të rishikuar disa koncepte bazë.")
	
	# Category insights
	category_performance = {}
	for attempt in user_attempts:
		exercise = db.get(models.Exercise, attempt.exercise_id)
		if exercise:
			cat = exercise.category.value
			if cat not in category_performance:
				category_performance[cat] = {"correct": 0, "total": 0}
			category_performance[cat]["total"] += 1
			if attempt.is_correct:
				category_performance[cat]["correct"] += 1
	
	best_category = None
	worst_category = None
	best_accuracy = 0
	worst_accuracy = 1
	
	for cat, perf in category_performance.items():
		accuracy = perf["correct"] / perf["total"]
		if accuracy > best_accuracy:
			best_accuracy = accuracy
			best_category = cat
		if accuracy < worst_accuracy:
			worst_accuracy = accuracy
			worst_category = cat
	
	if best_category and best_accuracy > 0.8:
		insights.append(f"Je shumë i fortë në {best_category}! Mund të ndihmosh të tjerët.")
	
	if worst_category and worst_accuracy < 0.6:
		insights.append(f"Fokusohu më shumë në {worst_category} për të përmirësuar rezultatet.")
	
	# Time-based insights
	if total_attempts > 50:
		insights.append("Ke bërë shumë progres! Vazhdo kështu.")
	elif total_attempts > 20:
		insights.append("Je duke ndërtuar një themel të fortë. Vazhdo me ushtrimet.")
	else:
		insights.append("Çdo ushtrim të afron më afër qëllimit. Vazhdo!")
	
	return {
		"insights": insights,
		"overall_accuracy": overall_accuracy,
		"total_attempts": total_attempts,
		"best_category": best_category,
		"worst_category": worst_category,
		"learning_streak": "positive" if recent_accuracy > overall_accuracy else "needs_improvement"
	}
