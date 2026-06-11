document.querySelectorAll(".prediction-form input").forEach((input) => {
    input.addEventListener("input", () => {
        if (Number(input.value) < 0) {
            input.value = 0;
        }
    });
});

document.querySelectorAll(".prediction-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = form.querySelector("button[type='submit']");
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = "Guardando...";

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "No se pudo guardar.");
            }

            const card = form.closest(".match-card");
            const predictionStrip = card.querySelector(".prediction-strip:not(.muted-strip)");
            if (predictionStrip && data.prediction) {
                predictionStrip.textContent = `Tu prediccion: ${data.prediction.home_score} - ${data.prediction.away_score} · ${data.prediction.points} pts`;
            }
        } catch (error) {
            alert(error.message);
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    });
});
