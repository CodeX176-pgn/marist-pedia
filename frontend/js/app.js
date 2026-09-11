/*
 * Marist Pedia desktop application controller.
 *
 * This file controls which major screen is currently visible.
 * The detailed Server and Client functionality will be added
 * in later development steps.
 */


// Get the major application screens.
const starterScreen = document.querySelector("#starter-screen");
const serverScreen = document.querySelector("#server-screen");
const clientScreen = document.querySelector("#client-screen");


// Get the role-selection buttons.
const serverModeButton = document.querySelector("#server-mode-btn");
const clientModeButton = document.querySelector("#client-mode-btn");


// Get the Back buttons.
const serverBackButton = document.querySelector("#server-back-btn");
const clientBackButton = document.querySelector("#client-back-btn");


/**
 * Show one application screen and hide the others.
 *
 * @param {HTMLElement} screenToShow - The screen to display.
 */
function showScreen(screenToShow) {

    // Hide every major screen first.
    starterScreen.classList.add("hidden");
    serverScreen.classList.add("hidden");
    clientScreen.classList.add("hidden");

    // Show the requested screen.
    screenToShow.classList.remove("hidden");
}


/**
 * Open Server mode.
 */
function openServerMode() {

    console.log("Opening Server mode.");

    showScreen(serverScreen);
}


/**
 * Open Client mode.
 */
function openClientMode() {

    console.log("Opening Client mode.");

    showScreen(clientScreen);
}


/**
 * Return to the starter screen from Server mode.
 */
function leaveServerMode() {

    showScreen(starterScreen);
}


/**
 * Return to the starter screen from Client mode.
 */
function leaveClientMode() {

    showScreen(starterScreen);
}


/*
 * Connect buttons to their actions.
 */
serverModeButton.addEventListener(
    "click",
    openServerMode,
);

clientModeButton.addEventListener(
    "click",
    openClientMode,
);

serverBackButton.addEventListener(
    "click",
    leaveServerMode,
);

clientBackButton.addEventListener(
    "click",
    leaveClientMode,
);


/*
 * Start the application on the starter screen.
 */
showScreen(starterScreen);
