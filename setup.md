# The sixty-second setup

Before the judges sit down. Everything is already plugged in and running when they arrive.

1. Power strip in. Laptop on power. Scarlett on its USB cable. Guitar cable in channel 1, INST lit, gain at the rehearsed mark (do not touch it again).
2. `wpctl status` shows the Scarlett as the default source. If not: `wpctl set-default <id>`.
3. From the demo directory: `./run.sh live`. The kiosk window opens. The chip reads `● LIVE guitar, this room` within five seconds and the number moves.
4. If the chip reads WAITING after ten seconds: hold the pickup against the wall wart on the table. Still waiting: `./run.sh wav samples/hum_aernata.wav`, and the chip reads `▶ RECORDING`. The pitch does not change.
5. Pedal on its USB cable with a guitar cable in it; the lights breathe. If they do not, the pedal stays on the table unpowered.
6. Small speaker on the headphone out at a quarter volume. Press `S`, hear the pitch, press `S` again.
7. Press `0`. The page is in its opening state. Hands off the keyboard until the first beat.

Keys during the pitch: `E` replay event · `I` island (press again to return) · `P` certificate · `A` the compiler's words · `R` refusal · `T` table · `M` mesh · `S` sound · `B` bright room · `0` reset · `Esc` close.

Sway: workspace 1 is the tuner, workspace 2 is HUM. `swayidle` is off: `pkill swayidle` before the demo. Do not disturb on. Nothing else open.
