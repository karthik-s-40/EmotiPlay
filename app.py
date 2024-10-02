import spotipy
from spotipy.oauth2 import SpotifyOAuth
from transformers import pipeline
from deepface import DeepFace
import cv2

# Initialize sentiment analysis
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

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
        'motivational': ['motivational', 'inspirational', 'empowering', 'encouraging','motivationn'],
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

    if mood == 'neutral':
        print("Detected mood is neutral. Please provide input.")
        user_input = input("How are you feeling today? ")
        mood = analyze_mood(user_input)

    print(f"Final detected mood: {mood}")

    # Fetch and display the first set of songs (page 1)
    offset = 0
    limit = 20
    while True:
        songs = get_songs_based_on_mood(mood, offset=offset, limit=limit)
        if not songs:
            print("No more songs found.")
            break
        
        # Display songs for the current page
        print(f"\nHere are some songs for your mood (Page {offset // limit + 1}):")
        for song in songs:
            print(song)

        # Ask if the user wants to manually enter the mood after showing the first set of songs
        if offset == 0:  # Only ask after the first page
            manual_input = input("\nDid I get it right? (yes/no): ").lower()
            if manual_input == 'no':
                mood = input("Please enter your mood: ").lower()

                # Fetch and display songs based on the manually entered mood
                offset = 0  # Reset offset to show new mood songs
                songs = get_songs_based_on_mood(mood, offset=offset, limit=limit)
                if not songs:
                    print("No songs found for the entered mood.")
                    break
                
                print(f"\nHere are some songs for your manually entered mood ({mood}):")
                for song in songs:
                    print(song)

        # Ask if user wants to see the next set of songs
        next_action = input("\nDo you want to see the next set of songs? (yes/no): ").lower()
        if next_action != 'yes':
            break

        # Increase offset for the next set of songs (next page)
        offset += limit
