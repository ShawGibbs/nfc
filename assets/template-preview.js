const viewPicker = document.querySelector("#template-view");
const firmPicker = document.querySelector("#template-firm");
const cardBody = document.querySelector(".card-body");
const actions = cardBody.querySelector(".button-row");
const logo = document.querySelector(".firm-logo");
const layouts = [...viewPicker.options].map(option => option.value);

function updatePreview() {
    const view = viewPicker.value;
    const firm = firmPicker.selectedOptions[0];

    document.body.classList.remove(...layouts);
    document.body.classList.toggle("card-design", view !== "original");
    document.body.classList.add(view);

    if (view === "direct") {
        cardBody.prepend(actions);
    } else {
        cardBody.append(actions);
    }

    document.body.dataset.firm = firm.value;
    logo.src = firm.dataset.logo;
    logo.alt = firm.textContent;
}

viewPicker.addEventListener("change", updatePreview);
firmPicker.addEventListener("change", updatePreview);
window.addEventListener("pageshow", updatePreview);
