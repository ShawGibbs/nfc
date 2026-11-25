const portrait = document.querySelector(".profile-photo");

if (portrait) {
    const fallback = document.querySelector(".portrait-fallback");

    function revealPortrait() {
        portrait.hidden = false;
        fallback.hidden = true;
    }

    if (portrait.complete && portrait.naturalWidth) {
        revealPortrait();
    } else {
        portrait.addEventListener("load", revealPortrait, { once: true });
    }
}
