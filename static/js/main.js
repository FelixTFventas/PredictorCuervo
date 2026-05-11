const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");

if (navToggle && nav) {
    navToggle.addEventListener("click", () => {
        nav.classList.toggle("open");
    });
}

const playerModal = document.querySelector("[data-player-modal]");
const playerTriggers = document.querySelectorAll("[data-player-name]");

if (playerModal && playerTriggers.length) {
    const avatarSlot = playerModal.querySelector("[data-player-card-avatar]");
    const nameSlot = playerModal.querySelector("[data-player-card-name]");
    const usernameSlot = playerModal.querySelector("[data-player-card-username]");
    const positionSlot = playerModal.querySelector("[data-player-card-position]");
    const pointsSlot = playerModal.querySelector("[data-player-card-points]");
    const predictionsSlot = playerModal.querySelector("[data-player-card-predictions]");
    const exactsSlot = playerModal.querySelector("[data-player-card-exacts]");
    const rateSlot = playerModal.querySelector("[data-player-card-rate]");
    const closeButtons = playerModal.querySelectorAll("[data-player-modal-close]");

    const closePlayerModal = () => {
        playerModal.hidden = true;
        document.body.classList.remove("modal-open");
    };

    const openPlayerModal = (trigger) => {
        const data = trigger.dataset;
        avatarSlot.replaceChildren();
        if (data.playerAvatar) {
            const image = document.createElement("img");
            image.src = data.playerAvatar;
            image.alt = `Avatar de ${data.playerName}`;
            avatarSlot.appendChild(image);
        } else {
            const initials = document.createElement("span");
            initials.textContent = data.playerInitials;
            avatarSlot.appendChild(initials);
        }

        nameSlot.textContent = data.playerName;
        usernameSlot.textContent = data.playerUsername;
        positionSlot.textContent = data.playerPosition;
        pointsSlot.textContent = data.playerPoints;
        predictionsSlot.textContent = data.playerPredictions;
        exactsSlot.textContent = data.playerExacts;
        rateSlot.textContent = data.playerRate;
        playerModal.hidden = false;
        document.body.classList.add("modal-open");
    };

    playerTriggers.forEach((trigger) => {
        trigger.addEventListener("click", () => openPlayerModal(trigger));
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closePlayerModal);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !playerModal.hidden) {
            closePlayerModal();
        }
    });
}
