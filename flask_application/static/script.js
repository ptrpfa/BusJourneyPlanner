
$(document).ready(function () {

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
            success: function (data) {
                var geoJsonData = JSON.parse(data);

                featureGroup.clearLayers();
                var newMarkers = L.geoJson(geoJsonData, {
                    pointToLayer: function (feature, latlng) {
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
                        marker.bindPopup(function (layer) {
                            return feature.properties.popup;
                        });
                        return marker;
                    }
                });
                featureGroup.addLayer(newMarkers);
            },
            error: function (xhr, status, error) {
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

    dropdownMenu.on('click', 'a', function () {
        // Get the selected dropdown item's text
        var selectedText = $(this).text();
        value = $(this).attr('value');
        // Set the dropdown button text to the selected text
        dropdownButton.text(selectedText);
    });


    $(".toggle-menu").click(function () {
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

    // Email global variable
    var overall_directions = "";


});

function email() {
    var emailInput = document.getElementById("email-input").value;
    var destination = document.getElementById("destination").value;
    var start = document.getElementById("start-location").value;
    var subject = "Directions from " + start + " to " + destination;
    if(emailInput.length > 0) {
        // Send the data to the Flask server using AJAX
        $.ajax({
            url: "/email",
            type: "POST",
            data: { Email: emailInput, Subject: subject, Message: overall_directions},
            success: function() {
                alert("Email sent to " + emailInput + "!");
            },
            error: function (error) {
                console.log(error);
            }
        });
        }
    else {
        alert("ERROR: No email entered!");
    }
    
}

function submitForm(value) {

    // Get the input data from the form
    const destination = document.getElementById("destination").value;
    const start = document.getElementById("start-location").value;
    const spinner = document.getElementById("loading-spinner");

    spinner.style.display = 'inline-block';
    // Send the data to the Flask server using AJAX
    $.ajax({
        url: "/process-data",
        type: "POST",
        data: { Start: start, Destination: destination, Option: value },
        success: function (data) {
            spinner.style.display = 'none';
            var map_html = data.map_html;
            var routes = data.routes;
            var duration = data.duration;
            var distance = data.distance;
            var bus = data.bus;
            var path_start_instructions = data.path_start_instructions;
            var path_end_instructions = data.path_end_instructions;
            var array_routes = []
            
            // Check for invalid inputs
            if (data.hasOwnProperty("error")) {
                console.log(data.error);
                alert(data.error);
            }

            else {
                // Update the target div with the processed data
                $("#map").html(map_html);

                // Clear results from any previous contents
                overall_directions = "";
                $("#results").html("");

                // Show Duration
                var newDuration = document.createElement('p')
                newDuration.innerHTML = '<div class="duration"><h4>Duration: '+ duration + '</br>' + 'Distance: '+ distance + 'km</h4></div>'
                $('#results').append(newDuration);
                overall_directions += newDuration.innerHTML;

                var parsedStartInstructions = "<button data-toggle=\"collapse\" data-target=\"#start_info\" class=\"btn btn-primary instruction\">📍 Directions to Bus Stop<\/button><div id=\"start_info\" class=\"collapse\"><p style=\"font-size:14px;\" >"+ path_start_instructions +"</p><\/div>"
                var parsedEndInstructions = "<button data-toggle=\"collapse\" data-target=\"#end_info\" class=\"btn btn-primary instruction\">🏁 Directions to Destination<\/button><div id=\"end_info\" class=\"collapse\"><p style=\"font-size:14px;\">"+ path_end_instructions +"</p><\/div>"

                // Show start walking route
                if(path_start_instructions.length > 0) {
                    var startingDirections = document.createElement('div');
                    startingDirections.innerHTML = '<div class="start_instructions" style="margin-left:10px;" >'+ parsedStartInstructions + '</div>' 
                    $('#results').append(startingDirections)
                    overall_directions += startingDirections.innerHTML;
                }

                // Add collapsible button for route
                var routeButton = "<button data-toggle=\"collapse\" style=\"margin:10px;\" data-target=\"#routeInfo\" class=\"btn btn-primary instruction\">🚍 Bus Routes<\/button>"
                $('#results').append(routeButton)
                
                // Show Bus route
                for (var i = 0; i < routes.length; i++) {
                    var newElement = document.createElement('div');
                    if(i > 0 && bus[i] != bus[i - 1]) {
                        newElement.innerHTML = '<div id="routeInfo" class="route collapse" style="margin-left:10px;"><h3>' + routes[i] + "</h3><p style=\"font-size:14px;\">" + "Bus Number: " + bus[i] + '<span style="color:blue"> (Change Bus!)</span></p></div>';;
                    }
                    else {
                        newElement.innerHTML = '<div id="routeInfo" class="route collapse" style="margin-left:10px;"><h3>' + routes[i] + "</h3><p style=\"font-size:14px;\">" + "Bus Number: " + bus[i] + '</p></div>';;
                    }
                    array_routes.push(newElement);
                }
                for (var i = 0; i < array_routes.length; i++) {
                    $('#results').append(array_routes[i]);
                    overall_directions += array_routes[i].innerHTML;
                }
                
                // Show end walking route
                if(path_end_instructions.length > 0) {
                    var endDirections = document.createElement('div');
                    endDirections.innerHTML = '<div class="end_instructions" style="margin-left:10px;">'+ parsedEndInstructions + '</div>' 
                    $('#results').append(endDirections)
                    overall_directions += endDirections.innerHTML;
                }

                // Add email button
                $('#results').append("<div class=\"form-group\" style=\"margin-top:20px; margin-left:10px;\"><label for=\"email-input\"><p style=\"color: green\">Save Planned Journey?</p><\/label><input class=\"form-control\" id=\"email-input\" type=\"text\" placeholder=\"Enter your email address\"\/><button type=\"button\" class=\"btn btn-secondary btn-sm\" style=\"margin-top:10px;\" onclick=\"email()\">📧 Send me a copy!</button><\/div>")

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




