// Arrow keys, space and click move between slides; the deck scales to the window;
// `?print` shows every slide stacked for export. A window taller than it is wide,
// such as a phone held upright, stacks each slide in one column 1080 wide; a
// short, wide one, such as a phone held sideways, drops the footers. In both the
// slide is as tall as its content, and the scale fits all of it in the window.
(() => {
  const slides = Array.from(document.querySelectorAll(".slide"));
  let i = Math.max(0, Math.min(slides.length - 1, parseInt(location.hash.slice(1) || "0", 10) || 0));
  const nav = document.createElement("div"); nav.className = "nav"; document.body.appendChild(nav);
  // Shown inside the live page's frame (`?embed`), the deck hides its own navigation label.
  if (location.search.includes("embed")) nav.style.display = "none";
  function show(n) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, k) => s.classList.toggle("current", k === i));
    nav.textContent = (i + 1) + " / " + slides.length + "  ·  ← → space  ·  the appendix follows slide " + document.querySelectorAll(".slide:not(.appendix)").length;
    history.replaceState(null, "", "#" + i);
    fit();
  }
  function fit() {
    const deck = document.querySelector(".deck"), W = window.innerWidth, H = window.innerHeight; if (!deck || !W || !H) return;
    const tall = W / H < 0.85, short = !tall && H < 560 && W / H > 1.25, root = document.documentElement;
    root.classList.toggle("tall", tall); root.classList.toggle("short", short);
    slides.forEach(s => { s.style.minHeight = ""; });
    if (!tall && !short) { deck.style.width = deck.style.height = ""; deck.style.transform = "scale(" + Math.min(W / 1920, H / 1080) + ")"; return; }
    const DW = tall ? 1080 : 1920, cur = slides[i];
    deck.style.width = DW + "px"; deck.style.height = "auto";
    cur.style.minHeight = Math.round(DW * H / W) + "px";
    const DH = cur.offsetHeight; deck.style.height = DH + "px";
    deck.style.transform = "scale(" + Math.min(W / DW, H / DH) + ")";
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
  show(i);
  if (document.fonts) document.fonts.ready.then(fit);
  window.addEventListener("load", fit);
})();
