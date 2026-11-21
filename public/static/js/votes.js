
async function readAjaxResponse(response) {
    const contentType = response.headers.get("Content-Type") || "";

    if (!contentType.includes("application/json")) {
        throw new Error(
            `Ошибка HTTP ${response.status}: сервер вернул не JSON`
        );
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || `Ошибка HTTP ${response.status}`
        );
    }

    return data;
}

const voteBlocks = document.querySelectorAll("[data-vote-url]");

voteBlocks.forEach(function (block) {
    const likeArrow = block.querySelector(".like-arrow");
    const dislikeArrow = block.querySelector(".dislike-arrow");
    const ratingBlock = block.querySelector(".rating");

    async function sendVote(value) {
        try {
            const response = await fetch(block.dataset.voteUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": block.dataset.csrfToken
                },
                body: new URLSearchParams({
                    value: String(value)
                })
            });

            const data = await readAjaxResponse(response);

            ratingBlock.querySelector(".rating-value").textContent = data.rating;

            ratingBlock.classList.toggle(
                "rating-liked", data.user_vote === 1
            );

            ratingBlock.classList.toggle(
                "rating-disliked", data.user_vote === -1
            );
            } 
        catch (error) {
            alert(error.message);
            console.error("Ошибка запроса:", error);
        }
    }

    likeArrow.addEventListener("click", function () {
        sendVote(1);
    });

    dislikeArrow.addEventListener("click", function () {
        sendVote(-1);
    });
});


const correctCheckboxes = document.querySelectorAll(
    "[data-correct-url]:not(:disabled)"
);


correctCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", async function () {
        const previousChecked = !checkbox.checked;

        correctCheckboxes.forEach(function (item) {
            item.disabled = true;
        });

        try {
            const response = await fetch(checkbox.dataset.correctUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": checkbox.dataset.csrfToken
                },
                body: new URLSearchParams({
                    question_id: checkbox.dataset.questionId
                })
            });

            const data = await readAjaxResponse(response);

            if (data.is_correct) {
                correctCheckboxes.forEach(function (item) {
                    item.checked = item === checkbox;
                });
            } else {
                checkbox.checked = false;
            }

        } 
        catch (error) {
            checkbox.checked = previousChecked;
            alert(error.message);
            console.error("Ошибка запроса:", error);
        } 
        finally {
            correctCheckboxes.forEach(function (item) {
                item.disabled = false;
            });
        }
    });
});
