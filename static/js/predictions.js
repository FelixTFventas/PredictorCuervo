document.querySelectorAll(".prediction-form input").forEach((input) => {
    input.addEventListener("input", () => {
        if (Number(input.value) < 0) {
            input.value = 0;
        }
    });
});
