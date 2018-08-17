var percentage = {
    tooltips: Array(),
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
        for (var i = 0; i < percentage.tooltips.length; i++) {
            var elements = Array.from(document.getElementsByClassName("contributions")).concat(Array.from(document.getElementsByClassName("selectedContributions")));
            var calc = Math.round((100 / percentage.selectedElement.innerHTML) * elements[i].innerHTML);
            var tooltip = percentage.tooltips[i].updateTitleContent(calc + "%")
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
        percentage.tooltips.push(
            new Tooltip(element, {
                placement: 'right',
                title: ""
            }));
    });
}