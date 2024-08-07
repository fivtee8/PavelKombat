document.addEventListener("DOMContentLoaded", function() {
    fetchLeaderboard();
});

function fetchLeaderboard() {
    loadJSON('https://fond-pangolin-lately.ngrok-free.app/leaderboard/', populateLeaderboard);
}

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

function populateLeaderboard(data) {
    const tbody = document.querySelector("#leaderboard tbody");
    tbody.innerHTML = '';

    data.boards.forEach(([name, click_count]) => {
        const row = document.createElement('tr');

        const nameCell = document.createElement('td');
        nameCell.textContent = name;

        const clickCountCell = document.createElement('td');
        clickCountCell.textContent = click_count;

        row.appendChild(nameCell);
        row.appendChild(clickCountCell);
        tbody.appendChild(row);
    });
}
