var count = 0;
var oldCount = 0;
var startDate;
var runHours = 230;
var tg = window.Telegram.WebApp;
var tgId;
var queryId;
var updater;
var elapsedHours;

document.querySelectorAll('img.pavelimage').forEach(function(img) {
    img.addEventListener('contextmenu', function(e) {
        e.preventDefault(); // Prevent right-click context menu
    });

    img.addEventListener('touchstart', function(e) {
        e.preventDefault(); // Prevent long-press context actions
        clickThis();; // Call your function here
    });

    img.addEventListener('mousedown', function(e) {
        e.preventDefault(); // Prevent text highlighting
        clickThis();; // Call your function here
    });

    img.addEventListener('click', function(e) {
        clickThis();; // Call your function here
    });
});

document.getElementById("clickable-image").addEventListener("click", function(event) {
    createCoin(event.clientX, event.clientY);
});


fetchStartDate();
setupApp();

function createCoin(x, y) {
    const coin = document.createElement("img");
    coin.src = "/PavelKombat/static/coin.jpeg";  // Path to your coin image
    coin.className = "coin";
    coin.style.left = `${x}px`;
    coin.style.top = `${y}px`;

    document.getElementById("image-container").appendChild(coin);

    // Set initial velocity and random direction
    let velocityX = (Math.random() - 0.5) * 10; // Random horizontal speed
    let velocityY = -Math.random() * 15 - 5; // Random upward speed
    let gravity = 0.5; // Gravity effect

    function animateCoin() {
        // Update position based on velocity
        x += velocityX;
        y += velocityY;

        // Apply gravity to the vertical velocity
        velocityY += gravity;

        // Update coin position in the DOM
        coin.style.left = `${x}px`;
        coin.style.top = `${y}px`;

        // Remove the coin if it falls out of view
        if (y > window.innerHeight || x > window.innerWidth || x < 0) {
            coin.remove();
        } else {
            requestAnimationFrame(animateCoin);
        }
    }

    requestAnimationFrame(animateCoin);
}


function doUpdate() {
    updateClock();
    sendClicks();
}

function setupApp() {
    tgId = tg.initDataUnsafe.user.id;
    queryId = tg.initDataUnsafe.query_id;
    console.log("User Id: " + tgId);

    tg.expand();
    fetchClickCount();
    sendQueryId();

    let isBanned = checkBanned();

    if (isBanned) doBanned;
    else {
        console.log('User is not banned');
        var updater = setInterval(doUpdate, 5000);
    }
}

function checkBanned () {
    let ret = loadJSON('https://fond-pangolin-lately.ngrok-free.app/get/' + tgId + '/' + queryId, processBannedResponse);
    return ret;
}

function processBannedResponse (data) {
    if (data.banned === '1') return true;
    else return false;
}

function doBanned () {
    window.location.replace('banned.html');
}

function sendQueryId () {
    loadJSON('https://fond-pangolin-lately.ngrok-free.app/put/query_id/' + tgId + '/' + queryId, doNothing);
}

function doNothing(data) {
    return;
}

function sendClicks() {
    let difference = parseFloat(count) - parseFloat(oldCount);

    loadJSON('https://fond-pangolin-lately.ngrok-free.app/put/clickcount/' + tgId + '/' + queryId + '/' + difference, processClickResponse);
}

function doStale() {
    window.location.replace('stale.html')
}

function processClickResponse (data) {
    if (data.banned === '1') {
        console.log('Banned user');
        doBanned();
    }

    else if (data.stale === '1') {
        doStale();
    }

    else {
        oldCount = data.clicks;
        console.log('Updated clicks');
    }
}

function fetchClickCount() {
    loadJSON('https://fond-pangolin-lately.ngrok-free.app/request/clickcount/' + tgId, updateClickCount);
}

function fetchStartDate() {
    loadJSON('https://fond-pangolin-lately.ngrok-free.app/request/starttime/', updateStartDate);
}

function updateClickCount(data) {
    count = data.clicks;

/*    if (count === '-1') {
        registerUser();
        count = 0;
    }
*/
    oldCount = count;

    console.log("Fetched click count: " + count);
}

/*
function registerUser () {
    let temp_name = tg.initDataUnsafe.user.first_name;
    let temp_last = tg.initDataUnsafe.user.last_name;
    let temp_usr = tg.initDataUnsafe.user.username;

    console.log('Names: ' + temp_name + '; ' + temp_last + '; ' + temp_usr);

    if (!temp_name) temp_name = 'na';
    if (!temp_last) temp_last = 'na';
    if (!temp_usr) temp_usr = 'na';

    console.log('New names: ' + temp_name + '; ' + temp_last + '; ' + temp_usr);


    loadJSON('https://fond-pangolin-lately.ngrok-free.app/put/register/' + tgId + '/' + temp_usr + '/' + temp_name + '/' + temp_last, handleRegistrationResponse);
    console.log('Sent registration request!');
}

function handleRegistrationResponse (data) {
    if (data.message === 'success') {
        console.log('Registration successful!');
    }
    else console.log('Registration failed...');
}
*/

function updateStartDate(data) {
    startDate = new Date(data.time).getTime();
    console.log("data.time: " + data.time + " startdate: " + startDate);
    updateClock();
}

// loadJSON method to open the JSON file.
function loadJSON(path, success) {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        return success(JSON.parse(xhr.responseText));
      }
    }
  };
  xhr.open('GET', path, true);
  xhr.setRequestHeader('ngrok-skip-browser-warning', true)
  xhr.send();
}

function updateProgressBar(elapsedHours) {
    const totalHours = 230;
    const progressBar = document.getElementById('progressBar');

    // Calculate the percentage of progress
    const percentage = (elapsedHours / totalHours) * 100;

    // Update the width of the progress bar
    progressBar.style.width = percentage + '%';
    progressBar.textContent = Math.round(percentage) + '%';
}

function loadLeaderboard() {
    window.location.replace('leaderboard.html');
}

function clickThis() {
    count++;
    console.log("Clicked!");
    createCoin(0, 0);
    document.querySelector('.counter').textContent = count;
}

function updateClock() {
    var now = new Date().getTime();
    var difference = now - startDate;
    var hourDiff = Math.round(difference / (60 * 60 * 1000))

    elapsedHours = hourDiff;
    updateProgressBar(elapsedHours);

    console.log("Now: " + now + " Diff: " + difference + " Hour dif: " + hourDiff);

    if (hourDiff >= runHours) {
        clearInterval(updater);
        document.getElementById("clock").innerHTML = "Ended!";
    }

    else {
        document.getElementById("clock").innerHTML = hourDiff + "/230";
    }
}