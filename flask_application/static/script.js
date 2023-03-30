// var map = L.map('map').fitWorld();
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
// attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);

document.addEventListener('DOMContentLoaded', () => {
    const map = document.getElementById('map');
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

    if (event.target !== map && !map.contains(event.target) && event.target.id !== 'show-results-btn') {
      // Clicked outside of map
      resultsList.classList.remove('show');
    }
    });

    var intervalID = setInterval( function() {
        $.ajax({
            url: "/update_markers",
            type: "GET",
            success: function(data) {
                //Remove Old
                $('#map').empty();
                //Get New
                $('#map').html(data);
            },
            error: function(xhr, status, error) {
                console.log("Error updating markers: " + error);
            }
        });
    }, 15000);

    /* Refreshes Live Map*/

    // initialize the map container
    // var leaflet_map = L.map('map');

    // // create a GeoJSON layer for the markers
    // // create an empty feature group
    // // var myFeatureGroup = L.featureGroup().addTo(leaflet_map);

    // // update the marker data every 15 seconds
    // var intervalID =setInterval(function() {
    //     console.log("Updating markers...");
    //     $.ajax({
    //         url: "/update_markers",
    //         type: "GET",
    //         success: function(data) {
    //             // clear the current markers on the map
    //             leaflet_map.eachLayer(function(layer) {
    //                 console.log(layer);
    //                   if (layer instanceof L.FeatureGroup && layer.options.name === 'Buses') {
    //                     leaflet_map.removeLayer(layer);
    //                     console.log("Removed");
    //                   }
    //             });
    //             // markerLayer.addData(JSON.parse(data));
    //             console.log("Update Successful")
    //         },
    //         error: function(xhr, status, error) {
    //             console.log("Error updating markers: " + error);
    //         }
    //     });
    // }, 15000);


    // var intervalID =setInterval(function() {
    //     console.log("Updating markers...");
    //     $.ajax({
    //         url: "/update_markers",
    //         type: "GET",
    //         success: function(data) {
    //             $('#map').html(data);
    //         },
    //         error: function(xhr, status, error) {
    //             console.log("Error updating markers: " + error);
    //         }
    //     });
    // }, 15000);
        // map_obj = map.children[0]._leaflet_map;
        // console.log('Map object:', map_obj);
        // map_obj.eachLayer(function(layer) {
        //         if (layer instanceof L.Marker) {
        //             map.removeLayer(layer);
        //         }
        // });

});

// window.onload = function() {
//     // Get the iframe element containing the folium map
//     var map2 = L.map('map_e088929ba3fb38e52bb8e680e17055d7');
//             map2.eachLayer(function(layer) {
//                 if (layer instanceof L.Marker) {
//                     map2.removeLayer(layer);
//                 }
//             });
        

// };
    
// window.onload = function() {
//     var map_el = document.getElementById('map').children[0];
//     if (map_el) {
//         var map_obj = map_el.children[0]._leaflet_map;
//         console.log('Map object:', map_obj);
//         var intervalID = setInterval(function() {
//             console.log("Updating markers...");
//             map_obj.eachLayer(function(layer) {
//                 if (layer instanceof L.Marker) {
//                     map_obj.removeLayer(layer);
//                 }
//             });
//             // Call the update_markers() function
//             update_markers();
//         }, 15000);
//     }
// };

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

/* Refreshes Live Map*/

// setInterval(function() {
//     console.log("Updating markers...");
//     $.ajax({
//         url: "/update_markers",
//         type: "GET",
//         success: function(data) {
//             var map = L.map('map');

//             // create a new GeoJSON layer with the updated marker data
//             var newLayer = L.geoJSON(JSON.parse(data));

//             // clear the current markers on the map
//             map.eachLayer(function(layer) {
//                 if (layer instanceof L.Marker) {
//                 map.removeLayer(layer);
//             }
//             });
//             // add the new markers to the map
//             newLayer.addTo(map);
//             console.log("Update Successful")
//         },
//         error: function(xhr, status, error) {
//             console.log("Error updating markers: " + error);
//         }
//     });
// }, 15000);


// make an AJAX request to get the initial marker data
// $.ajax({
//     url: "/update_markers",
//     type: "GET",
//     success: function(data) {
//         // update the GeoJSON layer with the initial marker data
//         markerLayer.clearLayers();
//         markerLayer.addData(JSON.parse(data));
//     },
//     error: function(xhr, status, error) {
//         console.log("Error updating markers: " + error);
//     }
// });


