// to hide all screens except home when page loads
document.addEventListener('DOMContentLoaded', function() {
    showHomePage();
});

// 
function showHomePage() {
    hideAllScreens();
    document.getElementById('home-screen').style.display = 'block';
}

// Hide all screens
function hideAllScreens() {
    document.getElementById('home-screen').style.display = 'none';
    document.getElementById('setup-screen').style.display = 'none';
    document.getElementById('game-screen').style.display = 'none';
    document.getElementById('result-screen').style.display = 'none';
    document.getElementById('gameover-screen').style.display = 'none';
}

/* 
HOW TO SHOW/HIDE SCREENS:

To show a specific screen:
    set the screen you want to display = 'block'

Example to show setup screen:
hideAllScreens();
document.getElementById('setup-screen').style.display = 'block';

Add your game functions below this comment
*/