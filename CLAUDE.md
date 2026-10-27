# How to work on HUM

HUM hears the power grid's frequency through a guitar pickup, shows how a
model of a Torus Station would respond, and decides with a controller
written in Mentl. It is a hackathon entry for two bounties, Torus and
Nucleus × Startup State, judged in person.

## Write in plain English

Most of what this repository holds is read or heard once, by people who
have never seen it: judges across a room, a sponsor reading a PDF, an
engineer opening the README. Write for them.

- Say who or what does what, and why it matters to the listener.
- Put one idea in each sentence. Prefer short sentences and common words.
- No slogans, no aphorisms, no inverted or poetic word order.
- Keep Mentl's and this project's internal words off anything a judge sees:
  no "first light", "fixed point", "row", "host call", "WASI", "the reflex"
  or "two bands". Say what happens instead: "the compiler won't build it",
  "it can't reach the internet while it decides".
- Give every number its unit and say what it measures.
- Reread each slide, caption and spoken line as someone hearing it once. If
  they could not repeat it back, rewrite it.

## Say only what is true

- The live hum and its frequency are real. The 9 August 2019 event is real
  data from Great Britain, transposed to 60 Hz and replayed. Say "replayed",
  never that anyone tripped a plant.
- The Station is a model built from Torus's published figures. Say "a model
  of Torus's Station", and label it simulated on every screen.
- "Proven" always names what is proven: the decision makes no network, file,
  clock or other host call, and allocates no memory. Do not claim more. The
  audit lists open claims, the program can trap, and the reading loop around
  the decision allocates memory.
- Measure a claim before writing it down. A number on a slide comes from a
  command you ran.

## Commits and secrets

- Every commit is authored by sonofagoose <sonofagoose@pm.me>. Never add a
  co-author line or credit an AI model.
- The EIA API key never enters the repository or a chat. The presenter sets
  `EIA_API_KEY` in their own shell.
- Recordings stay out of git except `samples/*.wav`.

## Where things are

- `README.md`: what HUM is and how to run it.
- `CONTRACTS.md`: the line formats between the ear, the director, the
  controller and the page.
- `ear/`: the Rust program that reads the hum, built on sonido.
- `director.py`: runs the ear and the controller, serves the page, records
  sessions. `record.py` records the bundled session.
- `index.html`: the page. `sessions/default.ndjson` plays when no director
  answers.
- `pitch/`: the decks, the one-page plan, the script and the captured
  compiler output. After `record.py`, `node pitch/shots.js` retakes the
  slide pictures from the bundled session and `node pitch/export.js`
  rewrites the PDFs.
- The controller lives in the Mentl repository under `examples/grid/`.
