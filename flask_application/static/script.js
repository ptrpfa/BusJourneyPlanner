// var map = L.map('map').fitWorld();
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
// attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);

$(document).ready(function() {

    /* Refreshes and Creates Live Map*/
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
    var intervalID = setInterval(updateMarkers, 15000);

    //JS for UI
    const current_map = document.getElementById('map');
    const showResultsBtn = document.getElementById('show-results-btn');
    const resultsList = document.getElementById('results');
    var dropdownMenu = $('.dropdown-menu');
    var dropdownButton = $('.dropdown-toggle');
    var value = 1;


    showResultsBtn.addEventListener('click', () => {
        clearInterval(intervalID);
        submitForm(value);
    });

    dropdownMenu.on('click', 'a', function() {
        // Get the selected dropdown item's text
        var selectedText = $(this).text();
        var selectedValue = $(this).attr('value');
        // Set the dropdown button text to the selected text
        dropdownButton.text(selectedText);
    });

    $(".toggle-menu").click(function() {
        //result => left:-100%
        $("#results").toggleClass("show");

        if ($(this).hasClass("show")) {
            //menu => left:-100%
            $(this).toggleClass("show");
            //menu => left:0
            $(this).toggleClass("hide");
        } else {
            //menu => left:-100%
            $(this).toggleClass("hide");
            //menu => left:30%
            $(this).toggleClass("show");

        }
    });


});


function submitForm(value) {
    // Get the input data from the form
    const destination = document.getElementById("destination").value;
    const start = document.getElementById("start-location").value;
    //const resultsList = document.getElementById('results');
    var dropdownText = $('.dropdown-toggle').text();
    var dropdownValue = $('.dropdown-item').attr('value');
    var dropdownButton = $('.dropdown-toggle').attr('value');


    // Send the data to the Flask server using AJAX
    $.ajax({
        url: "/process-data",
        type: "POST",
        data: { Start: start, Destination: destination, Option: dropdownValue},
        success: function (data) {

            // Check for invalid inputs
            if(data.includes("ERROR")) {
                console.log(data);
                alert(data);
            }
            else{
                // Update the target div with the processed data
                $("#map").html(data);
                //result => left:0
                $('#results').toggleClass("show");
                if ($('.toggle-menu').hasClass("show")) {
                    //menu => left:-100%
                    $('.toggle-menu').removeClass("hide");
                    //menu => left:30%
                     $('.toggle-menu').toggleClass("show");
                } else {
                    //menu => left:-100%
                    $('.toggle-menu').removeClass("hide");
                    //menu => left:30%
                    $('.toggle-menu').toggleClass("show");
    
                }
            }
   
        },
        error: function (error) {
            console.log(error);
        }

    });
}




