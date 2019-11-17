function reloadContributions() {
    let request = new XMLHttpRequest();
    request.onloadend = () => {
        if (request.status === 200) {
            let response = JSON.parse(request.responseText);
            document.getElementById('title').innerText = "Contributions " + response['information']['duration'].replace("eternity", "ever").replace("year", "this year");
            let table = document.getElementById('contributionsTable');
            response['participants'].forEach((participant) => {
                // Row
                let row = document.createElement('tr');
                row.classList.add('contributionUser');
                table.insertBefore(row, table.firstChild);
                // Username
                let username = document.createElement('td');
                username.classList.add('usernameTD');
                username.innerHTML = '<a class="username" href="/participant/' + participant['username'] + '">' + participant['username'] + '</a>';
                row.appendChild(username);
                // Contibution
                let contribution = document.createElement('td');
                contribution.classList.add('contributionsTD');
                contribution.setAttribute('data-affect-dark-mode', 'color');
                contribution.innerHTML = '<a class="contributions">' + participant['count'] + '</a>';
                row.appendChild(contribution);
                // Percentage
                row.innerHTML += '<td class="percentageTD" data-affect-dark-mode="color"><a class="percentage"></a></td>';
            });
            // Reload dark mode
            changeDarkMode(false);
            changeDarkMode(false);
            // Set percentage
            replacePercentageHandler();
            // Hide spinner
            document.getElementById('spinner').hidden = true;
            document.getElementById('loadingText').hidden = true;
        }
    };
    request.open("GET", "/api/contributions");
    if (localStorage.getItem("token") != null) {
        request.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    }
    request.send();
}

reloadContributions();