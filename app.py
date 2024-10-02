import spotipy
from spotipy.oauth2 import SpotifyOAuth
from transformers import pipeline

# Initialize sentiment analysis
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Analyze mood based on user input
def analyze_mood(user_input):
    result = sentiment_analyzer(user_input)[0]
    if result['label'] == 'POSITIVE':
        return "happy"
    elif result['label'] == 'NEGATIVE':
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
