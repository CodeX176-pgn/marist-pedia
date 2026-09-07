import { getHealth, getQuizzes } from "./api.js";

import {
    setLoading,
    showError,
    renderQuizCard,
} from "./ui.js";

const quizList = document.querySelector("#quiz-list");
const getStartedButton =
    document.querySelector("#get-started-btn");

async function initializeApp() {
    try {
        await getHealth();
        console.log("Connected to Marist Pedia backend.");

        await loadQuizzes();
    } catch (error) {
        console.error(
            "Failed to initialize application:",
            error
        );

        showError(
            quizList,
            "Unable to connect to the Marist Pedia server."
        );
    }
}

async function loadQuizzes() {
    setLoading(quizList, "Loading quizzes...");

    try {
        const quizzes = await getQuizzes();

        renderQuizzes(quizzes);
    } catch (error) {
        console.error("Failed to load quizzes:", error);

        showError(
            quizList,
            error.message
        );
    }
}

function renderQuizzes(quizzes) {
    quizList.innerHTML = "";

    if (!Array.isArray(quizzes) || quizzes.length === 0) {
        quizList.innerHTML = `
            <div class="empty-state">
                <h3>No quizzes yet</h3>
                <p>
                    Upload a document to create your first quiz.
                </p>
            </div>
        `;

        return;
    }

    for (const quiz of quizzes) {
        const card = renderQuizCard(quiz);
        quizList.appendChild(card);
    }
}

getStartedButton.addEventListener("click", () => {
    document
        .querySelector("#quizzes")
        .scrollIntoView({
            behavior: "smooth",
        });
});

initializeApp();
