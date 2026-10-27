# The two pitches

The slot is 8 to 25 minutes including questions, set by how many teams took each bounty (6 teams: 8 min, 4: 12, 3: 16, 2: 25). Each pitch below is a five-minute core; the beats marked *optional* go in when the slot allows. Ask Tyler for the team counts on Wednesday morning and pick the options before the first rehearsal of the day.

**Before the first word, both rooms.** The page live and kiosk, the number moving. The guitar on its stand, cable in, gain at the rehearsed mark, never touched live. Bitwig on workspace 1 with the tuner on the live input and `samples/event_gb.wav` on a second track, cued. The small speaker at a quarter. Hands off the keyboard until the first beat.

**The rule of names.** The Torus room hears "the program that decides" until the certificate; "Mentl" is said once there. The Nucleus room hears "Mentl" in the first sentence.

## Torus, five minutes plus options

| Time | Tool | On screen | Say | The point |
| --- | --- | --- | --- | --- |
| 0:00 | guitar, speaker | the page, the number | Touch the cable tip: the buzz. "Every guitarist knows that sound. That buzz is the grid." Plug the guitar in; move it; the number holds. "It is not my number. It belongs to the whole Western Interconnection, Alberta to Baja, measured from this room's wiring." | creativity; execution; the ear |
| 0:40 | Bitwig | the tuner, fifteen seconds | "My tuner reads it as B1, forty-nine cents flat. Sixty hertz is a note, and the whole West plays it in tune to a cent." Workspace 2: "the same reading, to the millihertz." Never switch back. | the library is real; the note |
| 1:10 | page | RUSH HOUR | "Your brief says rush hour. Here is PacifiCorp East's this week, from EIA: noon to four, the offices and factories, not the evening. The sun leaves at six. A traffic report for tomorrow's grid. The Station plans this band: Pulse carries the building through the jam and refills in the clean hours. Price follows the jam, and the Station reads it in the hour's plan, never inside the reflex." | Option 1 in its own words; Pulse |
| 2:00 | page | `E`, the real event; the note flips | "Rush hour you can plan. This you can only hear. The ninth of August 2019, two plants trip in one second. Watch the number." Eight seconds of calm, then the fall; Spin fires; the reason reads. "Spin answered in a third of a second. Pulse never moved. The grid changed key, B to A sharp, and a million people lost power at that A sharp." *Optional, +15 s:* play the event WAV through the speaker: "that is the pitch of a blackout." | execution; Spin; new meaning |
| 3:00 | page | `I`, the hum dies | "Now the grid goes dark. The same ear knows first. The Station carries the building. That is the two-way story you told me Monday." `I` again. | relate to products; her words |
| 3:30 | page | `P`, then `R` | "The program that just decided can act on each reading and command two machines. It cannot reach the network, cannot touch the filesystem, cannot ask Spin for more than ten C. Not by policy: proven by the compiler through every call." `R`: "Here is a price read slipped into the reflex, the way an engineer would write it. The build refuses and names the path: decide, price_m, fetch_param, Network. Price belongs to the hour's plan, not the millisecond's reflex; that is the bug the compiler refuses. The layer under Lasso." *Optional, +15 s, for an engineer:* the reflex curve on the Station panel: "Spin's reflex is a compressor on the grid's pitch: the deadband is the threshold, droop is the ratio, ten C is the ceiling, and it holds two seconds so the word never flickers." | the proof; Lasso; new meaning |
| 4:30 | slide 5 | the ask | "Five thousand dollars buys a second ear and a GPS clock. Two ears are a stereo pair, and the correlation meter's angle is the flow between two Salt Lake sites. I bring that measurement to your engineers." Stop. | the ask |

Questions: `M` for the mesh (simulated, say so), `T` for the raw lines, `G` for the gate, and the terminal for `mentl check examples/grid/station-leak.mn` live if anyone asks whether the refusal is real.

## Nucleus, five minutes plus options

