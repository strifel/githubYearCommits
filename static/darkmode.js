function changeDarkMode(userSet) {
    let button = document.getElementById("darkMode");
    if (button.innerText === "Dark Mode") { //Change to dark mode
        if (userSet) {
            localStorage.setItem("dark", "true");
        }
        button.innerText = "Light Mode";
        button.style.backgroundColor = "#f5f5f5";
        button.style.color = "#1D1F21";
        document.body.style.backgroundColor = "#1D1F21";
        const elements = document.getElementsByClassName("text");
        for (let i = 0; i < elements.length; i++) {
            elements[i].style.color = "#f5f5f5";
        }
    } else { //change to Light Mode
        if (userSet) {
            localStorage.setItem("dark", "false");
        }
        button.innerText = "Dark Mode";
        button.style.backgroundColor = "#1D1F21";
        button.style.color = "#f5f5f5";
        document.body.style.backgroundColor = "#f5f5f5";
        const elements = document.getElementsByClassName("text");
        for (let i = 0; i < elements.length; i++) {
            elements[i].style.color = "#1D1F21";
        }
    }
}

if (localStorage.getItem("dark") === "true") {
    changeDarkMode(false)
}

// Take server preference if no preference is set
if (localStorage.getItem("dark") == null) {
    let darkmodeRequest = new XMLHttpRequest();
    darkmodeRequest.onreadystatechange = () => {
        if  (darkmodeRequest.readyState === 4 && darkmodeRequest.status === 200) {
            // Checking localstorage again, if response took longer as user.
            if (JSON.parse(darkmodeRequest.responseText)['value'] === "true" && localStorage.getItem("dark") == null) {
                changeDarkMode(false);
            }
        }
    };
    darkmodeRequest.open("GET", "/api/setting/dark-mode-default");
    darkmodeRequest.send();
}