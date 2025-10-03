// start by hiding all screens
function hideAllScreens() {
    document.getElementById('home-screen').style.display = 'none';
    document.getElementById('setup-screen').style.display = 'none';
    document.getElementById('game-screen').style.display = 'none';
    document.getElementById('result-screen').style.display = 'none';
    document.getElementById('gameover-screen').style.display = 'none';
}
// showing the screen that you want to display
function showSetupScreen() {
    hideAllScreens();
    document.getElementById('setup-screen').style.display = 'block';
}

function showGameScreen() {
    hideAllScreens();
    document.getElementById('game-screen').style.display = 'block';
}

function showResultScreen(track, guess, artist, album, imageUrl) {
    hideAllScreens();
    document.getElementById('result-screen').style.display = 'block';

    document.getElementById('correct-track').textContent = track;
    document.getElementById('user-guess').textContent = guess;
    document.getElementById('artist-name').textContent = artist;
    document.getElementById('album-name').textContent = album;
    document.getElementById('album-cover').src = imageUrl;
} 

//for testing:
/*
showResultScreen(
    "Dangerous Woman",
    "User Guess",
    "Ariana Grande",
    "Dangerous Woman",
    "https://www.udiscovermusic.com/wp-content/uploads/2019/05/Ariana-Grande-Dangerous-Woman-album-cover-web-optimised-820-820x820.jpg"
);
*/

function testScreen(screenName) {
    hideAllScreens();
    document.getElementById(screenName + '-screen').style.display = 'block';
}
/* 
HOW TO SHOW/HIDE SCREENS:

To show a specific screen:
    set the screen you want to display inside of getElementById in the showSetupScreen function 

Example to show game screen:

document.getElementById('game-screen').style.display = 'block';
*/



/* startgame() function 
    create start game function here. It should check if the artist and username both exist
    error handling if it doesn't
    and then using the /api/start-game route to create a POST fetch request

*/

let currentUsername = ""; //global variable to store current username

function startGame() {
    const username = document.getElementById('username').value;
    const artist = document.getElementById('artist').value;
    if (!username || !artist) {
        alert('Please enter both username and artist name!');
        return;
    }

    currentUsername = username; //stores current username for later use

    //POST fetch request to start the game
    fetch('/api/start-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: username,
            artist: artist
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to start game');
        }
        return response.json();
    })
    .then(data => {
        console.log('Game started:', data);
        startRound(data); //game starts
    })
    .catch(error => {
        console.error('Error starting game: ', error);
        alert('Failed to start game. Please try again.');
    })
}

/*
function startGame(){
    hideAllScreens();
    showGameScreen();
}
    */

function startRound(roundData) {
    hideAllScreens();
    document.getElementById('game-screen').style.display = 'block';

    /* 
    round data parameter contains
        current round number = roundData.round
        artist name = roundData.artist
        roundData.preview_url = sound audio url
        roundData.score = current score
    */

    
    /* put game logic here 
    should display round number and artist name
    should set up an audio player, or brower autoplay with previewURL, snippet from iTunesSearchAPI
    create a input field for guesses
    handling the timer functionality
    handling the guess submission
    
    */
}

function submitGuess(){
    let currentGameId = "testuser"; //testing purposes
    const guess = document.getElementById('guess-input').value;
    fetch('/api/submit-guess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_id: currentGameId,
      guess: guess
    })
  })
}


function startCountdown() {
  let timeLeft = 30;
  let isRunning = false;
  let timer = null;    
  const countdownElement = document.getElementById("countdown");

  if (!isRunning) {
    // start or resume
    isRunning = true;

    timer = setInterval(() => {
      timeLeft--;
      countdownElement.textContent = timeLeft;

      if (timeLeft <= 0) {
        clearInterval(timer);
        isRunning = false;
      }
    }, 1000);

  } else {
    // pause countdown
    clearInterval(timer);
    isRunning = false;
  }
}

function startNextRound() {
    fetch('api/next-round', {
        method: 'POST',
        headers: {'Content-Type': 'application/json' },
        body: JSON.stringify({username: currentUsername})
    })
    .then(response => response.json())
    .then(newRoundData => {
        startRound(newRoundData);
    })
    .catch(error => {
        console.error('Error starting next round: ', error);
    });
}
