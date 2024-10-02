import spotipy
from spotipy.oauth2 import SpotifyOAuth
from transformers import pipeline
from deepface import DeepFace
import cv2
import requests

# Initialize sentiment analysis
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Replace with your actual YouTube API key
YOUTUBE_API_KEY = 'AIzaSyD8xIZDQ7qCAmmeb88GUWMQZfTNLakK98U'  # Update with your actual YouTube API key
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# Analyze mood based on text input
def analyze_mood(user_input):
    result = sentiment_analyzer(user_input)[0]
    sentiment = result['label']

    # Keywords for specific moods
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
    }

    user_input_lower = user_input.lower()
    detected_moods = set()

    # Detect multiple moods based on keywords
    for mood, keywords in mood_keywords.items():
        if any(word in user_input_lower for word in keywords):
            detected_moods.add(mood)

    # If multiple moods are detected, return a combined result
    if len(detected_moods) > 0:
        return ' and '.join(detected_moods)

    # Default mood based on sentiment
    if sentiment == 'POSITIVE':
        return "happy"
    elif sentiment == 'NEGATIVE':
        return "sad"
    else:
        return "neutral"

# Facial emotion recognition function
def detect_facial_expression():
    cap = cv2.VideoCapture(0)  # Start video capture
    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    print("Camera is ready. Please look at the camera for a moment...")

    # Continuously capture frames until a key is pressed
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Display the captured frame
        cv2.imshow('Facial Emotion Recognition', frame)

        # Check if the frame is valid
        if frame is None or frame.size == 0:
            print("Captured an empty frame.")
            break

        # Analyze the emotion from the current frame
        try:
            emotion_results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=True)
            if emotion_results:
                dominant_emotion = emotion_results[0]['dominant_emotion']
                print(f"Detected emotion: {dominant_emotion}")
            else:
                print("No emotion detected.")
                dominant_emotion = None
                
        except Exception as e:
            print(f"Error detecting emotion: {e}")
            dominant_emotion = None
        
        # Break the loop after detecting the emotion once
        break

    cap.release()  # Release the video capture
    cv2.destroyAllWindows()  # Close any OpenCV windows

    return dominant_emotion  # Return the dominant emotion detected

# Set up Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='961ca27d80624c26a92f1661add6802a',
                                               client_secret='903a5b11cdab448fa59aec251f8c4a8a',
                                               redirect_uri='http://localhost:8888/callback',
                                               scope='user-library-read playlist-modify-public'))

# Get songs based on mood with pagination
def get_songs_based_on_mood(mood, offset=0, limit=20):
    results = sp.search(q=mood, type='track', limit=limit, offset=offset)
    songs = []
    for track in results['tracks']['items']:
        songs.append(f"{track['name']} by {track['artists'][0]['name']} (URL: {track['external_urls']['spotify']})")
    return songs

# Function to get YouTube videos based on mood with pagination
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

if __name__ == "__main__":
    print("Using facial expression to detect mood...")
    detected_emotion = detect_facial_expression()

    # Map detected emotion to mood
    mood_map = {
        'happy': 'happy',
        'sad': 'depressed',
        'angry': 'angry',
        'surprise': 'happy',  # Assuming surprise could be linked to happy
        'neutral': 'neutral',
        'disgust': 'angry',
        'romantic': 'romantic',
        'fear': 'horror'
    }

    mood = mood_map.get(detected_emotion, 'neutral')  # Default to neutral if not found
    print(f"Mapped mood: {mood}")

    # Confirm mood
    confirm_mood = input("Is the detected mood correct? (yes/no): ").strip().lower()
    if confirm_mood == 'no':
        user_input = input("Please enter your mood description: ")
        mood = analyze_mood(user_input)
        print(f"Confirmed mood: {mood}")

    # Choose between songs and videos
    choice = input("Do you want to see songs, videos, or both? (songs/videos/both): ").strip().lower()
    
    if choice in ['songs', 'both']:
        song_offset = 0
        song_limit = 20

        while True:
            songs = get_songs_based_on_mood(mood, offset=song_offset, limit=song_limit)
            print("\nRecommended Songs:")
            for song in songs:
                print(song)

            # Check if more songs are available
            if len(songs) < song_limit:
                print("\nNo more songs available.")
                break

            # Ask for pagination input
            next_action = input("\nDo you want to see the next page of songs? (yes/no): ").strip().lower()
            if next_action == 'yes':
                song_offset += song_limit
            else:
                break

    if choice in ['videos', 'both']:
        youtube_next_page_token = None
        youtube_max_results = 5

        while True:
            youtube_videos, youtube_next_page_token = get_youtube_videos(mood, max_results=youtube_max_results, page_token=youtube_next_page_token)
            print("\nRecommended YouTube Videos:")
            for video in youtube_videos:
                print(video)

            # Check if more videos are available
            if not youtube_next_page_token:
                print("\nNo more videos available.")
                break

            # Ask for pagination input
            next_action = input("\nDo you want to see the next page of YouTube videos? (yes/no): ").strip().lower()
            if next_action == 'yes':
                continue  # Next page will automatically load due to the loop
            else:
                break
