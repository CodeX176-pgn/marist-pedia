const healthButton = document.querySelector("#health-button");
const statusElement = document.querySelector("#status");


async function checkBackendHealth() {
    statusElement.textContent = "Checking backend...";

    try {
        const response = await fetch("/api/health");

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();

        statusElement.textContent = data.message;
    } catch (error) {
        console.error(error);

        statusElement.textContent =
            "Could not connect to the backend.";
    }
}


healthButton.addEventListener("click", checkBackendHealth);
