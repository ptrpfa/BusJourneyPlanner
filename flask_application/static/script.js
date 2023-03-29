// var map = L.map('map').fitWorld();
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
// attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);

document.addEventListener('DOMContentLoaded', () => {
    const showResultsBtn = document.getElementById('show-results-btn');
    const resultsList = document.getElementById('results');
    const map = document.getElementById('map');
    var dropdownMenu = $('.dropdown-menu');
    var dropdownButton = $('.dropdown-toggle');

    showResultsBtn.addEventListener('click', () => {
        submitForm();
    });

    dropdownMenu.on('click', 'a', function() {
        // Get the selected dropdown item's text
        var selectedText = $(this).text();
        // Set the dropdown button text to the selected text
        dropdownButton.text(selectedText);
    });

    document.addEventListener('click', (event) => {

    if (event.target !== map && !map.contains(event.target) && event.target.id !== 'show-results-btn') {
      // Clicked outside of map
      resultsList.classList.remove('show');
    }
    });
});

function submitForm() {
    // Get the input data from the form
    const destination = document.getElementById("destination").value;
    const start = document.getElementById("start-location").value;
    const resultsList = document.getElementById('results');
    var dropdownText = $('.dropdown-toggle').text();
    var dropdownValue = $('.dropdown-item.active').attr('value');

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

setInterval(function() {
    console.log("Updating markers...");
    $.ajax({
        url: "/update_markers",
        type: "GET",
        success: function(data) {
            $("#map").html(data);
        },
        error: function(xhr, status, error) {
            console.log("Error updating markers: " + error);
        }
    });
}, 15000);