| Time | Tool | On screen | Say | The point |
| --- | --- | --- | --- | --- |
| 0:00 | slide 1 | the problem | "Software that steers physical things is tested and hoped on. Nobody can prove a controller will never reach the network while it steers a seven-ton flywheel. Agents now write that software. I built the language that proves it: Mentl." | the hard tech named |
| 0:40 | slide 2 | never / why / learns | "A claim like never reaches the network, never allocates, never exceeds this bound is proven through every call or the program does not build. Every fact carries its reason. A learning rule is read off the chain it learns on. Self-hosting, byte-identical, one WebAssembly file, open source, [[years]] of commits." | depth |
| 1:30 | guitar, page | the number; `E`; `P`; `R`; `G` | "This week I pointed it at a wall socket." The cable buzz, the guitar, the number, thirty seconds. "The grid is a note; the West plays a B." `E`: the real event, the decision, the reason in words. `P`: "what the program that just decided can and cannot do, proven." `R`: "what review cannot do: the build refuses and names the line." `G`: "and what an agent gets when it proposes code through the gate: PROVEN, or REFUSED with nothing emitted." | progress; show it working |
| 3:10 | slide 3 | before / this week | "Everything on the right is since Monday at four. The ledger prints every commit with its time." *Optional, +10 s:* the pedal in hand, "the same ear on a thirty-dollar chip." | progress, the brief's own rule |
| 3:40 | slide 4 | who needs it | "Torus, whose judge saw this an hour ago: their Station hears every cycle, the program beneath it has never been provable. Hill AFB's 309th, Utah's largest employer of software developers, verifying flight software by review. Every Utah company putting agents on production code. First hires: compiler and controls engineers, Salt Lake City." | Utah impact |
| 4:20 | slide 5 | 30 / 60 / 90, the split, the asks | "Ten thousand dollars is ninety days: the proven controller on inverter-class hardware, one Utah site, the SBIR Phase I drafted with Nucleus Grow in the same window. What I need from you is on the page: an introduction at Torus engineering, one at the 309th, a co-founder with power-electronics depth. Connecting people is what you do." | path to reality |
| 5:00 | | | "I have been doing this for [[years]] and I will be doing it in November either way. The bounty decides whether the first real target is a Torus Station or my bench." Stop. | team and pitch |

## Jargon, translated on every main screen

ROCOF is "falling at"; the trigger, 0.1 Hz per second, is "pitch falling faster than three cents a second". THD is "how clean the wave is". The deadband is "the band where nothing needs to happen", one cent wide. Droop is "the harder it falls, the harder Spin pushes", a compressor. `!Network` is "cannot reach the network". A refinement is "a number that cannot leave its range". One cent at 60 Hz is 35 millihertz. NDJSON is never said.

## Questions, and the answers

- **Why a new language instead of Rust?** Rust prevents memory bugs, not effects. A Rust controller can call the network from anywhere and no compiler will say so.
- **Why not Simulink or SCADE?** They verify models and generate C. They cannot state "never reaches the network" as an obligation through every callee, cannot prove a function allocation-free, cannot derive a learning rule from the chain it learns on, and are neither open nor web-native.
- **What is the trusted base?** The compiler is self-hosting and its pinned binary reproduces itself byte for byte. The verifier is sound for what it decides and incomplete by design: a claim it cannot decide is reported as pending, never silently passed. One false proof is known and documented, deep recursion against a no-trap claim.
- **Is the proof real or a comment?** `mentl check examples/grid/station-leak.mn` in the terminal: the refusal with the chain. `mentl why examples/grid/station.mn decide Network`: "the row of decide carries no Network".
- **How does WebAssembly run on a controller?** The proof is at compile time; the artifact is one WASI module; it runs wherever wasmtime runs, which includes the Linux supervisors beside inverters. It answers each reading in under a millisecond here. A native backend is on the roadmap; the pedal runs the ear natively today.
- **Isn't this what Lasso does?** Lasso dispatches, learns and secures the perimeter. This proves the program beneath it and explains each decision. The layer under Lasso, not a replacement.
- **Doesn't your inverter already hear the grid?** Yes, every cycle, and better than a guitar. The guitar is how a room hears it. The new things are the proof, the explanation, and the fleet seeing angle.
- **Why zero crossings and not a PLL?** Three estimators run side by side and agree within three millihertz; crossings are the simplest to read. The learner is the PLL's cousin, written as one learned coefficient.
- **Is a guitar accurate?** A few millihertz, calibrated against the grid's long-run mean of 60.000; the offset is printed on the screen.
- **A level drop is not anti-islanding.** Correct, and the screen says "the hum died". Real anti-islanding is frequency and voltage windows under IEEE 1547, which the same measurement feeds.
- **Is the station real?** Modeled from Torus's published figures, labeled on every screen, as the brief allows.
- **Why is the rush hour at noon?** Because PacifiCorp East's data says so this week: the valley's commercial and industrial load peaks midday in October; the evening is when the sun leaves. Both are on the page.
- **Where is price?** In the hour's plan, where the Station reads it before the reflex. A price read inside the reflex is the line the compiler refuses.
- **What's the business?** Paid pilots with asset operators, a hosted proof gate for teams running coding agents, and an SBIR lane for defense software assurance.
- **Are you incorporated?** [[the one-pager's answer, with the date]]
- **Who is the team?** One founder and a fleet of agents under a proof gate, which is the thesis demonstrated. The ask names the co-founder needed.
- **Who owns it?** The team. All three repositories are public: Mentl under Apache and MIT, sonido under AGPL with a commercial license available, HUM beside them.
- **What if the hum fails live?** The recording from this room, made Tuesday, labeled, and the bundled session.
- **How much was this week?** Slide three's right column; `./ledger.sh` prints every commit with its time.

## Facts to fill before export

`[[name]]`, `[[years]]` (how long Mentl has existed, and sonido), `[[date / status]]` of incorporation, the one line of bio, the photo of the guitar on the interface as `pitch/img/guitar.jpg`, the hosted page's URL on slide five if it differs from ampactor.dev/hum.
