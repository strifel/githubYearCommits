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
        percentage.selectedElement.className = "selectedContributions";
        var elements = Array.from(document.getElementsByClassName("contributions"));
        for (var i = 0; i < elements.length; i++) {
            var calc = Math.round((100 / percentage.selectedElement.innerHTML) * elements[i].innerHTML);
            var tooltip = elements[i].tooltip.updateTitleContent(calc + "%")
        }
    }
};

function onLoad() {
    var elements = Array.from(document.getElementsByClassName("contributions"));
    elements.forEach(function (element) {
        element.onclick = function () {
            percentage.unselectElement();
            percentage.selectElement(element);
        };

        element.tooltip = new Tooltip(element, {
            placement: 'right',
            title: ""
        });
    });
}