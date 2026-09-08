import {
    getHealth,
    getQuizzes,
    getQuiz,
    createQuizSession,
    submitAnswer,
    submitQuizSession,
} from "./api.js";

import {
    setLoading,
    showError,
    renderQuizCard,
    renderQuestion,
    renderQuestionNavigator,
    renderResults,
    setButtonLoading,
    show,
    hide,
} from "./ui.js";

const quizList = document.querySelector("#quiz-list");
const homeSection = document.querySelector("#home");
const quizzesSection = document.querySelector("#quizzes");
const quizScreen = document.querySelector("#quiz-screen");
const resultsScreen = document.querySelector("#results-screen");
const getStartedButton = document.querySelector("#get-started-btn");
const backToQuizzesButton = document.querySelector("#back-to-quizzes-btn");
const previousButton = document.querySelector("#previous-question-btn");
const nextButton = document.querySelector("#next-question-btn");
const submitButton = document.querySelector("#submit-quiz-btn");
const retryButton = document.querySelector("#retry-quiz-btn");
const resultsBackButton = document.querySelector("#results-back-btn");
const quizStatus = document.querySelector("#quiz-status");
const quizProgress = document.querySelector("#quiz-progress");

const state = {
    quizzes: [],
    currentQuiz: null,
    currentSession: null,
    currentQuestionIndex: 0,
    answers: {},
    answerRequests: new Map(),
    lastResult: null,
    startingQuiz: false,
    submittingQuiz: false,
};

async function initializeApp() {
    try {
        await getHealth();
        await loadQuizzes();
    } catch (error) {
        console.error("Failed to initialize application:", error);
        showError(quizList, error.message);
        quizList.setAttribute("aria-busy", "false");
    }
}

async function loadQuizzes() {
    setLoading(quizList, "Loading quizzes...");
    quizList.setAttribute("aria-busy", "true");

    try {
        const data = await getQuizzes();
        state.quizzes = Array.isArray(data) ? data : data?.quizzes || [];
        renderQuizzes();
    } catch (error) {
        console.error("Failed to load quizzes:", error);
        showError(quizList, error.message);
        quizList.setAttribute("aria-busy", "false");
    }
}

