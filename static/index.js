var percentage = {
    selectedElement: null,
    unselectElement: function () {
        if (percentage.selectedElement !== null) {
            percentage.selectedElement.className = "contributions";
            percentage.selectedElement = null;
        }
    },
    selectElement: function (element) {
        percentage.selectedElement = element;
        percentage.selectedElement.className = "selectedContributions"
    }
};

function onLoad() {
    var elements = document.getElementsByClassName("contributions");
    elements.forEach(function (element) {
        element.onclick = function () {
            percentage.unselectElement();
            percentage.selectElement(element);
        }
    });
}