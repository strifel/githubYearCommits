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
    let themeColor;
    let oppositeColor;
    if (document.darkMode === true) {
        document.darkMode = false;
        if (userSet) {
            localStorage.setItem("dark", "false");
        }
        themeColor = '#1D1F21';
        oppositeColor = '#f5f5f5';
    } else {
        document.darkMode = true;
        if (userSet) {
            localStorage.setItem("dark", "true");
        }
        themeColor = '#f5f5f5';
        oppositeColor = '#1D1F21';
    }
    $("[data-affect-dark-mode]").each(function () {
        let attribute = this.getAttribute("data-affect-dark-mode");
        if (attribute.includes("&")) {
            attribute.split("&").forEach((attr) => {
                setModeForElement(this, attr, themeColor, oppositeColor, document.darkMode);
            });
        } else {
            setModeForElement(this, attribute, themeColor, oppositeColor, document.darkMode);
        }
    });

}

function setModeForElement(element, option, themeColor, oppositeColor, isDark) {
    if (option.startsWith('!')) {
        element.style[option.slice(1)] = oppositeColor;
    } else if (option.startsWith('?')) {
        if (isDark) {
            element.classList.add(option.slice(1))
        } else {
            element.classList.remove(option.slice(1))
        }
    } else {
        element.style[option] = themeColor;
    }
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