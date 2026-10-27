# The two pitches

Each slot runs 8 to 25 minutes including questions, depending on how many teams took the bounty (6 teams: 8 minutes, 4: 12, 3: 16, 2: 25). Each pitch below takes about four and a half minutes, so questions get the rest. Ask Tyler for the team counts on Wednesday morning.

**Before the first word, in both rooms.** The page is up in kiosk mode and the number is moving. The guitar is plugged in, with the gain at the rehearsed mark. The pedal is on the floor if it is flashed and working. The speaker is at a quarter. Press `0` to reset. Hands off the keyboard until the first beat.

**The keys.** `H` sets the clock to tomorrow's noon and back. `E` replays the 2019 event. `I` cuts the hum and brings it back. `P` shows the proof card, `R` the refused card, `K` the thank-you card. `Esc` closes a card, `D` switches to the engineers' dashboard. On the pedal, if flashed: footswitch 1 is `E`, footswitch 2 is `I`, toggle 1 down is tomorrow's noon.

**What to say, and what not to.** Say "a model of Torus's Station", never "the Station" alone. Say "replayed", never that anyone tripped a plant. Say "can't reach the internet while it decides", never "proven" alone. Never say a function name, "WASI", "row" or "first light".

## Torus: no slides, about four and a half minutes

| Time | Do | On screen | Say |
| --- | --- | --- | --- |
| 0:00 | Touch the cable tip, then plug in the guitar. | The number and sonido's tuner. | "That buzz is the power grid. Every wire in this room carries it. This is my audio library's tuner listening to the wall: sixty hertz, the note B. The whole Western grid, from Alberta to Baja, hums this one note." |
| 0:45 | Nothing. | The tuner holding steady. | "Your brief asks for software that knows when the grid is jammed and stays out of traffic. The grid jams in two ways." |
| 1:00 | `H` | Tomorrow 12:30 PM. The battery lights up. | "The first you can see coming. This is tomorrow at noon, from EIA's data for PacifiCorp East: rush hour. A model of your Station runs the building on its battery, three hundred kilowatts kept off the grid, and recharges when the power is clean." Then `H` again. |
| 1:45 | `E`, or footswitch 1 | REPLAY. The number falls, the needle swings flat, the flywheel lights. | "The second you can only hear. On the ninth of August 2019, two power plants in Britain tripped within a second. This is that day's real frequency, replayed at our grid's pitch. Watch the tuner." When the flywheel lights: "The flywheel answered in under a millisecond. Software reading hourly data would still be waiting for the next hour." |
| 2:40 | `I`, or footswitch 2 | THE HUM IS CUT. "The grid went dark. The building is still on." | "That evening in Britain, a million people lost power. When the grid goes dark here, the building stays on. That is the two-way Station you described on Monday." Then `I` again. |
| 3:05 | `P` | Proven. | "One more thing for your engineers. The software making these decisions can't reach the internet while it decides. That isn't a policy. The compiler proves it." |
| 3:25 | `R` | Refused. | "Watch me break it. One line that reads a price online, and the compiler won't build the program. I built that compiler. It's called Mentl." |
| 3:50 | `K` | Thank you, Torus. The QR code. | "This explains a Station to anyone in thirty seconds. I'd love to bring it to a Torus event, and to show your engineers the proof underneath. The code replays this demo on your phone." Stop. |

**If the slot allows.** Hand Nicole the pedal before `E`: "Step on this. It replays the second those plants tripped." Or play `samples/event_gb.wav` through the speaker during the replay: "That is the sound of the grid going flat, rendered from the 2019 record."

## Nucleus: five slides around the demo, about five minutes

