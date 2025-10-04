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


function showResultScreen(track, guess, artist, album, imageUrl) {
    hideAllScreens();
    document.getElementById('result-screen').style.display = 'block';

    document.getElementById('correct-track').textContent = track;
    document.getElementById('user-guess').textContent = guess;
    document.getElementById('artist-name').textContent = artist;
    document.getElementById('album-name').textContent = album;
    document.getElementById('album-cover').src = imageUrl;
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
let currentGameData = null
let guessesUsed = 0;


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
        currentGameData = data;
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
    guessesUsed = 0;
    document.getElementById('guess1').style.backgroundColor = 'white';
    document.getElementById('guess2').style.backgroundColor = 'white';
    document.getElementById('guess3').style.backgroundColor = 'white';
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
    let currentGameId = currentGameData.game_id;
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

        updateCircle(data.is_correct);

        score = data.score;

        if (data.message === "Game completed!") {
          showGameOverScreen();
        } else {
            if (data.round !== currentGameData.round) {

                // show result screen here


                setTimeout(() => {
                    
                    guessesUsed = 0;
                    document.getElementById('guess1').style.backgroundColor = 'white';
                    document.getElementById('guess2').style.backgroundColor = 'white';
                    document.getElementById('guess3').style.backgroundColor = 'white';
                    // Update stored round number
                    currentGameData.round = data.round;

                    timeLeft = 30;
                    clearInterval(timer);
                    isRunning = false;
                    startCountdown();

                    if (data.preview_url) {
                        playAudio(data.preview_url);
                    }
                    showGameScreen();
                }, 1000);
            }
            document.getElementById('guess-input').value = '';
        }
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
function updateCircle(isCorrect) {
    guessesUsed++;
    const circle = document.getElementById(`guess${guessesUsed}`);
    if (circle) circle.style.backgroundColor = isCorrect ? 'green' : 'red';
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




