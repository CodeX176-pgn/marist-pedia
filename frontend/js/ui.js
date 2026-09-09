export function setLoading(element, message = "Loading...") {
    element.innerHTML = `
        <div class="loading-state" role="status" aria-live="polite">
            <div class="spinner" aria-hidden="true"></div>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}


export function showError(element, message) {
    element.innerHTML = `
        <div class="error-state" role="alert">
            <div class="error-icon" aria-hidden="true">!</div>
            <h3>Something went wrong</h3>
            <p>${escapeHtml(message)}</p>

            <button
                class="button button-primary"
                data-action="retry"
                type="button"
            >
                Try Again
            </button>
        </div>
    `;
}


export function renderQuizCard(quiz) {
    const card = document.createElement("article");

    card.className = "quiz-card";

    const questionCount = Number(
        quiz.question_count
    ) || 0;

    card.innerHTML = `
        <div class="quiz-card-top">
            <span
                class="quiz-card-icon"
                aria-hidden="true"
            >
                ✦
            </span>

            <span class="quiz-card-label">
                Available quiz
            </span>
        </div>

        <div class="quiz-card-content">
            <h3>
                ${escapeHtml(quiz.title)}
            </h3>

            <p>
                ${escapeHtml(
                    quiz.description ||
                    "Test your knowledge with this quiz."
                )}
            </p>
        </div>

        <div class="quiz-card-footer">
            <span class="quiz-card-meta">
                <span aria-hidden="true">◈</span>

                ${questionCount}
                ${questionCount === 1 ? "question" : "questions"}
            </span>

            <button
                class="button button-primary quiz-start-button"
                type="button"
                data-quiz-id="${escapeHtml(quiz.id)}"
                aria-label="Start ${escapeHtml(quiz.title)} quiz"
            >
                Start quiz
                <span aria-hidden="true">→</span>
            </button>
        </div>
    `;

    return card;
}


export function renderQuestion(
    question,
    questionNumber,
    totalQuestions,
    selectedAnswer,
) {
    const questionText = document.querySelector(
        "#question-text"
    );

    const answerOptions = document.querySelector(
        "#answer-options"
    );

    const progressBar = document.querySelector(
        "#quiz-progress-bar"
    );

    const difficulty = document.querySelector(
        "#question-difficulty"
    );

    questionText.textContent = question.text;

    difficulty.textContent = capitalize(
        question.difficulty || "medium"
    );

    difficulty.dataset.difficulty =
        question.difficulty || "medium";

    const percentage =
        (questionNumber / totalQuestions) * 100;

    progressBar.style.width =
        `${percentage}%`;

    progressBar.setAttribute(
        "aria-valuenow",
        String(Math.round(percentage)),
    );

    answerOptions.innerHTML = "";

    question.choices.forEach(
        (choice, index) => {
            const letter =
                String.fromCharCode(65 + index);

            const option =
                document.createElement("button");

            option.type = "button";
            option.className =
                "answer-option";

            option.dataset.answerId =
                choice.id;

            option.setAttribute(
                "role",
                "radio",
            );

            option.setAttribute(
                "aria-checked",
                String(
                    selectedAnswer === choice.id
                ),
            );

            option.setAttribute(
                "aria-label",
                `Option ${letter}: ${choice.text}`,
            );

            if (
                selectedAnswer === choice.id
            ) {
                option.classList.add(
                    "selected"
                );
            }

            option.innerHTML = `
                <span
                    class="answer-letter"
                    aria-hidden="true"
                >
                    ${letter}
                </span>

                <span class="answer-text">
                    ${escapeHtml(choice.text)}
                </span>

                <span
                    class="answer-check"
                    aria-hidden="true"
                >
                    ✓
                </span>
            `;

            answerOptions.appendChild(
                option
            );
        }
    );
}


export function renderQuestionNavigator(
    questions,
    currentIndex,
    answers,
) {
    const navigator = document.querySelector(
        "#question-navigator"
    );

    if (!navigator) return;

    navigator.innerHTML = "";

    questions.forEach(
        (question, index) => {
            const button =
                document.createElement("button");

            button.type = "button";
            button.className =
                "question-dot";

            button.dataset.questionIndex =
                String(index);

            button.textContent =
                String(index + 1);

            button.setAttribute(
                "aria-label",
                `Go to question ${index + 1}`,
            );

            button.setAttribute(
                "aria-current",
                index === currentIndex
                    ? "step"
                    : "false",
            );

            if (
                index === currentIndex
            ) {
                button.classList.add(
                    "current"
                );
            }

            if (
                answers[question.id]
            ) {
                button.classList.add(
                    "answered"
                );
            }

            navigator.appendChild(
                button
            );
        }
    );
}


export function renderResults(
    quiz,
    result,
) {
    const total =
        result?.total_questions ??
        quiz.questions.length;

    const score =
        result?.score ?? 0;

    const percentage =
        Math.round(
            result?.percentage ?? 0
        );

    document.querySelector(
        "#score-percentage"
    ).textContent =
        `${percentage}%`;

    document.querySelector(
        "#score-summary"
    ).textContent =
        `You answered ${score} out of ${total} questions correctly.`;

    const resultMessage =
        document.querySelector(
            "#result-message"
        );

    if (resultMessage) {
        resultMessage.textContent =
            getResultMessage(
                percentage
            );
    }

    const review =
        document.querySelector(
            "#results-review"
        );

    review.innerHTML = "";

    const results =
        Array.isArray(result?.results)
            ? result.results
            : [];

    const resultByQuestion =
        new Map(
            results.map(
                (item) => [
                    item.question_id,
                    item,
                ]
            )
        );

    quiz.questions.forEach(
        (question, index) => {
            const itemResult =
                resultByQuestion.get(
                    question.id
                );

            const item =
                document.createElement(
                    "article"
                );

            const isCorrect =
                Boolean(
                    itemResult?.is_correct
                );

            item.className =
                `result-item ${
                    isCorrect
                        ? "result-correct"
                        : "result-incorrect"
                }`;

            const selectedChoice =
                question.choices.find(
                    (choice) =>
                        choice.id ===
                        itemResult?.selected_answer
                );

            const correctChoice =
                question.choices.find(
                    (choice) =>
                        choice.id ===
                        itemResult?.correct_answer
                );

            item.innerHTML = `
                <div class="result-item-header">
                    <span class="result-number">
                        ${index + 1}
                    </span>

                    <span class="result-status">
                        ${
                            isCorrect
                                ? "Correct"
                                : "Review"
                        }
                    </span>
                </div>

                <h3>
                    ${escapeHtml(
                        question.text
                    )}
                </h3>

                <div class="result-answer-row">
                    <span>Your answer</span>

                    <strong>
                        ${escapeHtml(
                            selectedChoice?.text ||
                            "Not answered"
                        )}
                    </strong>
                </div>

                <div class="result-answer-row correct-answer-row">
                    <span>Correct answer</span>

                    <strong>
                        ${escapeHtml(
                            correctChoice?.text ||
                            itemResult?.correct_answer ||
                            "Unavailable"
                        )}
                    </strong>
                </div>

                ${
                    itemResult?.explanation
                        ? `
                            <div class="result-explanation">
                                <strong>Why?</strong>

                                <p>
                                    ${escapeHtml(
                                        itemResult.explanation
                                    )}
                                </p>
                            </div>
                        `
                        : ""
                }
            `;

            review.appendChild(
                item
            );
        }
    );
}


export function setButtonLoading(
    button,
    isLoading,
    loadingText = "Loading...",
) {
    if (!button) return;

    if (isLoading) {
        if (
            !button.dataset.originalText
        ) {
            button.dataset.originalText =
                button.innerHTML;
        }

        button.disabled = true;

        button.setAttribute(
            "aria-busy",
            "true",
        );

        button.innerHTML = `
            <span
                class="button-spinner"
                aria-hidden="true"
            ></span>

            ${escapeHtml(
                loadingText
            )}
        `;
    } else {
        button.disabled = false;

        button.removeAttribute(
            "aria-busy"
        );

        button.innerHTML =
            button.dataset.originalText ||
            button.innerHTML;

        delete button.dataset.originalText;
    }
}


export function show(element) {
    element.classList.remove(
        "hidden"
    );
}


export function hide(element) {
    element.classList.add(
        "hidden"
    );
}


export function escapeHtml(value) {
    return String(value)
        .replaceAll(
            "&",
            "&amp;",
        )
        .replaceAll(
            "<",
            "&lt;",
        )
        .replaceAll(
            ">",
            "&gt;",
        )
        .replaceAll(
            '"',
            "&quot;",
        )
        .replaceAll(
            "'",
            "&#039;",
        );
}


function capitalize(value) {
    const text =
        String(value);

    return (
        text.charAt(0).toUpperCase() +
        text.slice(1)
    );
}


function getResultMessage(
    percentage,
) {
    if (percentage === 100) {
        return "Perfect score. Excellent work!";
    }

    if (percentage >= 80) {
        return "Great job. You have a strong grasp of this material.";
    }

    if (percentage >= 60) {
        return "Good progress. Review the missed questions and try again.";
    }

    return "Keep going. A quick review can help you improve your next attempt.";
}