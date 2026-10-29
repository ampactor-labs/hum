# The two pitches

**The format, from the judging sheet.** Each team gets one 5-minute slot per bounty, back to back with the next team, so there is no time for questions: everything the judges learn, they learn from the pitch. Nucleus is judged in groups 1 to 3 and Torus in groups 4 to 6, in different rooms, and a team in both pitches Nucleus first with 15 minutes to move. Finalists present again to the full panel between 6:15 and 6:45 PM, and winners are announced Thursday at 9:00 AM at the Zero Gravity Summit. Arrive by 5:00 PM; judging starts at 5:15. Run `./pitch/submission.sh` and upload the `submission/` folder it fills (the four PDFs, the stage picture and a README) to the submission Drive folder before then.

**Before you start, in both rooms.** The page is up in kiosk mode and the number is moving. The guitar is plugged in, with the gain at the rehearsed mark, and its neck pickup rests against the power adapter on the power strip, so the number is steady and the tuner reads B. The speaker is at a quarter. Never touch the cable tip on stage: the ear reads that buzz a full hertz high, and the flywheel would fire. The page opens on the show's title. If it isn't on the title, press `0`. Then press nothing until the judges are ready.

**One show, one key.** Both rooms and the finals get the same show, in the same order. Footswitch 1, Space, the right arrow or a clicker's Page Down runs the next beat. Footswitch 2 or the left arrow steps back one. `0` returns to the title. The timer at the bottom right shows the beat and the time since the first press, such as `5/15 · 0:52`. Every screen explains itself in writing, so a judge who looks away can catch up, and each beat sets the whole screen, so a step back or forward always lands on the right one.

**What to say, and what not to.** Say "a model of Torus's Station", never "the Station" alone. Say "replayed", never that anyone tripped a plant. Say "can't reach the internet while it decides", never "proven" alone. Never say a function name, "WASI", "row" or "first light".

## The show: fifteen beats, four and a quarter minutes, every room

| Time | Beat | On screen | Say |
| --- | --- | --- | --- |
| before | 1 title | Name, the sentence, the picture. Up while the room changes over. | Nothing until the judges are ready. |
| 0:00 | (still the title) | | "I'm Morgan Espitia. I build a programming language called Mentl, here in Salt Lake City." Next. |
| 0:05 | 2 how to read it | The grid, the ear, the Station, the software. | Let them read it for three seconds. "Here's how to read what you're about to see." Next. |
| 0:10 | 3 live | The live number and sonido's tuner. Top line: "Live in this room". | Don't touch the guitar: the pickup stays taped to the adapter. "That hum is the power grid. Every power adapter in this room sings it, and a guitar pickup hears it. Sixty hertz, the note B. The whole Western grid, from Alberta to Baja, hums this one note. It jams in two ways." Next. |
| 0:30 | 4 rush hour | TOMORROW · 12:30 PM. The battery runs the building. | "You can see the first kind coming. This is tomorrow at noon, from EIA's data for PacifiCorp East: rush hour. A model of Torus's Station runs the building on its battery, three hundred kilowatts kept off the grid." Next. |
| 0:50 | 5 replay | REPLAY. The number falls, the needle swings flat, the flywheel lights. | "You can only hear the second kind. On the ninth of August 2019, two power plants in Britain tripped within a second. This is that day's real frequency, replayed at our grid's pitch." When the flywheel lights: "The flywheel started pushing within half a second. Hourly data can't show a fall like this one." Let the line on the floor finish its drop. Next. |
| 1:35 | 6 dark | THE HUM IS CUT. "The grid went dark. The building is still on." | "That evening a million people in Britain lost power. When the grid goes dark here, the flywheel carries the first seconds and the battery runs the building." Next (the hum comes back by itself). |
| 1:50 | 7 proven | Proven. | "The software making these decisions is written in Mentl, and it can't reach the internet while it decides. The compiler proves that by checking every function the decision calls." Next. |
| 2:05 | 8 refused | Refused, with the compiler's path. | "Say an AI assistant adds one line that checks electricity prices online. The hour's plan can use EIA's data, but the split-second decision can't reach the internet, so the compiler won't build it." Next. |
| 2:15 | 9 why it matters | AI now helps write the software that runs machines. | "That matters because AI now helps write the software that runs batteries, flywheels and flight controls, and no mainstream language can prove what that software will never do." Next. |
| 2:30 | 10 Mentl | Mentl proves what software can never do, and the compiler's answer about this controller. | "Mentl can. You write a rule into the code, the compiler checks it through every function the code calls, and code that breaks it won't build. Seven months, twenty-six hundred commits, and the compiler is written in its own language." Next. |
| 2:45 | 11 Mentl's code | Five operators as real code, and the `with !Network` rule. | "This is what it looks like. Five operators draw the program's shape, and the rule on the last line is what the compiler checks." Next. |
| 2:55 | 12 built this week | Before Monday, and this week, in commits. | "Everything you just saw was built since Monday at four. The repository prints every commit with its time." Next. |
| 3:00 | 13 who needs it | Torus, and Hill AFB's 309th. | "Who needs it here: Torus, for the software inside each Station, and Hill Air Force Base's 309th, which maintains flight software for the F-16, the F-35 and the missile fleet." Next. |
| 3:20 | 14 the $10,000 | Day 30, 60, 90 and three asks. | "Ten thousand dollars puts this controller beside a real battery in Utah within ninety days: on my bench by day thirty, beside a real battery at a Utah site by day sixty, and a pilot agreement and an SBIR proposal with Nucleus Grow by day ninety. Three asks: a Utah operator who will host it, an introduction to the 309th, and a co-founder who knows power electronics." Next. |
| 3:55 | 15 thank you | The QR code and ampactor.dev/hum. | "Scan the code to replay this on your phone. Thank you." Stop, by 4:15. |

