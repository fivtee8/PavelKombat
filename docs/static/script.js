var count = 0;
var oldCount = 0;
var startDate;
var runHours = 230;
var tg = window.Telegram.WebApp;
var tgId;

fetchStartDate();
setupApp();

function doUpdate() {
    updateClock();
    sendClicks();
}

function setupApp() {
    tg.expand()

    console.log("User Id: " + tg.initDataUnsafe.user.id);
    tgId = tg.initDataUnsafe.user.id;
    fetchClickCount();
    var updater = setInterval(doUpdate, 5000);
}

function sendClicks() {
    let difference = parseFloat(count) - parseFloat(oldCount);

    loadJSON('https://fond-pangolin-lately.ngrok-free.app/put/clickcount/' + tgId + '/' + difference, processClickResponse);
}

function processClickResponse (data) {
    if (data.banned === '1') {
        // put banned code here
        console.log('Banned user');
    }

    else {
        oldCount = data.clicks;
        console.log('Updated clicks')
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

    if (count === '-1') {
        registerUser();
        count = 0;
    }

    oldCount = count;

    console.log("Fetched click count: " + count);
}

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
        success(JSON.parse(xhr.responseText));
      }
    }
  };
  xhr.open('GET', path, true);
  xhr.setRequestHeader('ngrok-skip-browser-warning', true)
  xhr.send();
}

function clickthis() {
    count++;
    console.log("Clicked!");
    document.querySelector('.counter').textContent = count;
}

function updateClock() {
    var now = new Date().getTime();
    var difference = now - startDate;
    var hourDiff = Math.round(difference / (60 * 60 * 1000))

    console.log("Now: " + now + " Diff: " + difference + " Hour dif: " + hourDiff);

    if (hourDiff >= runHours) {
        clearInterval(updater);
        document.getElementById("clock").innerHTML = "Ended!";
    }

    else {
        document.getElementById("clock").innerHTML = hourDiff + "/230";
    }
}