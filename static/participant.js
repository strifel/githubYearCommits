function loadParticipant(username, query) {
    let participantRequest = new XMLHttpRequest();
    participantRequest.onreadystatechange = () => {
        if (participantRequest.readyState === 4) {
            if (participantRequest.status === 200) {
                // No error. -> Hide the error window
                document.getElementById('error').hidden = true;
                // Loading...
                let participant = JSON.parse(participantRequest.responseText);
                document.title = 'Participant - ' + participant['general']['username'];
                document.getElementById('profile_picture').src = 'https://github.com/' + participant['general']['username'] + '.png?size=5000';
                document.getElementById('profile_picture').hidden = false;
                {
                    let link = document.getElementById('profile_link');
                    // Not using innerHTML here to not allow user to insert html tags by changing his username...
                    {
                        let h3 = document.createElement('h3');
                        h3.innerText = participant['general']['username'];
                        link.appendChild(h3);
                    }
                    link.href = 'https://github.com/' + participant['general']['username'];
                }
                document.getElementById('contributions_in_year').innerText = 'Contributions (' + participant['stats']['contributions']['year'] + '): ' + participant['stats']['contributions']['contributions'];
                // Check if email exists because it is optional/controllable by setting
                if (participant['general']['commit_mail'] !== null) {
                    let mail = document.getElementById('commit_email');
                    mail.innerText = participant['general']['commit_mail'];
                    mail.href = 'mailto:' + participant['general']['commit_mail'];
                    document.getElementById('commit_email_header').hidden = false;
                } else {
                    document.getElementById('commit_email_header').hidden = true;
                }
                document.getElementById('contribution_streak').innerText = 'Contribution streak: ' + participant['stats']['contribution_streak'];
                //Languages
                let languages = document.getElementById('languages');
                participant['languages'].forEach((language) => {
                    if (language['language'] !== 'None') {
                        let languageElement = document.createElement('li');
                        languageElement.innerText = language['language'];
                        languageElement.classList.add('language');
                        languageElement.setAttribute('data-affect-dark-mode', 'color');
                        if (languages.childElementCount <= 0) {
                            languages.appendChild(languageElement);
                        } else {
                            languages.insertBefore(document.createElement('br'), languages.firstChild);
                            languages.insertBefore(languageElement, languages.firstChild);
                        }
                    }
                });
                document.getElementById('languageText').hidden = false;
                // Reload darkmode (Yeah bad implementation. But who cares? The whole project is coded like this!)
                changeDarkMode(false);
                changeDarkMode(false);
                // Hide the spinner
                document.getElementById('spinner').hidden = true;
            } else {
                if (participantRequest.responseText.startsWith("{")) {
                    // Should be json...
                    document.getElementById('error_body').innerText = JSON.parse(participantRequest.responseText)['error'];
                    document.getElementById('error').hidden = false;
                } else {
                    // Some error (maybe) HTML formatted. Just relay it...
                    document.body.innerHTML = participantRequest.responseText;
                }
            }
        }
    };
    participantRequest.open('GET', '/api/participants/' + username + query);
    participantRequest.send();
}
{
    let path = location.pathname.split('/');
    loadParticipant(path[path.length - 1], location.search)
}
