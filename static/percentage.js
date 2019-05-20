let users = document.querySelectorAll('.contributionUser');
let choosen = '';

function calculateFor(contributions) {
    users.forEach((user) => {
        let ownContributions = parseInt(user.getElementsByClassName('contributions')[0].innerText);
        user.getElementsByClassName('percentage')[0].innerText = '(' + Math.round((100 / contributions) * ownContributions) + '%)';
    });
}

function clear() {
    users.forEach((user) => {
        user.getElementsByClassName('percentage')[0].innerText = '';
    });
}

users.forEach((user) => {
    user.onclick = () => {
        let username = user.getElementsByClassName('username')[0].innerText;
        if (username === choosen) {
            clear();
            choosen = '';
        } else {
            let contributions = parseInt(user.getElementsByClassName('contributions')[0].innerText);
            calculateFor(contributions);
            choosen = username;
        }
    };
});

