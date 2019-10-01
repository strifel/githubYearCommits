// Script provides AJAX Connection for Admin Interface
// Throw not logged in user to login page. This does not validate the token!
if (localStorage.getItem("token") == null) location.href = "/login";
// Settings
document.getElementById('setting').onchange = () => {
    let setting = document.getElementById('setting').value;
    document.getElementById('settingValue').classList.remove("settingValueError");
    document.getElementById('settingValue').value = "";
    if (setting !== 'placeholder') {
        let settingValueRequest = new XMLHttpRequest();
        settingValueRequest.onreadystatechange = () => {
            if (settingValueRequest.readyState === 4 && settingValueRequest.status === 200) {
                let settingValue = document.getElementById('settingValue');
                settingValue.hidden = false;
                settingValue.placeholder = JSON.parse(settingValueRequest.responseText)['value'];
            }
        };
        settingValueRequest.open('GET', '/api/setting/' + setting);
        settingValueRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
        settingValueRequest.send();
    }
};
// Call to show value directly. (Firefox saves selection)
document.getElementById('setting').onchange();

function saveSetting() {
    let setting = document.getElementById('setting').value;
    let value = document.getElementById('settingValue').value;
    if (!setting.hidden && value !== null) {
        let settingChangeRequest = new XMLHttpRequest();
        settingChangeRequest.onreadystatechange = () => {
            if (settingChangeRequest.readyState === 4 && settingChangeRequest.status === 200) {
                document.getElementById('settingValue').placeholder = JSON.parse(settingChangeRequest.responseText)['value'];
                document.getElementById('settingValue').value = '';
                document.getElementById('settingValue').classList.remove("settingValueError");
            } else if (settingChangeRequest.readyState === 4 && settingChangeRequest.status === 400) {
                document.getElementById('settingValue').classList.add("settingValueError");
            }
        };
        settingChangeRequest.open('PUT', '/api/setting/' + setting);
        settingChangeRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
        settingChangeRequest.setRequestHeader('Content-Type', 'application/json');
        settingChangeRequest.send(JSON.stringify({'value': value}))

    }
}

//Participants
let selectedUsersPermissions = "";

function addParticipant() {
    let usernameField = document.getElementById('participantUsername');
    let addRequest = new XMLHttpRequest();
    addRequest.onreadystatechange = () => {
        if (addRequest.readyState === 4) {
            reloadParticipants();
            usernameField.value = '';
        }
    };
    addRequest.open('POST', '/api/participants/' + usernameField.value);
    addRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    addRequest.send();
}

function removeParticipant() {
    let username = document.getElementById('participants').value;
    let removeRequest = new XMLHttpRequest();
    removeRequest.onreadystatechange = () => {
        if (removeRequest.readyState === 4) {
            reloadParticipants();
        }
    };
    removeRequest.open('DELETE', '/api/participants/' + username);
    removeRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    removeRequest.send();
}

function reloadParticipants() {
    let chooser = document.getElementById('participants');
    chooser.innerHTML = '<option value="placeholder">Please choose a participant to remove</option>';
    let getRequest = new XMLHttpRequest();
    getRequest.onreadystatechange = () => {
        if (getRequest.readyState === 4 && getRequest.status === 200) {
            JSON.parse(getRequest.responseText).forEach((name) => {
               let participant = document.createElement('option');
               participant.value = name;
               participant.innerText = name;
               chooser.add(participant);
            });
        }
    };
    getRequest.open('GET', '/api/participants');
    getRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    getRequest.send();
}

reloadParticipants();

// Users

function reloadUsers() {
    let chooser = document.getElementById('users');
    chooser.innerHTML = '<option value="placeholder">Please choose a user to edit</option>';
    let getUserRequest = new XMLHttpRequest();
    getUserRequest.onreadystatechange = () => {
        if (getUserRequest.readyState === 4 && getUserRequest.status === 200) {
            JSON.parse(getUserRequest.responseText).forEach((name) => {
               let participant = document.createElement('option');
               participant.value = name;
               participant.innerText = name;
               chooser.add(participant);
            });
        } else if (getUserRequest.readyState === 4 && getUserRequest.status === 403) {
            chooser.innerHTML = '<option value="'+ localStorage.getItem("username") + '">You</option>';
            chooser.hidden = true;
            chooser.onchange();
        }
    };
    getUserRequest.open('GET', '/api/users');
    getUserRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    getUserRequest.send();
}


