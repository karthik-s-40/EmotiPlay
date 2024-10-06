let currentSpotifyOffset = 0;
let currentYouTubePageToken = null;

// Handle facial mood detection
document.getElementById('facial-mood-btn').addEventListener('click', () => {
    fetch('/facial-mood')
        .then(response => response.json())
        .then(data => {
            const detectedMood = data.mood;
            document.getElementById('detected-mood').textContent = detectedMood;
            document.getElementById('mood-detection').style.display = 'none';
            document.getElementById('confirm-mood-section').style.display = 'block';
        })
        .catch(error => console.error('Error detecting facial mood:', error));
});

// Handle mood confirmation
document.getElementById('confirm-mood-btn').addEventListener('click', () => {
    document.getElementById('confirm-mood-section').style.display = 'none';
    document.getElementById('choice-section').style.display = 'block';
});

// Handle mood rejection
document.getElementById('reject-mood-btn').addEventListener('click', () => {
    document.getElementById('confirm-mood-section').style.display = 'none';
    document.getElementById('manual-mood-section').style.display = 'block';
});

// Submit manual mood
document.getElementById('manual-mood-btn').addEventListener('click', () => {
    console.log("Manual mood button clicked");
    document.getElementById('mood-detection').style.display = 'none';
    document.getElementById('manual-mood-section').style.display = 'block';
});

// Key listener for manual mood input
document.getElementById('manual-mood-input').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        submitManualMood();
    }
});

document.getElementById('submit-manual-mood-btn').addEventListener('click', submitManualMood);

function submitManualMood() {
    const manualMood = document.getElementById('manual-mood-input').value;
    if (manualMood) {
        console.log('Manual Mood Entered:', manualMood);
        document.getElementById('manual-mood-section').style.display = 'none';
        document.getElementById('detected-mood').textContent = manualMood;
        document.getElementById('choice-section').style.display = 'block';
    }
}


// Handle song choice
document.getElementById('choose-songs-btn').addEventListener('click', () => {
    const mood = document.getElementById('detected-mood').textContent;
    fetchSpotifySongs(mood);
});

// Function to fetch Spotify songs
function fetchSpotifySongs(mood) {
    fetch('/spotify-songs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mood: mood, offset: currentSpotifyOffset }),
    })
        .then(response => response.json())
        .then(data => {
            const resultsList = document.getElementById('results-list');
            resultsList.innerHTML = '';
            data.songs.forEach(song => {
                const li = document.createElement('li');
                li.textContent = song;
                resultsList.appendChild(li);
            });

            // Show pagination buttons
            document.getElementById('pagination-songs').style.display = data.next_offset !== null ? 'block' : 'none';
            currentSpotifyOffset = data.next_offset || 0;
            document.getElementById('next-songs-btn').onclick = () => loadMoreSpotifySongs(mood);

            document.getElementById('choice-section').style.display = 'none';
            document.getElementById('results-section').style.display = 'block';
        })
        .catch(error => console.error('Error getting Spotify songs:', error));
}

// Function to load more Spotify songs
function loadMoreSpotifySongs(mood) {
    fetch('/spotify-songs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mood: mood, offset: currentSpotifyOffset }),
    })
        .then(response => response.json())
        .then(data => {
            const resultsList = document.getElementById('results-list');
            data.songs.forEach(song => {
                const li = document.createElement('li');
                li.textContent = song;
                resultsList.appendChild(li);
            });

            // Update pagination
            currentSpotifyOffset = data.next_offset || 0;
            document.getElementById('pagination-songs').style.display = data.next_offset !== null ? 'block' : 'none';
        })
        .catch(error => console.error('Error loading more Spotify songs:', error));
}

// Handle video choice
document.getElementById('choose-videos-btn').addEventListener('click', () => {
    const mood = document.getElementById('detected-mood').textContent;
    fetchYouTubeVideos(mood);
});

