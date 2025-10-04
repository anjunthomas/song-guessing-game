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

function showHomeScreen() {
    hideAllScreens();
    document.getElementById('home-screen').style.display = 'block';
}

function showGameScreen() {
    hideAllScreens();
    document.getElementById('final-score').textContent = score;
    document.getElementById('game-screen').style.display = 'block';
}

function showGameOverScreen() {
    hideAllScreens();
    document.getElementById('final-score').textContent = score;
    document.getElementById('gameover-screen').style.display = 'block';
}

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

let score = 0; /*default that will be changed later*/

function startGame() {
    const username = document.getElementById('username').value;
    const artist = document.getElementById('artist').value;
    if (!username || !artist) {
        alert('Please enter both username and artist name!');
        return;
    }

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

    startCountdown();
    playAudio(roundData.preview_url);
    score = roundData.score;
    document.getElementById('real-score').textContent = score;

    
    /* put game logic here 
    should display round number and artist name
    should set up an audio player, or brower autoplay with previewURL, snippet from iTunesSearchAPI
    create a input field for guesses
    handling the timer functionality
    handling the guess submission
    
    */
}

function submitGuess(){
    let currentGameId = document.getElementById('username').value;
    const guess = document.getElementById('guess-input').value;

    if (!guess) {
        alert('Please enter a guess!');
        return;
    }

    fetch('/api/submit-guess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_id: currentGameId,
      guess: guess
    })
  })

  .then(response => {
        if (!response.ok) {
            throw new Error('Failed to submit guess');
        }
        return response.json();
    })
    .then(data => {
        console.log('Guess submitted:', data);

        updateCircle(data.round, data.is_correct);

        score = data.score;
 
        alert(data.message);
    })
    .catch(error => {
        console.error('Error submitting guess:', error);
        alert('Failed to submit guess. Please try again.');
    });
}

//function to play the audio
function playAudio(url) {
  const audio = document.getElementById('audio-preview');
  audio.src = url;
  audio.play().catch(err => console.log('Autoplay blocked:', err));
}

//Changes the color of the guess circles
function updateCircle(round, isCorrect) {
    const circle = document.getElementById(`guess${round}`);
    if (circle) circle.style.backgroundColor = isCorrect ? 'green' : 'red';
}

function nextRound() {
    fetch('/api/next-round')
    .then(response => {
        if (!response.ok) throw new Error('Failed to get next round');
        return response.json();
    })
    .then(data => {
        console.log('Next round:', data);
        playAudio(data.preview_url);
    })
    .catch(error => {
        console.error('Error loading next round:', error);
    });
}

let timeLeft = 30;
let isRunning = false;
let timer = null;

function startCountdown() {   
  if (!isRunning) {
    // start or resume
    isRunning = true;
    const countdownElement = document.getElementById("countdown");

    timer = setInterval(() => {
      timeLeft--;
      countdownElement.textContent = timeLeft;

      if (timeLeft <= 0) {
        clearInterval(timer);
        isRunning = false;
        showGameOverScreen();
      }
    }, 1000);

  } 
}







