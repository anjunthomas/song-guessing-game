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





