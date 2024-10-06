from flask import Flask, render_template, jsonify, request
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from transformers import pipeline
from deepface import DeepFace
import cv2
import requests
from dotenv import load_dotenv
import os

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize sentiment analysis model
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# YouTube API Credentials
YOUTUBE_API_KEY = 'AIzaSyD8xIZDQ7qCAmmeb88GUWMQZfTNLakK98U'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# Load environment variables from .env file
load_dotenv()

# Get the Spotify credentials from environment variables
client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.environ.get('SPOTIFY_REDIRECT_URI')

# Initialize Spotipy with OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='user-library-read playlist-modify-public'
))
# Mood mapping for facial emotion detection
mood_map = {
    'happy': 'happy',
    'sad': 'depressed',
    'angry': 'angry',
    'surprise': 'happy',
    'neutral': 'neutral',
    'disgust': 'angry',
    'fear': 'horror'
}

# Mood keywords for text-based mood detection
mood_keywords = {
    'party': ['party', 'celebrate', 'dance', 'club', 'fun'],
        'angry': ['angry', 'mad', 'rage', 'furious', 'annoyed', 'aggressive', 'vicious'],
        'depressed': ['depressed', 'down', 'unhappy', 'hopeless', 'sad', 'mournful', 'somber', 'melancholic'],
        'indian': ['indian', 'bollywood', 'desi'],
        'classical': ['classical', 'orchestra', 'symphony', 'instrumental'],
        'indie': ['indie', 'alternative', 'folk', 'independent'],
        'pop': ['pop', 'popular', 'chart', 'mainstream'],
        'chill': ['chill', 'relax', 'calm', 'laid-back', 'easy', 'chilled', 'carefree', 'cool', 'laid back'],
        'romantic': ['love', 'romantic', 'romance', 'lustful'],
        'horror': ['horror', 'afraid', 'spooky', 'ghost', 'fear', 'scary', 'terrifying', 'terror'],
        'action': ['action', 'energetic', 'intense', 'dynamic', 'driving'],
        'adventurous': ['adventurous', 'daring', 'brave', 'bold'],
        'ambient': ['ambient', 'ethereal', 'atmospheric', 'airy'],
        'cinematic': ['cinematic', 'dramatic', 'epic'],
        'emotional': ['emotional', 'sentimental', 'heartfelt', 'touching'],
        'upbeat': ['upbeat', 'happy', 'positive', 'optimistic', 'cheerful', 'fun', 'sunny'],
        'nostalgic': ['nostalgia', 'nostalgic', 'yesteryear', 'vintage', 'retro', 'reflective'],
        'motivational': ['motivational', 'inspirational', 'empowering', 'encouraging', 'motivation'],
        'calm': ['calm', 'peaceful', 'serene', 'tranquil', 'meditative'],
        'danger': ['danger', 'dark', 'ominous', 'tense', 'suspenseful'],
        'futuristic': ['futuristic', 'tech', 'industrial', 'digital', 'glitchy'],
        'happy': ['happy', 'joyful', 'elated', 'euphoric', 'sunshine'],
        'gym': ['gym', 'workout', 'driven', 'hard', 'determined', 'relentless'],
        'rap': ['rap', 'hip-hop', 'beats', 'rhymes', 'trap', 'bars'],
        'hindi': ['hindi', 'bollywood', 'desi', 'filmi'],
        'tamil': ['tamil', 'kollywood', 'south indian', 'tamil cinema'],
        'telugu': ['telugu', 'tollywood', 'south indian'],
        'punjabi': ['punjabi', 'bhangra', 'punjab', 'punjabi beats'],
        'bengali': ['bengali', 'bangla', 'bengali folk'],
        'marathi': ['marathi', 'lavani', 'marathi folk'],
        'kannada': ['kannada', 'sandalwood', 'kannada songs'],
        'malayalam': ['malayalam', 'mollywood', 'malayalam songs'],
        'gujarati': ['gujarati', 'garba', 'gujarati folk'],
        'odia': ['odia', 'odia folk', 'odia songs'],
        'assamese': ['assamese', 'bihu', 'assamese folk'],
        'comedy': ['comedy', 'funny', 'humor', 'joke', 'laugh', 'hilarious'],
        'drama': ['drama', 'tragic', 'emotional', 'intense', 'theatrical'],
        'devotional': ['devotional', 'spiritual', 'worship', 'prayer', 'mantra', 'sacred'],
        'lofi':['lofi','lo-fi']
    # Add other mood keywords...
}

