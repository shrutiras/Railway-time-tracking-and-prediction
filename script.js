document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("trainForm");
    const trainDataDiv = document.getElementById("trainData");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Get input values
        const trainNumber = document.getElementById("trainNumber").value.trim();
        const trainName = document.getElementById("trainName").value.trim();

        // Clear previous results
        trainDataDiv.innerHTML = "";

        // Validate input
        if (!trainNumber && !trainName) {
            alert("Please enter either a Train Number or Train Name.");
            return;
        }

        try {
            // Choose API based on input
            let apiUrl;
            if (trainNumber) {
                apiUrl = `https://api.example.com/trains/number/${trainNumber}`;
            } else {
                apiUrl = `https://api.example.com/trains/name/${trainName}`;
            }

            // Fetch train data
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error("Train not found or API error.");
            }
            const trainData = await response.json();

            // Display train data
            displayTrainData(trainData);
        } catch (error) {
            trainDataDiv.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    function displayTrainData(data) {
        // Create HTML for train data
        let html = `
            <h3>Train Details</h3>
            <table class="table table-bordered mt-3">
                <thead>
                    <tr>
                        <th>Station</th>
                        <th>Arrival Time</th>
                        <th>Departure Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // Populate rows with train data
        data.stations.forEach(station => {
            html += `
                <tr>
                    <td>${station.name}</td>
                    <td>${station.arrival}</td>
                    <td>${station.departure}</td>
                    <td>${station.status}</td>
                </tr>
            `;
        });

        html += `</tbody></table>`;
        trainDataDiv.innerHTML = html;
    }
});
