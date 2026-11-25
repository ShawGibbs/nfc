const views = ["editorial", "split", "signature", "direct"];
const view = new URLSearchParams(location.search).get("view");
const card = document.querySelector("main.card");

if (views.includes(view)) {
    document.body.classList.add("nik-design", view);

    if (!card.parentElement.classList.contains("design-frame")) {
        const frame = document.createElement("div");
        frame.className = "design-frame";
        card.before(frame);
        frame.append(card);
    }

    const actions = card.querySelector(".button-row");
    if (view === "direct" && actions) {
        card.querySelector(".card-body").prepend(actions);
    }
}

const firmPicker = document.querySelector("#template-firm");
if (firmPicker) {
    const logo = card.querySelector(".firm-logo");

    function applyFirm() {
        const firm = firmPicker.selectedOptions[0];
        document.body.dataset.firm = firm.value;
        logo.src = firm.dataset.logo;
        logo.alt = firm.textContent;
    }

    firmPicker.addEventListener("change", applyFirm);
    window.addEventListener("pageshow", applyFirm);
}
