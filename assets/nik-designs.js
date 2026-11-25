const portrait = document.querySelector(".profile-photo");

function revealPortrait() {
    portrait.hidden = false;
    document.querySelector(".portrait-fallback").hidden = true;
}

if (portrait.complete && portrait.naturalWidth) {
    revealPortrait();
} else {
    portrait.addEventListener("load", revealPortrait, { once: true });
}
