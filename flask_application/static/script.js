// var map = L.map('map').fitWorld();
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
// attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);

document.addEventListener('DOMContentLoaded', () => {
    const current_map = document.getElementById('map');
    const showResultsBtn = document.getElementById('show-results-btn');
    const resultsList = document.getElementById('results');
    var dropdownMenu = $('.dropdown-menu');
    var dropdownButton = $('.dropdown-toggle');
    var value;
    showResultsBtn.addEventListener('click', () => {
        clearInterval(intervalID);
        submitForm();
    });

    dropdownMenu.on('click', 'a', function() {
        // Get the selected dropdown item's text
        var selectedText = $(this).text();
        var selectedValue = $(this).attr('value');
        // Set the dropdown button text to the selected text
        dropdownButton.text(selectedText);
        console.log(selectedValue)
    });

    document.addEventListener('click', (event) => {

    if (event.target !== current_map && !current_map.contains(event.target) && event.target.id !== 'show-results-btn') {
      // Clicked outside of map
      resultsList.classList.remove('show');
    }
    });


});

/* Refreshes Live Map*/

$(document).ready(function() {
    var map = L.map('map').setView([1.4964559999542668, 103.74374661113058], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);
    var featureGroup = L.featureGroup().addTo(map);
    updateMarkers();
    function updateMarkers() {
        $.ajax({
            url: '/update_map',
            type: 'GET',
            success: function(data) {
                var geoJsonData = JSON.parse(data);
                
                featureGroup.clearLayers();
                var newMarkers = L.geoJson(geoJsonData, {
                    pointToLayer: function(feature, latlng) {
                        var markerIcon = L.icon({
                            icon: feature.properties.icon.icon,
                            prefix: feature.properties.icon.prefix,
                            iconUrl: feature.properties.icon.iconUrl,
                            iconSize: feature.properties.icon.iconSize,
                            iconAnchor: feature.properties.icon.iconAnchor,
                            popupAnchor: feature.properties.icon.popupAnchor,
                            className: feature.properties.icon.className,
                            color: feature.properties.icon.color
                        });
                        var marker = L.marker(latlng, {
                            icon: markerIcon
                        });
                        marker.bindPopup(function(layer) {
                            return feature.properties.popup;
                        });
                        return marker;
                    }
                });
                featureGroup.addLayer(newMarkers);
            },
            error: function(xhr, status, error) {
                console.log('Error updating markers: ' + error);
            }
        });
    }

    // Call updateMarkers every 15 seconds
    setInterval(updateMarkers, 15000);
});


function submitForm() {
    // Get the input data from the form
    const destination = document.getElementById("destination").value;
    const start = document.getElementById("start-location").value;
    const resultsList = document.getElementById('results');
    var dropdownText = $('.dropdown-toggle').text();
    var dropdownValue = $('.dropdown-item').attr('value');
    var dropdownButton = $('.dropdown-toggle').attr('value');
    console.log(dropdownValue);
    // Send the data to the Flask server using AJAX
    $.ajax({
        url: "/process-data",
        type: "POST",
        data: { Start: start, Destination: destination, Option: dropdownValue},
        success: function (data) {
            // Update the target div with the processed data
            $("#map").html(data);
            resultsList.classList.toggle('show');

            //Change the dropdownButton text to the current in the menu
            $('.dropdown-toggle').text($('.dropdown-item.active').text());
        },
        error: function (error) {
            console.log(error);
        }

    });
}




