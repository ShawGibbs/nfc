const picker = document.querySelector("#card-view");
const contactLinks = [...document.querySelectorAll(".directory-list a, .template-link")].map(link => ({
    link,
    original: link.getAttribute("href")
}));

function updateContactLinks() {
    const view = picker.value;
    for (const { link, original } of contactLinks) {
        if (!view) {
            link.href = original;
        } else if (original === "nik/") {
            link.href = `${original}${view}/`;
        } else {
            link.href = `${original}?view=${view}`;
        }
    }
}

picker.addEventListener("change", updateContactLinks);
window.addEventListener("pageshow", updateContactLinks);
updateContactLinks();
document.querySelector("#view-picker").hidden = false;
