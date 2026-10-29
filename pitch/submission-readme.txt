HUM · Hard Tech Week 2026, Salt Lake City
Morgan Espitia · sonofagoose@pm.me
Entered for the Torus bounty and the Nucleus × Startup State open call.


WHAT HUM IS

HUM hears the power grid's frequency through a guitar pickup resting on a
power adapter. A model of a Torus Station decides what its flywheel and
battery should do, using a controller written in Mentl, a language I
built. The controller's rules are written into its code, and the compiler
checks them through every function the decision calls on every build: the
decision never reaches the network, a file or the clock, never allocates
memory and never stops with an error. A version that breaks a rule does
not build.


THE FILES

1-HUM-pitch-deck.pdf
  The slides shown on stage, the same in both rooms. The live screens (the
  hum, rush hour, the 2019 replay and the blackout) run between them.

Files 2 to 4 are written to be read afterwards, not shown on stage.

2-HUM-Torus-leave-behind.pdf
  Four pages for Torus.

3-Mentl-Nucleus-deck.pdf
  The Nucleus pages, with two backup pages: what is proven, exactly, and
  the engineering left before the controller runs on the guitar pedal.

4-Mentl-Nucleus-one-page-plan.pdf
  The one-page plan: the problem, what exists, ninety days, the $10,000.

5-HUM-stage-during-the-2019-replay.png
  The live screen while the replayed 2019 event pulls the frequency down
  and the flywheel pushes 100 kW.

6-Mentl-budget-for-the-10000.md
  The $10,000, line by line, with what each item costs and where each
  price comes from.


SEE IT

The demo in a browser:  https://ampactor.dev/hum
  It plays a session recorded with the real controller. The arrows on
  screen, or the arrow keys, step through the same show.
The demo's code:        https://github.com/ampactor-labs/hum
Mentl, the language:    https://github.com/ampactor-labs/mentl
sonido, the audio code: https://github.com/ampactor-labs/sonido


WHAT IS REAL AND WHAT IS SIMULATED

- The live hum and its frequency are real, read from a room's wiring.
- The 9 August 2019 event is real data from Great Britain: National Grid
  ESO's one-second frequency record, transposed to 60 Hz and replayed.
- Rush hour comes from EIA-930 hourly demand for PacifiCorp East,
  19 to 26 October 2026.
- The Station is a model built from Torus's published figures: a flywheel
  giving 100 kW for six minutes and a battery giving 300 kW for four
  hours. It is simulated, and every screen says so.
- Checked by the compiler through every call: the decision makes no
  network, file, clock or other call outside the program, allocates no
  memory and never stops with an error. Not proven: that its decisions
  are good; recordings test them.


BUILT THIS WEEK

Everything in the HUM repository was written after the hackathon began,
on Monday 26 October 2026 at 4:00 PM MDT. Mentl (since March 15) and
sonido (since January 25) existed before it. ./ledger.sh in the HUM
repository prints every commit in all three, with its time.
