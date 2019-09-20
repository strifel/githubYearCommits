// This script depends on JQuery!

function changeDarkMode(userSet) {
    let button = document.getElementById("darkModeButton");
    if (button != null) {
        if (button.innerText === "Dark Mode") { //Change to dark mode
            button.innerText = "Light Mode";
            button.style.backgroundColor = "#f5f5f5";
            button.style.color = "#1D1F21";
        } else { //change to Light Mode
            button.innerText = "Dark Mode";
            button.style.backgroundColor = "#1D1F21";
            button.style.color = "#f5f5f5";
        }
    }
    let newColor;
    if (document.darkMode === true) {
        document.darkMode = false;
        if (userSet) {
            localStorage.setItem("dark", "false");
        }
        document.body.style.backgroundColor = "#f5f5f5";
        newColor = '#1D1F21';
    } else {
        document.darkMode = true;
        if (userSet) {
            localStorage.setItem("dark", "true");
        }
        document.body.style.backgroundColor = "#1D1F21";
        newColor = '#f5f5f5';
    }
    $("[data-affect-dark-mode]").each(function () {
        let attribute = this.getAttribute("data-affect-dark-mode");
        if (attribute.includes("&")) {
            attribute.split("&").forEach((attr) => {
                this.style[attr] = newColor;
            });
        } else {
            this.style[attribute] = newColor;
        }
    });

}


if (localStorage.getItem("dark") === "true") {
    changeDarkMode(false)
}

// Take server preference if no preference is set
if (localStorage.getItem("dark") == null) {
    let darkmodeRequest = new XMLHttpRequest();
    darkmodeRequest.onreadystatechange = () => {
        if (darkmodeRequest.readyState === 4 && darkmodeRequest.status === 200) {
            // Checking localstorage again, if response took longer as user.
            if (JSON.parse(darkmodeRequest.responseText)['value'] === "true" && localStorage.getItem("dark") == null) {
                changeDarkMode(false);
            }
        }
    };
    darkmodeRequest.open("GET", "/api/setting/dark-mode-default");
    darkmodeRequest.send();
}