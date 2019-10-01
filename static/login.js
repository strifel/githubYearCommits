function login() {

    var password = document.getElementById("password").value;
    var username = document.getElementById("username").value;
    var request = new XMLHttpRequest();
    request.onreadystatechange = () => {
        if (request.readyState === 4) {
            if (request.status === 200) {
                if (request.responseText.startsWith("{") && JSON.parse(request.responseText).hasOwnProperty('token')) {
                    localStorage.setItem("token", JSON.parse(request.responseText)['token']);
                    localStorage.setItem("username", username);
                }
                location.href = "/admin";
            } else if (request.status === 403) {
                document.getElementById("error").innerText = "Password wrong!";
                setTimeout(() => {
                    document.getElementById("error").innerText = "";
                }, 700);
            }
        }
    };
    request.open("POST", "/api/login");
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify({"username": username, "password": password}));
}