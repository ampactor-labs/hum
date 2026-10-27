# The sixty-second setup

Before the judges sit down. Everything is already plugged in and running when they arrive.

1. Power strip in. Laptop on power. Scarlett on its USB cable. Guitar cable in channel 1, INST lit, gain at the rehearsed mark (do not touch it again).
2. `wpctl status` shows the Scarlett as the default source. If not: `wpctl set-default <id>`.
3. From the demo directory: `./run.sh live`. The kiosk window opens. The chip reads `● LIVE guitar, this room` within five seconds and the number moves.
4. If the chip reads WAITING after ten seconds: hold the pickup against the wall wart on the table. Still waiting: `./run.sh wav samples/hum_aernata.wav`, and the chip reads `▶ RECORDING`. The pitch does not change.
5. Pedal on its USB cable with a guitar cable in it; the lights breathe. If they do not, the pedal stays on the table unpowered. Flashing it (once, Tuesday), from sonido's `crates/sonido-daisy` with the Seed in DFU mode (hold BOOT, tap RESET):

   ```
   cargo objcopy --example grid_pedal --release -- -O binary -R .sram1_bss firmware/grid_pedal.bin
   dfu-util -a 0 -s 0x90040000:leave -D firmware/grid_pedal.bin
   ```

   Then `cat /dev/ttyACM0` shows one line every 50 ms, and `./run.sh pedal` reads them.
6. Small speaker on the headphone out at a quarter volume: Bitwig's output, so the room hears the real hum. In Bitwig: track 1 the live input with the sonido tuner on it; track 2 `samples/event_gb.wav`, cued to its start, muted until the optional beat ("that is the pitch of a blackout").
7. Press `0`. The page is in its opening state. Hands off the keyboard until the first beat.

Keys during the pitch: `H` tomorrow's noon (the clock set inside the rush hour; press again to return) · `E` replay event (eight seconds of calm, then the fall) · `I` island (press again to return) · `P` certificate · `A` the compiler's words · `R` refusal · `G` the gate · `T` table · `M` mesh · `S` the page's own tone (not used; the speaker carries the hum) · `B` bright room · `0` reset · `Esc` close.

Sway: workspace 1 is Bitwig with the tuner, workspace 2 is HUM, workspace 3 a terminal in the Mentl checkout for `mentl check examples/grid/station-leak.mn` in questions. `swayidle` is off: `pkill swayidle` before the demo. Do not disturb on. Nothing else open.