// Function to fetch YouTube videos
function fetchYouTubeVideos(mood) {
    fetch('/youtube-videos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mood: mood, next_page_token: currentYouTubePageToken }),
    })
        .then(response => response.json())
        .then(data => {
            const resultsList = document.getElementById('results-list');
            resultsList.innerHTML = '';
            data.videos.forEach(video => {
                const li = document.createElement('li');
                li.textContent = video;
                resultsList.appendChild(li);
            });

            // Show pagination buttons
            document.getElementById('pagination-videos').style.display = data.next_page_token ? 'block' : 'none';
            currentYouTubePageToken = data.next_page_token || null;
            document.getElementById('next-videos-btn').onclick = () => loadMoreYouTubeVideos(mood);

            document.getElementById('choice-section').style.display = 'none';
            document.getElementById('results-section').style.display = 'block';
        })
        .catch(error => console.error('Error getting YouTube videos:', error));
}

// Function to load more YouTube videos
function loadMoreYouTubeVideos(mood) {
    fetch('/youtube-videos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mood: mood, next_page_token: currentYouTubePageToken }),
    })
        .then(response => response.json())
        .then(data => {
            const resultsList = document.getElementById('results-list');
            data.videos.forEach(video => {
                const li = document.createElement('li');
                li.textContent = video;
                resultsList.appendChild(li);
            });

            // Update pagination
            currentYouTubePageToken = data.next_page_token || null;
            document.getElementById('pagination-videos').style.display = data.next_page_token ? 'block' : 'none';
        })
        .catch(error => console.error('Error loading more YouTube videos:', error));
}

// Key listener for navigation
document.addEventListener('keydown', (event) => {
    const resultsList = document.getElementById('results-list');
    const items = resultsList.getElementsByTagName('li');
    
    if (event.key === 'ArrowDown') {
        // Move down the list
        for (let i = 0; i < items.length; i++) {
            if (items[i].classList.contains('selected')) {
                items[i].classList.remove('selected');
                if (i + 1 < items.length) {
                    items[i + 1].classList.add('selected');
                }
                break;
            } else if (i === 0) {
                items[i].classList.add('selected');
            }
        }
    } else if (event.key === 'ArrowUp') {
        // Move up the list
        for (let i = 0; i < items.length; i++) {
            if (items[i].classList.contains('selected')) {
                items[i].classList.remove('selected');
                if (i - 1 >= 0) {
                    items[i - 1].classList.add('selected');
                }
                break;
            }
        }
    } else if (event.key === 'Enter') {
        // Handle selection
        for (let i = 0; i < items.length; i++) {
            if (items[i].classList.contains('selected')) {
                alert('Selected: ' + items[i].textContent);
                break;
            }
        }
    }
});
// Function to create and animate emojis in the background
function createEmoji() {
  const emojis = ['🙂', '😊', '🥰', '😭', '😄', '😎', '🥳', '😤', '😝', '😌'];
  const emojiContainer = document.querySelector('.emoji-background');

    // Create a random emoji element
    const emojiElement = document.createElement('div');
    emojiElement.className = 'emoji';
    emojiElement.innerText = emojis[Math.floor(Math.random() * emojis.length)];

    // Position it randomly on the screen
    emojiElement.style.left = Math.random() * 100 + 'vw'; // Random horizontal position
    emojiElement.style.top = Math.random() * 100 + 'vh'; // Random vertical position
    emojiElement.style.fontSize = Math.random() * 3 + 2 + 'rem'; // Random size between 2rem and 5rem

    // Append to emoji container
    emojiContainer.appendChild(emojiElement);

    // Optional: Remove after a delay (e.g., 5 seconds)
    setTimeout(() => {
        emojiContainer.removeChild(emojiElement);
    }, 5000); // Keep emoji for 5 seconds before removal
}

// Create a fixed number of emojis at intervals
setInterval(createEmoji, 1000);

