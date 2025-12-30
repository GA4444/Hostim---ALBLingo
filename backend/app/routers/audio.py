from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
import tempfile
import subprocess
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import uuid
import json

router = APIRouter()

# Create temp directory for audio files
TEMP_AUDIO_DIR = "temp_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)


@router.post("/text-to-speech")
async def text_to_speech(text: str, language: str = "sq"):
	"""
	Convert text to speech using Google Text-to-Speech
	Language codes: 'sq' for Albanian, 'en' for English
	"""
	try:
		# Create unique filename
		filename = f"tts_{uuid.uuid4()}.mp3"
		filepath = os.path.join(TEMP_AUDIO_DIR, filename)
		
		# Generate speech
		tts = gTTS(text=text, lang=language, slow=False)
		tts.save(filepath)
		
		# Return audio file
		return FileResponse(
			filepath, 
			media_type="audio/mpeg",
			filename=f"speech_{language}.mp3"
		)
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")


@router.post("/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...), language: str = "sq-AL"):
	"""
	Convert speech to text using Google Speech Recognition
	Language codes: 'sq-AL' for Albanian, 'en-US' for English
	"""
	try:
		# Save uploaded file temporarily
		temp_filename = f"stt_{uuid.uuid4()}.wav"
		temp_filepath = os.path.join(TEMP_AUDIO_DIR, temp_filename)
		
		with open(temp_filepath, "wb") as buffer:
			buffer.write(await audio_file.read())
		
		# Convert to proper format if needed
		audio = AudioSegment.from_file(temp_filepath)
		audio = audio.set_frame_rate(16000).set_channels(1)
		audio.export(temp_filepath, format="wav")
		
		# Initialize recognizer
		recognizer = sr.Recognizer()
		
		# Load audio file
		with sr.AudioFile(temp_filepath) as source:
			audio_data = recognizer.record(source)
		
		# Recognize speech
		text = recognizer.recognize_google(audio_data, language=language)
		
		# Clean up temp files
		os.remove(temp_filepath)
		
		return {
			"text": text,
			"confidence": 0.9,  # Google doesn't provide confidence for free tier
			"language": language
		}
		
	except sr.UnknownValueError:
		raise HTTPException(status_code=400, detail="Could not understand audio")
	except sr.RequestError as e:
		raise HTTPException(status_code=500, detail=f"Speech recognition service error: {str(e)}")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")
	finally:
		# Clean up temp files
		if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
			os.remove(temp_filepath)


@router.post("/pronunciation-check")
async def pronunciation_check(
	audio_file: UploadFile = File(...), 
	target_text: str = "",
	language: str = "sq-AL"
):
	"""
	Check pronunciation by comparing spoken text with target text
	"""
	try:
		# Convert speech to text
		recognized_text = await speech_to_text(audio_file, language)
		
		# Simple similarity check (can be enhanced with more sophisticated algorithms)
		similarity = calculate_similarity(recognized_text["text"], target_text)
		
		return {
			"spoken_text": recognized_text["text"],
			"target_text": target_text,
			"similarity_score": similarity,
			"is_correct": similarity > 0.7,
			"feedback": get_pronunciation_feedback(similarity, recognized_text["text"], target_text)
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Pronunciation check failed: {str(e)}")


def calculate_similarity(text1: str, text2: str) -> float:
	"""Calculate similarity between two texts"""
	if not text1 or not text2:
		return 0.0
	
	# Convert to lowercase and remove punctuation for comparison
	text1_clean = ''.join(c.lower() for c in text1 if c.isalnum() or c.isspace())
	text2_clean = ''.join(c.lower() for c in text2 if c.isalnum() or c.isspace())
	
	# Simple word-based similarity
	words1 = set(text1_clean.split())
	words2 = set(text2_clean.split())
	
	if not words1 or not words2:
		return 0.0
	
	intersection = words1.intersection(words2)
	union = words1.union(words2)
	
	return len(intersection) / len(union) if union else 0.0


def get_pronunciation_feedback(similarity: float, spoken: str, target: str) -> str:
	"""Generate feedback based on pronunciation accuracy"""
	if similarity > 0.9:
		return "Shumë mirë! Shqiptimi yt është i saktë."
	elif similarity > 0.7:
		return "Mirë! Mund të përmirësosh pak shqiptimin."
	elif similarity > 0.5:
		return "Provo sërish. Fokuso më shumë në shqiptimin e duhur."
	else:
		return "Duhet të praktikosh më shumë. Dëgjo përsëri fjalën dhe provo sërish."


@router.get("/audio-exercises/{exercise_id}")
async def get_audio_exercise(exercise_id: int, slow: bool = True):
	"""
	Get audio version of an exercise for listening practice
	Supports Albanian corpus exercises with proper pronunciation
	"""
	try:
		from ..database import get_db
		from .. import models
		
		# Get exercise from database
		db = next(get_db())
		exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
		
		if not exercise:
			raise HTTPException(status_code=404, detail="Exercise not found")
		
		# Extract text to be spoken
		exercise_text = ""
		if exercise.data:
			try:
				data = json.loads(exercise.data)
				if "audio_text" in data:
					exercise_text = data["audio_text"]
			except:
				pass
		
		# Fallback to answer if no audio_text specified
		if not exercise_text:
			exercise_text = exercise.answer
		
		# Generate speech with Albanian pronunciation
		filename = f"exercise_{exercise_id}_{uuid.uuid4()}.mp3"
		filepath = os.path.join(TEMP_AUDIO_DIR, filename)
		
		# Use slower speech for dictation exercises
		tts = gTTS(text=exercise_text, lang="sq", slow=slow)
		tts.save(filepath)
		
		return FileResponse(
			filepath,
			media_type="audio/mpeg",
			filename=f"exercise_{exercise_id}.mp3"
		)
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Audio exercise generation failed: {str(e)}")


@router.post("/albanian-pronunciation-check")
async def albanian_pronunciation_check(
	audio_file: UploadFile = File(...), 
	exercise_id: int = 0,
	target_text: str = ""
):
	"""
	Specialized pronunciation check for Albanian corpus exercises
	Includes Albanian-specific phonetic considerations
	"""
	try:
		from ..database import get_db
		from .. import models
		
		# Get target text from exercise if not provided
		if not target_text and exercise_id:
			db = next(get_db())
			exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
			if exercise:
				target_text = exercise.answer
		
		# Convert speech to text with Albanian language model
		recognized_text = await speech_to_text(audio_file, "sq-AL")
		
		# Enhanced similarity check for Albanian
		similarity = calculate_albanian_similarity(recognized_text["text"], target_text)
		
		# Determine score based on Albanian corpus rules
		is_correct = similarity > 0.8  # Higher threshold for Albanian
		score = get_albanian_score(similarity)
		
		return {
			"spoken_text": recognized_text["text"],
			"target_text": target_text,
			"similarity_score": similarity,
			"is_correct": is_correct,
			"score": score,
			"feedback": get_albanian_feedback(similarity, recognized_text["text"], target_text),
			"pronunciation_tips": get_albanian_pronunciation_tips(recognized_text["text"], target_text)
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Albanian pronunciation check failed: {str(e)}")


def calculate_albanian_similarity(text1: str, text2: str) -> float:
	"""Enhanced similarity calculation for Albanian language"""
	if not text1 or not text2:
		return 0.0
	
	# Albanian-specific character normalization
	albanian_chars = {
		'ë': 'e', 'ç': 'c', 'rr': 'r', 'll': 'l', 'nj': 'n', 'gj': 'g', 
		'dh': 'd', 'th': 't', 'sh': 's', 'zh': 'z', 'xh': 'x'
	}
	
	def normalize_albanian(text):
		text = text.lower().strip()
		for alb_char, replacement in albanian_chars.items():
			text = text.replace(alb_char, replacement)
		return ''.join(c for c in text if c.isalnum() or c.isspace())
	
	text1_norm = normalize_albanian(text1)
	text2_norm = normalize_albanian(text2)
	
	# Exact match gets perfect score
	if text1_norm == text2_norm:
		return 1.0
	
	# Character-level similarity for short words
	if len(text2_norm.split()) == 1:
		return character_similarity(text1_norm, text2_norm)
	
	# Word-level similarity for sentences
	words1 = set(text1_norm.split())
	words2 = set(text2_norm.split())
	
	if not words1 or not words2:
		return 0.0
	
	intersection = words1.intersection(words2)
	union = words1.union(words2)
	
	return len(intersection) / len(union) if union else 0.0


def character_similarity(text1: str, text2: str) -> float:
	"""Calculate character-level similarity"""
	if not text1 or not text2:
		return 0.0
	
	# Levenshtein distance approximation
	if len(text1) == len(text2):
		matches = sum(c1 == c2 for c1, c2 in zip(text1, text2))
		return matches / len(text1)
	
	# For different lengths, use a simple approach
	shorter, longer = (text1, text2) if len(text1) < len(text2) else (text2, text1)
	matches = sum(c in longer for c in shorter)
	return matches / len(longer)


def get_albanian_score(similarity: float) -> int:
	"""Convert similarity to Albanian corpus scoring system"""
	if similarity >= 0.95:
		return 3  # Perfect - 3 stars
	elif similarity >= 0.85:
		return 2  # Good - 2 stars  
	elif similarity >= 0.7:
		return 1  # Acceptable - 1 star
	else:
		return 0  # Needs improvement


def get_albanian_feedback(similarity: float, spoken: str, target: str) -> str:
	"""Albanian-specific pronunciation feedback"""
	if similarity >= 0.95:
		return "🌟 Përgëzime! Shqiptimi yt është i përsosur!"
	elif similarity >= 0.85:
		return "👍 Shumë mirë! Shqiptimi yt është pothuajse i saktë."
	elif similarity >= 0.7:
		return "📈 Mirë! Mund të përmirësosh pak më shumë shqiptimin."
	elif similarity >= 0.5:
		return "🔄 Provo sërish. Fokuso në secilën shkronjë."
	else:
		return "📚 Dëgjo me kujdes dhe provo përsëri. Merr kohën tënde."


def get_albanian_pronunciation_tips(spoken: str, target: str) -> list:
	"""Provide specific tips for Albanian pronunciation"""
	tips = []
	
	if not spoken or not target:
		return ["Dëgjo me kujdes fjalën dhe provo të flasësh qartë."]
	
	spoken_lower = spoken.lower()
	target_lower = target.lower()
	
	# Check for common Albanian pronunciation issues
	if 'ë' in target_lower and 'e' in spoken_lower:
		tips.append("💡 Kujdes me shkronjën 'ë' - shqiptohet si 'uh' në anglisht.")
	
	if 'rr' in target_lower and 'r' in spoken_lower:
		tips.append("💡 Shkronja 'rr' duhet të jetë më e fortë se 'r' e thjeshtë.")
	
	if 'ç' in target_lower and 'c' in spoken_lower:
		tips.append("💡 Shkronja 'ç' shqiptohet si 'ch' në anglisht.")
	
	if 'll' in target_lower and 'l' in spoken_lower:
		tips.append("💡 Shkronja 'll' ka një tingull të veçantë shqip.")
	
	if not tips:
		tips.append("🎯 Përqendrohu në shqiptimin e qartë të çdo shkronje.")
	
	return tips


@router.delete("/cleanup-audio")
async def cleanup_audio_files():
	"""Clean up temporary audio files"""
	try:
		for filename in os.listdir(TEMP_AUDIO_DIR):
			filepath = os.path.join(TEMP_AUDIO_DIR, filename)
			if os.path.isfile(filepath):
				os.remove(filepath)
		return {"message": "Audio files cleaned up successfully"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
