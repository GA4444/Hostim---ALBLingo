from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Enum, UniqueConstraint, DateTime, Float
from sqlalchemy.orm import relationship, backref
from .database import Base
import enum
from datetime import datetime


class CategoryEnum(str, enum.Enum):
	LISTEN_WRITE = "listen_write"  # Diktim (Audio → shkruaj)
	WORD_FROM_DESCRIPTION = "word_from_description"  # Fjala nga përshkrimi
	SYNONYMS_ANTONYMS = "synonyms_antonyms"  # Sinonime & Antonime
	ALBANIAN_OR_LOANWORD = "albanian_or_loanword"  # Shqipe apo Huazim?
	MISSING_LETTER = "missing_letter"  # Shkronja që mungon
	WRONG_LETTER = "wrong_letter"  # Shkronja e gabuar
	BUILD_WORD = "build_word"  # Ndërto fjalën
	NUMBER_TO_WORD = "number_to_word"  # Numri me fjalë
	PHRASES = "phrases"  # Shprehje (frazeologjike)
	SPELLING_PUNCTUATION = "spelling_punctuation"  # Drejtshkrim & Pikësim
	ABSTRACT_CONCRETE = "abstract_concrete"  # Abstrakte vs Konkrete
	BUILD_SENTENCE = "build_sentence"  # Ndërto fjalinë
	VOCABULARY = "vocabulary"  # Legacy category
	SPELLING = "spelling"  # Legacy category
	GRAMMAR = "grammar"  # Legacy category
	NUMBERS = "numbers"  # Legacy category
	PUNCTUATION = "punctuation"  # Legacy category


class Course(Base):
	__tablename__ = "courses"
	
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(100), nullable=False)
	description = Column(Text, nullable=True)
	order_index = Column(Integer, default=0, nullable=False)
	category = Column(Enum(CategoryEnum), index=True, nullable=False)
	required_score = Column(Integer, default=80, nullable=False)  # percentage to unlock
	enabled = Column(Boolean, default=True)
	parent_class_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # For class hierarchy
	
	# Relationships
	levels = relationship("Level", back_populates="course", order_by="Level.order_index")
	exercises = relationship("Exercise", back_populates="course")
	sub_courses = relationship("Course", backref=backref("parent_class", remote_side=[id]))  # Courses within a class


class Level(Base):
	__tablename__ = "levels"
	
	id = Column(Integer, primary_key=True, index=True)
	course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
	name = Column(String(100), nullable=False)
	description = Column(Text, nullable=True)
	order_index = Column(Integer, default=0, nullable=False)
	required_score = Column(Integer, default=80, nullable=False)  # percentage to unlock
	enabled = Column(Boolean, default=True)
	
	# Relationships
	course = relationship("Course", back_populates="levels")
	exercises = relationship("Exercise", back_populates="level")


class Exercise(Base):
	__tablename__ = "exercises"

	id = Column(Integer, primary_key=True, index=True)
	category = Column(Enum(CategoryEnum), index=True, nullable=False)
	course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
	level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
	prompt = Column(Text, nullable=False)
	# JSON-encoded string for choice lists or structured data when needed
	data = Column(Text, nullable=True)
	# expected answer text (or JSON-serialized for multi-answers)
	answer = Column(Text, nullable=False)
	points = Column(Integer, default=1, nullable=False)
	enabled = Column(Boolean, default=True)
	order_index = Column(Integer, default=0, nullable=False)

	# Rule-specific field (optional): e.g., pass threshold, max_errors
	rule = Column(String(50), nullable=True)

	# Relationships
	course = relationship("Course", back_populates="exercises")
	level = relationship("Level", back_populates="exercises")
	attempts = relationship("Attempt", back_populates="exercise")


class Attempt(Base):
	__tablename__ = "attempts"

	id = Column(Integer, primary_key=True, index=True)
	exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
	user_id = Column(String(64), index=True, nullable=False)
	response = Column(Text, nullable=False)
	is_correct = Column(Boolean, default=False)
	score_delta = Column(Integer, default=0)

	exercise = relationship("Exercise", back_populates="attempts")


class Progress(Base):
	__tablename__ = "progress"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(String(64), index=True, nullable=False)
	category = Column(Enum(CategoryEnum), index=True, nullable=False)
	course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
	level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
	# aggregate points and error counts
	points = Column(Integer, default=0)
	errors = Column(Integer, default=0)
	stars = Column(Integer, default=0)
	completed = Column(Boolean, default=False)
	
	# Relationships
	course = relationship("Course")
	level = relationship("Level")


class CourseProgress(Base):
	__tablename__ = "course_progress"
	
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
	total_exercises = Column(Integer, default=0)
	completed_exercises = Column(Integer, default=0)
	correct_answers = Column(Integer, default=0)
	total_points = Column(Integer, default=0)
	accuracy_percentage = Column(Float, default=0.0)
	is_completed = Column(Boolean, default=False)
	is_unlocked = Column(Boolean, default=False)
	completed_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
	
	# Relationships
	user = relationship("User")
	course = relationship("Course")
	
	# Unique constraint to prevent duplicate progress records
	__table_args__ = (UniqueConstraint('user_id', 'course_id', name='unique_user_course_progress'),)


class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String(50), unique=True, index=True, nullable=False)
	email = Column(String(100), unique=True, index=True, nullable=False)
	age = Column(Integer, nullable=True)
	# grade_level = Column(String(20), nullable=True)  # e.g., "Class 1", "Class 2" - REMOVED
	# learning_style = Column(String(50), nullable=True)  # e.g., "visual", "auditory", "kinesthetic" - REMOVED
	# preferred_difficulty = Column(String(20), default="normal")  # "easy", "normal", "hard" - REMOVED
	created_at = Column(DateTime, default=datetime.utcnow)
	last_login = Column(DateTime, nullable=True)
	is_active = Column(Boolean, default=True)
	is_admin = Column(Boolean, default=False, nullable=False)
	password_hash = Column(String(255), nullable=False)


