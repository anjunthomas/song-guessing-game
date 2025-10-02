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
let currentGameData = null;

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
    hideAllScreens();
    document.getElementById('game-screen').style.display = 'block';

    timeLeft = 30;
    isRunning = false;
    if (timer) clearInterval(timer);
    document.getElementById('countdown').textContent = '30';

    const audio = document.querySelector('audio');
    audio.src = roundData.preview_url;

    console.log(`Round ${roundData.round} of ${roundData.total_rounds}`);
    console.log(`Current score: ${roundData.score}`);
    console.log(`Artist: ${roundData.artist}`);
    

    audio.play();
    
    document.getElementById('countdown').textContent = '30';

}

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



function submitGuess() {
    const guess = document.getElementById('guess-input').value;
    
    if (!guess) {
        alert('Please enter a guess!');
        return;
    }
    
    if (!currentGameData || !currentGameData.game_id) {
        alert('No active game!');
        return;
    }
    
    fetch('/api/submit-guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            game_id: currentGameData.game_id,
            guess: guess
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Guess result:', data);
        
        if (data.is_correct) {
            alert(`Correct! The song was "${data.correct_answer}". Score: ${data.score}`);
        } else {
            alert(`Wrong! The correct answer was "${data.correct_answer}". Score: ${data.score}`);
        }
        
        if (data.message === "Game completed!") {
            alert(`Game Over! Final score: ${data.score}`);
            hideAllScreens();
            document.getElementById('home-screen').style.display = 'block';
        } else {
            currentGameData.round = data.round;
            currentGameData.score = data.score;
            currentGameData.preview_url = data.preview_url;
            startRound(currentGameData);
        }
    })
    .catch(error => {
        console.error('Error submitting guess:', error);
        alert('Failed to submit guess. Please try again.');
    });
}

let timeLeft = 30;
let isRunning = false;
let timer = null;    

function startCountdown() {
  
  const countdownElement = document.getElementById("countdown");

  if (!isRunning) {
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
    clearInterval(timer);
    isRunning = false;
  }
}






