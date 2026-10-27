# The two pitches

Both rooms. Everything is running before the judges sit down: cable plugged, gain set, the number moving, the pedal's lights breathing. No gain knob is touched live. The guitar moment is sixty to ninety seconds in the Torus room and forty-five in the Nucleus room.

**The rule of names.** The Torus room hears "the program that decides" until slide four; "Mentl" is said once there. The Nucleus room hears "Mentl" in the first sentence.

**The guitar moment, both rooms.** Touch the cable tip: the buzz. "Every guitarist knows that sound. That buzz is the grid." Plug the guitar in; the number is on screen. Move the guitar: the level swings, the number holds. "It does not care where I hold it. It is not my number." Lift the pedal: the same number. Hand it to a judge. Press `S`: fifteen seconds of the pitch wobble through the speaker. Press `S`. Guitar on its stand.

## Torus, six minutes

| Time | On screen | Say |
| --- | --- | --- |
| 0:00 | HUM live, the number | "Everyone here will show you the traffic report. I'm going to show you the road. That number is not mine. It belongs to the Western Interconnection, Alberta to Baja, measured from this room's wiring through a guitar pickup. It sags when the whole grid is short." |
| 0:40 | the tuner (workspace 1), then back | "My tuner reads it as B1, forty-nine cents flat. That is sixty hertz. The grid is a note, and it wobbles by half a cent." |
| 1:00 | sound on, the pedal lifted | "Your Station already hears this every cycle. The rest of this hackathon reads an hourly report. I built the smallest thing that hears what your Station hears, so this room can hear the rush hour too. And it fits in this." |
| 1:45 | RUSH HOUR panel | "PacifiCorp East's rush hour this week is not six in the evening. It is noon to four, when the valley's offices and factories run. The sun leaves at six. Pulse takes these hours; Spin takes the milliseconds." |
| 2:30 | `E`: the real event | "A real event's shape: the ninth of August, 2019, two plants tripped in the same second. Watch. The frequency falls, the rate of fall crosses the trigger, Spin answers within a third of a second, Pulse never moved. That is your two-technology story, in numbers, with the reason in words." |
| 3:30 | `I`: the hum dies | "Now the grid goes dark. The same ear knows first. The Station carries the building. That is the two-way story you told me last night." `I` again. |
| 4:15 | `P` then `R` | "The program that just decided can read the stream and write commands. It cannot reach the network, cannot touch the filesystem, cannot ask Spin for more than ten C. Not by policy: proven, by the compiler, through every call. Here is what happens when a price lookup sneaks into the loop." The refusal, ten seconds. "That is the layer under Lasso." |
| 5:15 | slide 5 | "Five thousand dollars buys a second ear and a GPS clock. The angle between two Salt Lake sites is the flow between them. I'll bring that measurement to your engineers." Stop. `M` only if asked. |

**The five-minute cut:** drop the tuner line at 0:40 and the island at 3:30; say "and when the hum dies, it carries the building" at 2:30 instead.

## Nucleus, six minutes

| Time | On screen | Say |
| --- | --- | --- |
| 0:00 | slide 1 | "Software that steers physical things is tested and hoped on. Nobody can prove a controller will never reach the network while it is steering a seven-ton flywheel. Agents now write that software. I built the language that proves it. It is called Mentl." |
| 0:45 | slide 2 | "A claim like never reaches the network, never allocates, never exceeds a bound is proven through every call or the program does not build. Every fact carries its reason. A learning rule is read off the chain it learns on. Self-hosting, byte-identical, one WebAssembly file, open source, [[years]] of commits." |
| 1:45 | HUM live, then `E`, then `R` | "This week I pointed it at a wall socket." The guitar moment, forty-five seconds. "Here is a real grid event, and the controller's decision with its reason." `R`: "and here is what review cannot do: the build refuses, and names the line." The agent transcript, one sentence: "an agent tried the same thing through the gate and got REFUSED." |
| 3:15 | slide 4, the pedal in hand | "Who needs it. Torus, who judged this demo an hour ago: their Station hears every cycle, their security is a perimeter, the program itself has never been provable until now. Hill AFB's 309th, Utah's largest employer of software developers, verifying flight software by review. And every Utah company putting agents on production code. The same code runs on this thirty-dollar chip." |
| 4:15 | slide 5 | "Ten thousand dollars is ninety days: the proven controller on inverter-class hardware, one Utah site, and the SBIR Phase I drafted with Nucleus Grow in the same window. The split is on the slide. What I need from you is on the page: an introduction at Torus engineering, one at the 309th, and a co-founder with power-electronics depth. Connecting people is what you do." |
| 5:15 | | "I have been doing this for [[years]] and I will be doing it in November either way. The bounty decides whether the first real target is a Torus Station or my bench." Stop. |

