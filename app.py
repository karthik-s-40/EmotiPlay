import spotipy
from spotipy.oauth2 import SpotifyOAuth
from transformers import pipeline

# Initialize sentiment analysis
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Analyze mood based on user input
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
    else:
        # Default mood based on sentiment
        if sentiment == 'POSITIVE':
            return "happy"
        elif sentiment == 'NEGATIVE':
            return "sad"
        else:
            return "neutral"


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
    user_input = input("How are you feeling today? ")
    mood = analyze_mood(user_input)
    print(f"Detected mood: {mood}")
    
    songs = get_songs_based_on_mood(mood)
    print("\nHere are some songs for your mood:")
    for song in songs:
        print(song)
