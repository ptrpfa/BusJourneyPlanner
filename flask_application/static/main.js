// var map = L.map('map').fitWorld();
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
// attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);

function submitForm() {
    // Get the input data from the form
    const inputData = document.getElementById("destination").value;
    console.log(inputData);
    // Send the data to the Flask server using AJAX
    $.ajax({
        url: "/process-data",
        type: "POST",
        data: { input_data: inputData },
        success: function (data) {
            // Update the target div with the processed data
            // $("#map").html(data);
            console.log(data);
        }

    });
}