| Time | Do | On screen | Say |
| --- | --- | --- | --- |
| 0:00 | Touch the cable, plug in the guitar. | The live page. | "That buzz is the power grid, and this number is its frequency, measured from this room's wiring." |
| 0:15 | Slide 1 | The problem. | "AI now helps write the software that runs machines: batteries, flywheels, flight controls. No mainstream language can prove what that software will never do. So it is tested, reviewed, and then trusted." |
| 0:45 | Slide 2 | Mentl. | "I built a language whose compiler proves it. You write a promise into the code, like 'this never touches the internet'. The compiler checks it through every function the code calls. Break the promise, and the program won't build. Seven months, twenty-six hundred commits, and the compiler is written in its own language." |
| 1:30 | Back to the page, `E` | The replay; the flywheel lights. | "This week I pointed it at the grid. This is a model of a Torus Station: a flywheel for the milliseconds, a battery for the hours. Here is a real 2019 grid failure, replayed. The decision you just watched was made by software written in Mentl, in under a millisecond." |
| 2:10 | `R` | Refused. | "Say an AI assistant suggests one line that checks electricity prices online, inside that decision. The compiler refuses to build it." Then `Esc`. |
| 2:30 | Slide 3 | Built this week. | "Everything on this slide was built since Monday at four. The language and my audio library existed before. The ledger in the repository prints every commit with its time." |
| 3:00 | Slide 4 | Who needs it in Utah. | "Torus, here in Salt Lake: the software inside each Station is the first place a proof pays, and their judge is seeing this demo today. And Hill Air Force Base's 309th, which maintains flight software for the F-16, the F-35 and the missile fleet." |
| 3:40 | Slide 5 | What $10,000 unlocks. | "Ten thousand dollars puts a proven controller on a real machine in Utah within ninety days. Day thirty, I form the company and run it on a battery inverter on my bench. Day sixty, beside a real battery at one Utah site. Day ninety, a pilot agreement, and an SBIR proposal with Nucleus Grow. Two asks this room can answer: a Utah operator who will host it, and an introduction to the 309th." |
| 4:30 | Stay on slide 5. | | "I've built the language since March and the audio library since January, and I'll keep going in November either way. Your bounty decides whether the first real machine is a battery in Utah or my bench. And if you know someone who knows power electronics, that's the co-founder I need." Stop. |

## Questions, and the answers

- **Isn't 60 Hz between A sharp and B?** With A at 440 Hz, yes. I set the tuner's A to 427.65 Hz so that the grid sits exactly on B. The needle then centers while the grid is in tune and swings flat when it sags.
- **Is the guitar accurate?** On a test signal it reads within half a thousandth of a hertz. Live, the reading is calibrated against the grid's long-run average of exactly sixty, and the offset is printed on the dashboard.
- **Doesn't a Torus Station already measure the grid?** Yes, every cycle, and better than a guitar. The guitar is how a room hears it. What's new is the proof underneath the decisions.
- **Is the Station real?** It's a model built from Torus's published figures: 100 kW from the flywheel for six minutes, 300 kW from the battery for four hours. Every screen says it's simulated.
- **Is the proof real?** In a terminal: `mentl check examples/grid/station-leak.mn` refuses the price lookup, and `mentl why examples/grid/station.mn decide WASI` answers that the decision makes no host call. `D` then `Shift+P` shows the full list.
- **What exactly is proven?** That the decision makes no network, file, clock or other host call, and allocates no memory, through every function it calls. The power limits are clamped in code, and the compiler lists the claims it could not settle. It does not prove the program never crashes, or that its decisions are good. The backup slide has the table.
- **Why a new language instead of Rust?** Rust stops memory bugs. It can't say "this function never reaches the network" and check it through every call.
- **Can it run on the pedal?** Not yet. The controller is a 37 KB WebAssembly file, and the pedal's chip has no engine for it. The loop around the decision also keeps 8 KB per reading. Both are on the day-30 list, and the backup slide shows the measurements.
- **Why is rush hour at noon?** PacifiCorp East's data this week says so: offices and factories peak midday in October. The evening jam comes when the sun leaves.
- **Where is price?** In the hour's plan, read before the fast decision. A price lookup inside the fast decision is the line the compiler refuses.
- **Are you incorporated?** Not yet. The brief doesn't require it. Forming a Utah company is day one, because the federal grant registrations need it and take weeks.
- **Who is the first customer?** [[the one person who has said "put this at my site"; ask before Wednesday at 5 PM]]. Until then, the day-60 site is the pilot, and Torus is the one I want.
- **What's the business?** Paid pilots with operators of batteries and flywheels first. The same compiler, as a check that AI-written code must pass, second. SBIR grants fund the safety-critical work in between.
- **Who is on the team?** One founder. The first hires are a controls engineer and a compiler engineer in Salt Lake City, and the co-founder I need knows power electronics.
- **What if the live hum fails?** `./run.sh wav` plays a recording made in this room, and the page says RECORDING.

## Still to fill

`[[name]]` and the one line about you on the one-page plan; the first customer's name if anyone says yes; the photo of the guitar on the interface as `pitch/img/guitar.jpg` if you want it on a slide.