document.getElementById('users').onchange = () => {
    let option = document.getElementById('users').value;
    if (option === "placeholder") {
        document.getElementById('userPassword').hidden = true;
        document.getElementById('userPermissionsLabel').hidden = true;
        document.getElementById('userPermissions').hidden = true;
        document.getElementById('userPermissionAdd').hidden = true;
        return;
    }
    document.getElementById('userPassword').hidden = false;
    let userInfoRequest = new XMLHttpRequest();
    userInfoRequest.onloadend = () => {
        if (userInfoRequest.status === 200) {
            let response = JSON.parse(userInfoRequest.responseText);
            selectedUsersPermissions = response['permissions'];
            if (selectedUsersPermissions === "*") {
                document.getElementById('userPermissions').innerHTML = "<p class='permission' data-affect-dark-mode='color' onclick='removePermission(\"*\");'>All permissions granted!</p>";
                document.getElementById('userPermissionAdd').hidden = true;
            } else {
                document.getElementById('userPermissions').innerHTML = "";
                selectedUsersPermissions.slice(1, selectedUsersPermissions.length - 1).split(")(").forEach((permission) => {
                    document.getElementById('userPermissions').innerHTML += "<p class='permission' data-affect-dark-mode='color' onclick='removePermission(\"" + permission + "\");'>" + permission + ",</p>";
                });
                document.getElementById('userPermissionAdd').hidden = false;
            }
            document.getElementById('userPermissions').hidden = false;
            document.getElementById('userPermissionsLabel').hidden = false;
        } else if (userInfoRequest.status === 403) {
            document.getElementById('userPermissions').hidden = true;
            document.getElementById('userPermissionsLabel').hidden = true;
        }

        //Reload dark mode
       changeDarkMode(false);
       changeDarkMode(false);
    };
    userInfoRequest.open("GET", "/api/users/" + option);
    userInfoRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    userInfoRequest.send();
};


document.getElementById('userPassword').onchange = () => {
    let setPasswordRequest = new XMLHttpRequest();
    setPasswordRequest.onreadystatechange = () => {
        if (setPasswordRequest.readyState === 4) {
            document.getElementById('userPassword').value = '';
        }
    };
    setPasswordRequest.open('PUT', '/api/users/' + document.getElementById('users').value);
    setPasswordRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    setPasswordRequest.setRequestHeader('Content-Type', 'application/json');
    setPasswordRequest.send(JSON.stringify({"password": document.getElementById('userPassword').value}));
};

function removePermission(permission) {
    if (permission !== "*") {
        permission = "(" + permission + ")";
    }
    selectedUsersPermissions = selectedUsersPermissions.replace(permission, "");
    syncUserPermissions();
}


document.getElementById('userPermissionAdd').onchange = () => {
    let value = document.getElementById('userPermissionAdd').value;
    if (value === "") return;
    if (value === "*") {
        selectedUsersPermissions = "*";
    } else {
        selectedUsersPermissions += "(" + value + ")";
    }
    syncUserPermissions();
};

function syncUserPermissions() {
    let setPermissionRequest = new XMLHttpRequest();
    setPermissionRequest.onreadystatechange = () => {
        if (setPermissionRequest.readyState === 4) {
            document.getElementById('userPermissionAdd').value = '';
            document.getElementById('users').onchange();
        }
    };
    setPermissionRequest.open('PUT', '/api/users/' + document.getElementById('users').value);
    setPermissionRequest.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));
    setPermissionRequest.setRequestHeader('Content-Type', 'application/json');
    setPermissionRequest.send(JSON.stringify({"permissions": selectedUsersPermissions}));
}

reloadUsers();
document.getElementById('users').onchange();


