// var map = L.map('map').fitWorld();
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
// attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);

document.addEventListener('DOMContentLoaded', () => {
  const showResultsBtn = document.getElementById('show-results-btn');
  const resultsList = document.getElementById('results');
  const map = document.getElementById('map');

  showResultsBtn.addEventListener('click', () => {
    resultsList.classList.toggle('show');
    submitForm();
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
    // Send the data to the Flask server using AJAX
    $.ajax({
        url: "/process-data",
        type: "POST",
        data: { Start: start, Destination: destination  },
        success: function (data) {
            // Update the target div with the processed data
            $("#map").html(data);
        },
        error: function (error) {
            console.log(error);
        }

    });
}

