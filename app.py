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
    party_keywords = ['party', 'celebrate', 'dance', 'club', 'fun']
    angry_keywords = ['angry', 'mad', 'rage', 'furious', 'annoyed']
    depressed_keywords = ['depressed', 'down', 'unhappy', 'hopeless', 'sad']
    indian_keywords = ['indian', 'bollywood', 'desi']
    classical_keywords = ['classical', 'orchestra', 'symphony', 'instrumental']
    indie_keywords = ['indie', 'alternative', 'folk', 'independent']
    pop_keywords = ['pop', 'popular', 'chart', 'mainstream']
    chill_keywords = ['chill', 'relax', 'calm', 'laid-back', 'easy']
    romantic_keywords = ['love', 'romantic', 'romance']
    horror_keywords=['afraid','spooky','ghost','fear']

    user_input_lower = user_input.lower()

    # Detect mood based on keywords
    if any(word in user_input_lower for word in party_keywords):
        return "party"
    elif any(word in user_input_lower for word in angry_keywords):
        return "angry"
    elif any(word in user_input_lower for word in depressed_keywords):
        return "depressed"
    elif any(word in user_input_lower for word in indian_keywords):
        return "indian"
    elif any(word in user_input_lower for word in classical_keywords):
        return "classical"
    elif any(word in user_input_lower for word in indie_keywords):
        return "indie"
    elif any(word in user_input_lower for word in pop_keywords):
        return "pop"
    elif any(word in user_input_lower for word in chill_keywords):
        return "chill"
    elif any(word in user_input_lower for word in romantic_keywords):
        return "romantic"
    elif any(word in user_input_lower for word in horror_keywords):
        return "horror"
    else:
        # Default mood based on sentiment
        if sentiment == 'POSITIVE':
            return "happy"
        elif sentiment == 'NEGATIVE':
            return "sad"
        else:
            return "neutral"

# Facial emotion recognition function
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

# Get songs based on mood
def get_songs_based_on_mood(mood):
    results = sp.search(q=mood, type='track', limit=20)
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
    songs = get_songs_based_on_mood(mood)
    print("\nHere are some songs for your mood:")
    for song in songs:
        print(song)
