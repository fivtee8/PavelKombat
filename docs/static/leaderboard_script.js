document.addEventListener("DOMContentLoaded", function() {
    fetchLeaderboard();
});

function fetchLeaderboard() {
    fetch('https://fond-pangolin-lately.ngrok-free.app/leaderboard/')
        .then(response => response.json())
        .then(data => {
            populateLeaderboard(data);
        })
        .catch(error => {
            console.error('Error fetching leaderboard data:', error);
        });
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