function renderQuizzes() {
    quizList.innerHTML = "";
    quizList.setAttribute("aria-busy", "false");

    if (state.quizzes.length === 0) {
        quizList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon" aria-hidden="true">✦</div>
                <h3>No quizzes yet</h3>
                <p>Generate a quiz from a study document to get started.</p>
            </div>
        `;
        return;
    }

    state.quizzes.forEach((quiz) => {
        quizList.appendChild(renderQuizCard(quiz));
    });
}

async function startQuiz(quizId, triggerButton = null) {
    if (state.startingQuiz || !quizId) return;

    state.startingQuiz = true;

    if (triggerButton) {
        setButtonLoading(triggerButton, true, "Opening...");
    }

    try {
        const quiz = await getQuiz(quizId);

        if (!quiz?.questions?.length) {
            throw new Error("This quiz does not contain any questions.");
        }

        const session = await createQuizSession(quiz.id);

        state.currentQuiz = quiz;
        state.currentSession = session;
        state.currentQuestionIndex = 0;
        state.answers = {};
        state.answerRequests = new Map();
        state.lastResult = null;

        showQuizScreen();
    } catch (error) {
        console.error("Failed to start quiz:", error);
        showInlineError(`Unable to open quiz: ${error.message}`);
    } finally {
        state.startingQuiz = false;
        if (triggerButton) {
            setButtonLoading(triggerButton, false);
        }
    }
}

function showInlineError(message) {
    window.alert(message);
}

function showQuizScreen() {
    hide(homeSection);
    hide(quizzesSection);
    hide(resultsScreen);
    show(quizScreen);

    document.querySelector("#quiz-title").textContent = state.currentQuiz.title;
    document.querySelector("#quiz-subtitle").textContent =
        `${state.currentQuiz.questions.length} questions · Take your time and choose the best answer.`;

    renderCurrentQuestion();
    window.scrollTo({ top: 0, behavior: "smooth" });
    focusQuestion();
}

function renderCurrentQuestion() {
    if (!state.currentQuiz) return;

    const questions = state.currentQuiz.questions;
    const index = state.currentQuestionIndex;
    const question = questions[index];
    const selectedAnswer = state.answers[question.id];

    renderQuestion(
        question,
        index + 1,
        questions.length,
        selectedAnswer,
    );
    renderQuestionNavigator(questions, index, state.answers);

    previousButton.disabled = index === 0;

    const isLastQuestion = index === questions.length - 1;
    if (isLastQuestion) {
        hide(nextButton);
        show(submitButton);
    } else {
        show(nextButton);
        hide(submitButton);
    }

    const answered = Object.keys(state.answers).length;
    quizStatus.textContent = `${answered} of ${questions.length} answered`;
    quizProgress.textContent = `Question ${index + 1} of ${questions.length}`;
}

function selectAnswer(answerId) {
    if (!state.currentQuiz || state.submittingQuiz) return;

    const question = state.currentQuiz.questions[state.currentQuestionIndex];
    if (!question.choices.some((choice) => choice.id === answerId)) return;

    state.answers[question.id] = answerId;
    renderCurrentQuestion();

    if (state.currentSession) {
        const request = submitAnswer(
            state.currentSession.id,
            question.id,
            answerId,
        ).catch((error) => {
            console.warn("Answer could not be saved immediately:", error);
        });

        state.answerRequests.set(question.id, request);
    }
}

function goToNextQuestion() {
    if (!state.currentQuiz) return;

    if (state.currentQuestionIndex < state.currentQuiz.questions.length - 1) {
        state.currentQuestionIndex += 1;
        renderCurrentQuestion();
        focusQuestion();
    }
}

function goToPreviousQuestion() {
    if (!state.currentQuiz) return;

    if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex -= 1;
        renderCurrentQuestion();
        focusQuestion();
    }
}

function goToQuestion(index) {
    if (!state.currentQuiz) return;

    if (index >= 0 && index < state.currentQuiz.questions.length) {
        state.currentQuestionIndex = index;
        renderCurrentQuestion();
        focusQuestion();
    }
}

async function finishQuiz() {
    if (!state.currentQuiz || !state.currentSession || state.submittingQuiz) {
        return;
    }

    const unanswered = state.currentQuiz.questions.filter(
        (question) => !state.answers[question.id],
    );

    if (unanswered.length > 0) {
        const shouldSubmit = window.confirm(
            `You have ${unanswered.length} unanswered question${unanswered.length === 1 ? "" : "s"}. Submit anyway?`,
        );
        if (!shouldSubmit) return;
    }

    state.submittingQuiz = true;

    try {
        setButtonLoading(submitButton, true, "Submitting...");
        quizStatus.textContent = "Saving your answers...";

        await Promise.all(state.answerRequests.values());

        // Re-sync every selected answer before final evaluation. The backend
        // treats repeated submissions for an active question as an update.
        await Promise.all(
            Object.entries(state.answers).map(([questionId, answerId]) =>
                submitAnswer(
                    state.currentSession.id,
                    questionId,
                    answerId,
                ),
            ),
        );

        const result = await submitQuizSession(state.currentSession.id);
        state.lastResult = result;
        showResults();
    } catch (error) {
        console.error("Failed to submit quiz:", error);
        showInlineError(`Unable to submit quiz: ${error.message}`);
        quizStatus.textContent =
            "Submission failed. Your answers are still on this screen.";
    } finally {
        state.submittingQuiz = false;
        setButtonLoading(submitButton, false);
    }
}

function showResults() {
    hide(homeSection);
    hide(quizzesSection);
    hide(quizScreen);
    show(resultsScreen);

    renderResults(state.currentQuiz, state.lastResult);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

async function restartQuiz() {
    if (!state.currentQuiz || state.startingQuiz) return;

    state.startingQuiz = true;
    setButtonLoading(retryButton, true, "Starting...");

    try {
        const session = await createQuizSession(state.currentQuiz.id);

        state.currentSession = session;
        state.currentQuestionIndex = 0;
        state.answers = {};
        state.answerRequests = new Map();
        state.lastResult = null;

        showQuizScreen();
    } catch (error) {
        console.error("Unable to restart quiz:", error);
        showInlineError(`Unable to restart quiz: ${error.message}`);
    } finally {
        state.startingQuiz = false;
        setButtonLoading(retryButton, false);
    }
}

function returnToQuizLibrary() {
    if (state.currentQuiz && Object.keys(state.answers).length > 0) {
        const leave = window.confirm(
            "Leave this quiz? Your current attempt will not be submitted.",
        );
        if (!leave) return;
    }

    resetQuizState();

    hide(quizScreen);
    hide(resultsScreen);
    show(homeSection);
    show(quizzesSection);

    document.querySelector("#quizzes").scrollIntoView({ behavior: "smooth" });
    loadQuizzes();
}

function resetQuizState() {
    state.currentQuiz = null;
    state.currentSession = null;
    state.currentQuestionIndex = 0;
    state.answers = {};
    state.answerRequests = new Map();
    state.lastResult = null;
    state.submittingQuiz = false;
}

function focusQuestion() {
    document.querySelector("#question-text")?.focus({ preventScroll: true });
}

getStartedButton.addEventListener("click", () => {
    quizzesSection.scrollIntoView({ behavior: "smooth" });
});

backToQuizzesButton.addEventListener("click", returnToQuizLibrary);
resultsBackButton.addEventListener("click", () => {
    resetQuizState();
    hide(resultsScreen);
    show(homeSection);
    show(quizzesSection);
    document.querySelector("#quizzes").scrollIntoView({ behavior: "smooth" });
    loadQuizzes();
});
retryButton.addEventListener("click", restartQuiz);
previousButton.addEventListener("click", goToPreviousQuestion);
nextButton.addEventListener("click", goToNextQuestion);
submitButton.addEventListener("click", finishQuiz);

document.addEventListener("keydown", (event) => {
    if (quizScreen.classList.contains("hidden") || !state.currentQuiz) return;
    if (event.ctrlKey || event.metaKey || event.altKey) return;

    const activeElement = document.activeElement;
    const isInteractive = activeElement?.matches(
        "button, a, input, textarea, select",
    );

    if (isInteractive) return;

    if (event.key === "ArrowRight") {
        event.preventDefault();
        goToNextQuestion();
    }

    if (event.key === "ArrowLeft") {
        event.preventDefault();
        goToPreviousQuestion();
    }
});

document.addEventListener("click", (event) => {
    const answerButton = event.target.closest(".answer-option");
    if (answerButton) {
        selectAnswer(answerButton.dataset.answerId);
        return;
    }

    const startButton = event.target.closest(".quiz-start-button");
    if (startButton) {
        startQuiz(startButton.dataset.quizId, startButton);
        return;
    }

    const questionButton = event.target.closest(".question-dot");
    if (questionButton) {
        goToQuestion(Number(questionButton.dataset.questionIndex));
        return;
    }

    const retryAction = event.target.closest('[data-action="retry"]');
    if (retryAction) {
        loadQuizzes();
    }
});

initializeApp();
