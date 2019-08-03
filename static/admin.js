// Script provides AJAX Connection for Admin Interface

// Settings
document.getElementById('setting').onchange = () => {
    let setting = document.getElementById('setting').value;
    if (setting !== 'placeholder') {
        let settingValueRequest = new XMLHttpRequest();
        settingValueRequest.onreadystatechange = () => {
            if (settingValueRequest.readyState === 4 && settingValueRequest.status === 200) {
                document.getElementById('settingValue').placeholder = JSON.parse(settingValueRequest.responseText)['value'];
            }
        };
        settingValueRequest.open('GET', '/backend/setting/' + setting);
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
            }
        };
        settingChangeRequest.open('PUT', '/backend/setting/' + setting);
        settingChangeRequest.setRequestHeader('Content-Type', 'application/json');
        settingChangeRequest.send(JSON.stringify({'value': value}))

    }
}