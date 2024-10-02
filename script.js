document.getElementById('facial-mood-btn').addEventListener('click', () => {
    fetch('/facial-mood')
      .then(response => response.json())
      .then(data => {
        document.getElementById('facial-mood-result').querySelector('span').textContent = data.mood;
      })
      .catch(error => console.error('Error detecting facial mood:', error));
  });
  
  document.getElementById('text-mood-btn').addEventListener('click', () => {
    const userInput = document.getElementById('mood-text').value;
    fetch('/text-mood', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: userInput }),
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById('text-mood-result').querySelector('span').textContent = data.mood;
      })
      .catch(error => console.error('Error analyzing text mood:', error));
  });
  
  document.getElementById('get-songs-btn').addEventListener('click', () => {
    const mood = document.getElementById('facial-mood-result').querySelector('span').textContent || 'happy';
    fetch('/spotify-songs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mood: mood }),
    })
      .then(response => response.json())
      .then(data => {
        const songsList = document.getElementById('songs-list');
        songsList.innerHTML = '';  // Clear previous songs
        data.songs.forEach(song => {
          const li = document.createElement('li');
          li.textContent = song;
          songsList.appendChild(li);
        });
      })
      .catch(error => console.error('Error getting Spotify songs:', error));
  });
  
  document.getElementById('get-videos-btn').addEventListener('click', () => {
    const mood = document.getElementById('facial-mood-result').querySelector('span').textContent || 'happy';
    fetch('/youtube-videos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mood: mood }),
    })
      .then(response => response.json())
      .then(data => {
        const videosList = document.getElementById('videos-list');
        videosList.innerHTML = '';  // Clear previous videos
        data.videos.forEach(video => {
          const li = document.createElement('li');
          li.textContent = video;
          videosList.appendChild(li);
        });
      })
      .catch(error => console.error('Error getting YouTube videos:', error));
  });
  