# Function to analyze mood based on text input
def analyze_mood(user_input):
    result = sentiment_analyzer(user_input)[0]
    sentiment = result['label']
    user_input_lower = user_input.lower()
    detected_moods = set()

    # Detect multiple moods based on keywords
    for mood, keywords in mood_keywords.items():
        if any(word in user_input_lower for word in keywords):
            detected_moods.add(mood)

    if len(detected_moods) > 0:
        return ' and '.join(detected_moods)

    # Default mood based on sentiment
    if sentiment == 'POSITIVE':
        return "happy"
    elif sentiment == 'NEGATIVE':
        return "sad"
    else:
        return "neutral"

# Function to detect facial expressions using DeepFace
def detect_facial_expression():
    cap = cv2.VideoCapture(0)  # Start video capture
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()

    if not ret:
        return None

    emotion_results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=True)
    return emotion_results[0]['dominant_emotion'] if emotion_results else None

# Route to analyze mood from facial expression
@app.route('/facial-mood', methods=['GET'])
def facial_mood():
    detected_emotion = detect_facial_expression()
    mood = mood_map.get(detected_emotion, 'neutral')
    return jsonify({'mood': mood})

# Route to analyze mood based on text input
@app.route('/text-mood', methods=['POST'])
def text_mood():
    data = request.json
    user_input = data.get('text', '')
    mood = analyze_mood(user_input)
    return jsonify({'mood': mood})

# Function to get songs based on mood from Spotify
def get_songs_based_on_mood(mood, offset=0, limit=10):
    results = sp.search(q=mood, type='track', limit=limit, offset=offset)
    songs = []
    for track in results['tracks']['items']:
        songs.append(f"{track['name']} by {track['artists'][0]['name']} (URL: {track['external_urls']['spotify']})")
    next_offset = offset + limit if len(results['tracks']['items']) == limit else None
    return songs, next_offset

# Route to get Spotify songs based on mood with pagination
@app.route('/spotify-songs', methods=['POST'])
def spotify_songs():
    data = request.json
    mood = data.get('mood', 'happy')
    offset = data.get('offset', 0)
    songs, next_offset = get_songs_based_on_mood(mood, offset)
    return jsonify({'songs': songs, 'next_offset': next_offset})

# Function to get YouTube videos based on mood
def get_youtube_videos(mood, max_results=5, page_token=None):
    params = {
        'part': 'snippet',
        'q': mood,
        'type': 'video',
        'maxResults': max_results,
        'key': YOUTUBE_API_KEY,
    }
    if page_token:
        params['pageToken'] = page_token

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    videos = response.json().get('items', [])
    next_page_token = response.json().get('nextPageToken', None)

    video_list = []
    for video in videos:
        video_title = video['snippet']['title']
        video_id = video['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_list.append(f"{video_title} (URL: {video_url})")
    
    return video_list, next_page_token

# Route to get YouTube videos based on mood with pagination
@app.route('/youtube-videos', methods=['POST'])
def youtube_videos():
    data = request.json
    mood = data.get('mood', 'happy')
    page_token = data.get('next_page_token', None)
    videos, next_page_token = get_youtube_videos(mood, page_token)
    return jsonify({'videos': videos, 'next_page_token': next_page_token})

# Route to render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5001)
