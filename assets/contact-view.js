const views = ["editorial", "split", "signature", "direct"];
const view = new URLSearchParams(location.search).get("view");

if (views.includes(view)) {
    document.body.classList.add("nik-design", view);

    const card = document.querySelector("main.card");
    const frame = document.createElement("div");
    frame.className = "design-frame";
    card.before(frame);
    frame.append(card);

    if (view === "direct") {
        const body = card.querySelector(".card-body");
        body.prepend(body.querySelector(".button-row"));
    }

    card.querySelector(".portrait-fallback").hidden = false;
}