**If the room is slow to start,** skip beat 2's line and cut the last sentence of beat 3. **If you run long,** drop the second sentence of beat 10, beat 11's line, and the day-by-day list in beat 14 ("within ninety days, then three asks"). **Never add** anything to the show on stage: the slot has no room.

## The finals, 6:15 PM, if called

The full panel, both bounties, five minutes. Run the same show. Nothing changes.

## If anyone asks, in the hallway or after the finals

- **Isn't 60 Hz between A sharp and B?** With A at 440 Hz, yes. I set the tuner's A to 427.65 Hz so that the grid sits exactly on B. The needle then centers while the grid is in tune and swings flat when it sags.
- **Is the guitar accurate?** On a test signal it reads within half a thousandth of a hertz. Live, the reading is calibrated against the grid's long-run average of exactly sixty, and the offset is printed on the dashboard.
- **How fast does the flywheel really answer?** In the replay it starts pushing about 0.4 seconds after the fall shows, once the frequency is more than 36 millihertz low. It reaches full power within 0.75 seconds, when the ear measures the fall passing 100 millihertz per second. The decision itself typically takes under a millisecond.
- **Doesn't a Torus Station already measure the grid?** Yes, every cycle, and better than a guitar. The guitar is how a room full of people gets to hear it. What's new is that the decisions come with a proof.
- **Is the Station real?** It's a model built from Torus's published figures: 100 kW from the flywheel for six minutes, 300 kW from the battery for four hours. Every screen says it's simulated.
- **Is the proof real?** In a terminal: `mentl check examples/grid/station-leak.mn` refuses the price lookup, and `mentl why examples/grid/station.mn decide WASI` answers that the decision's effects carry no call outside the program. The answer starts with the word "error" because the compiler is reporting that there is nothing to show; it is the result you want. `D` then `Shift+P` shows the full list.
- **What exactly is proven?** That the decision makes no network, file, clock or other call outside the program, and allocates no memory, through every function it calls. The power limits are proven where each machine answers a command, and the decision is proven never to stop with an error. It does not prove that its decisions are good. The backup slide has the table.
- **Why does "can't reach the internet" matter to a Station?** The decision code itself can't send anything out or take instructions from outside, whatever is added to it later, by a person or by an AI assistant. It does not protect the rest of the Station.
- **Why a new language instead of Rust?** Rust stops memory bugs. It can't say "this function never reaches the network" and check it through every call.
- **Can it run on the pedal?** Not yet. The controller is a 37 KB WebAssembly file, and the pedal's chip has no engine for it. Its memory no longer grows: the same peak after 300,000 readings as after one. The engine is on the day-30 list, and the backup slide shows the measurements.
- **Why is rush hour at noon?** PacifiCorp East's data this week says so: offices and factories peak midday in October. The evening jam comes when solar power drops off at sunset.
- **Where is price?** In the hour's plan, read before the fast decision. A price lookup inside the fast decision is the line the compiler refuses.
- **How much of the code did AI write?** Answer in one true sentence, decided before you walk in.
- **Are you incorporated?** Not yet. Forming a Utah company is day one, because the federal grant registrations need it and take weeks.
- **Which is the company, the controller or the language?** The company is Mentl. Energy control software is the first market, because a mistake there is physical and the buyers are here.
- **Who is the first customer?** Nobody has signed yet. The day-60 site is the pilot, and Torus is the one I want.
- **Who is on the team?** One founder. The first hires are a controls engineer and a compiler engineer in Salt Lake City, and the co-founder I need knows power electronics.
- **What if the live hum fails?** `./run.sh wav` plays a recording made in this room, and the page says RECORDING.