**The five-minute cut:** fold slide 2 into one sentence at 0:45 and skip the agent transcript.

## Jargon, translated on every main screen

ROCOF is "falling at". THD is "how clean the wave is" ("wave 3% distorted"). The deadband is "the band where nothing needs to happen". Droop is "the harder it falls, the harder Spin pushes". `!Network` is "cannot reach the network". A refinement is "a number that cannot leave its range". NDJSON is never said.

## Questions, and the answers

- **Why a new language instead of Rust?** Rust prevents memory bugs, not effects. A Rust controller can call the network from anywhere and no compiler will say so.
- **Why not Simulink or SCADE?** They verify models and generate C. They cannot state "never reaches the network" as an obligation through every callee, cannot prove a function allocation-free, cannot derive a learning rule from the chain it learns on, and are neither open nor web-native.
- **What is the trusted base?** The compiler is self-hosting and its pinned binary reproduces itself byte for byte. The verifier is sound for what it decides and incomplete by design: a claim it cannot decide is reported as pending, never silently passed. One false proof is known and documented, deep recursion against a no-trap claim.
- **How does WebAssembly run on a controller?** The proof is at compile time; the artifact is one WASI module; it runs wherever wasmtime runs, which includes the Linux supervisors beside inverters. A native backend is on the roadmap; the pedal runs the ear natively today.
- **Isn't this what Lasso does?** Lasso dispatches, learns and secures the perimeter. This proves the program beneath it and explains each decision. The layer under Lasso, not a replacement.
- **Doesn't your inverter already hear the grid?** Yes, every cycle, and better than a guitar. The guitar is how a room hears it. The new things are the proof, the explanation, and the fleet seeing angle.
- **Why zero crossings and not a PLL?** Three estimators run side by side and agree within three millihertz; crossings are the simplest to read. A PLL is one of the two lines of feedback the learner already draws.
- **Is a guitar accurate?** A few millihertz, calibrated against the grid's long-run mean of 60.000; the offset is printed on the screen.
- **A level drop is not anti-islanding.** Correct, and the screen says "the hum died". Real anti-islanding is frequency and voltage windows under IEEE 1547, which the same measurement feeds.
- **Is the station real?** Modeled from Torus's published figures, labeled on every screen, as the brief allows.
- **Why is the rush hour at noon?** Because PacifiCorp East's data says so this week: the valley's commercial and industrial load peaks midday in October; the evening is when the sun leaves. Both are on the page.
- **What's the business?** Paid pilots with asset operators, a hosted proof gate for teams running coding agents, and an SBIR lane for defense software assurance.
- **Are you incorporated?** [[the one-pager's answer, with the date]]
- **Who is the team?** One founder and a fleet of agents under a proof gate, which is the thesis demonstrated. The ask names the co-founder needed.
- **Who owns it?** The team. Both repositories are public: Mentl under Apache and MIT, sonido under AGPL with a commercial license available.
- **What if the hum fails live?** The recording from this room, made Tuesday, labeled, and the video.
- **How much was this week?** Slide three's right column; `./ledger.sh` prints every commit with its time.

## Facts to fill before export

`[[name]]`, `[[email]]`, `[[years]]` (how long Mentl has existed, and sonido), `[[date / status]]` of incorporation, the one line of bio, the photo of the guitar on the interface as `pitch/img/guitar.jpg`, the hosted page's URL on slide five if it differs from ampactor.dev/hum.
