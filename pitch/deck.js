// Arrow keys, space and click move between slides; the deck scales to the window;
// `?print` shows every slide stacked for export.
(() => {
  const slides = Array.from(document.querySelectorAll(".slide"));
  let i = Math.max(0, Math.min(slides.length - 1, parseInt(location.hash.slice(1) || "0", 10) || 0));
  const nav = document.createElement("div"); nav.className = "nav"; document.body.appendChild(nav);
  function show(n) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, k) => s.classList.toggle("current", k === i));
    nav.textContent = (i + 1) + " / " + slides.length + "  ·  ← → space  ·  the appendix follows slide " + document.querySelectorAll(".slide:not(.appendix)").length;
    history.replaceState(null, "", "#" + i);
  }
  function fit() {
    const deck = document.querySelector(".deck"); if (!deck) return;
    const s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    deck.style.transform = "scale(" + s + ")";
  }
  document.addEventListener("keydown", e => {
    if (["ArrowRight", " ", "PageDown"].includes(e.key)) { e.preventDefault(); show(i + 1); }
    else if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); show(i - 1); }
    else if (e.key === "Home") show(0);
    else if (e.key === "End") show(slides.length - 1);
  });
  document.addEventListener("click", e => { if (e.clientX > window.innerWidth / 2) show(i + 1); else show(i - 1); });
  window.addEventListener("resize", fit);
  window.addEventListener("hashchange", () => show(parseInt(location.hash.slice(1), 10) || 0));
  fit(); show(i);
})();
