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
    console.log('I can see the screen');
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

function startGame(){
    hideAllScreens();
    showGameScreen();
}

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






