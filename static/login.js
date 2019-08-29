function login() {

    var password = document.getElementById("password").value;
    var md = forge.md.sha256.create();
    md.update(password);
    document.cookie = "gyc_login=" + md.digest().toHex();
    var request = new XMLHttpRequest();
    request.onreadystatechange = () => {
        if (request.readyState === 4) {
            if (request.status === 200) {
                if (location.pathname === '/admin') {
                    location.reload();
                } else {
                    location.href = '/admin';
                }
            } else if (request.status === 403) {
                document.getElementById("error").innerText = "Password wrong!";
                setTimeout(() => {
                    document.getElementById("error").innerText = "";
                }, 700);
            }
        }
    };
    request.open("GET", "/api/setting/password");
    request.send();
}