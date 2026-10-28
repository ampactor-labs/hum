# The venue setup

Two rooms, 15 minutes apart: Nucleus at 5:25 PM in the group 1 room, Torus at 5:40 PM in the group 4 room. Each slot is five minutes including your setup and the next team's, so the rig travels as one unit and is never unplugged between rooms.

## Before you leave home

1. `git pull` in `~/hum` and `~/mentl`, then `cd ~/hum/ear && cargo build --release`.
2. Plug the guitar into the Scarlett (INST lit, gain at the rehearsed mark) and the Scarlett into the laptop. Run `./run.sh live` and press `1`, then Space nine times, watching the timer. Press `2` and Space eight times. Then `0`.
3. Pack: the laptop and charger, the Scarlett and its USB cable, the guitar and cable, the 12 V power adapter that the pickup rests on, the small speaker and its cable, a power strip, the clicker if you have one, and the printed one-page plans. The pedal and its USB cable only if it is flashed and worked at home.

## On arrival, 5:00 PM

1. **Record a fallback first.** Plug in and record one minute of the venue's hum: `arecord -D pipewire -f S16_LE -r 48000 -c 1 -d 60 samples/hum_aernata.wav`.
2. **Power.** Power strip in, laptop on power. Between rooms the laptop runs on its battery with the lid open, so nothing restarts.
3. **The rig.** Plug the 12 V adapter into the power strip: it is the hum's source. Guitar into the Scarlett's channel 1, INST lit, gain at the rehearsed mark, and the guitar's neck pickup resting against the adapter for the whole pitch (tape the adapter to the guitar stand if it slips). `wpctl status` must show the Scarlett as the default source; if not, `wpctl set-default <id>`. Run `./run.sh live`. Never touch the cable tip on stage: the ear reads that buzz about a hertz high, and the flywheel fires.
   - With the pedal: guitar into the pedal, the pedal into the Scarlett, the pedal's USB into the laptop. Its footswitches type `e` and `i`.
   - Without the Scarlett: `./run.sh pedal` reads the pedal's own measurements over USB. The number and the needle work, but the waveform does not.
4. **Check the stage.** The kiosk window opens on the stage. Within five seconds the chip reads LIVE and the number moves.
5. **If it stays on WAITING.** Hold the pickup against a wall wart. If it still waits after ten seconds, run `./run.sh wav samples/hum_aernata.wav`. The chip then reads RECORDING, and the pitch does not change.
6. **Sound.** The small speaker at a quarter volume on the Scarlett's output, with direct monitoring on. The room hears the hum.
7. **Select the flow.** `2` before Nucleus, `1` before Torus. Then leave the keyboard alone until you start.

## Between rooms, 5:30 to 5:40

Close the laptop lid only if it is set not to sleep; otherwise carry it open. Carry the guitar plugged in. In the new room: power strip, speaker, `1`. If the hum is lost on the way, `0` and then `1` resets the page, and the ear reconnects on its own.

## The keys

`1` the Torus flow · `2` the Nucleus flow · Space or the right arrow: the next beat · the left arrow: one beat back · `H` tomorrow's noon, and back · `E` replay the 2019 event · `I` cut the hum, and bring it back · `P` proven · `R` refused · `K` thank you · `Esc` close a card · `D` the engineers' dashboard · `0` reset.

A presenter's clicker sends Page Down and Page Up, which the page reads as the next beat and one beat back.

## The pedal

Footswitch 1 replays the 2019 event. Footswitch 2 cuts the hum and brings it back. Toggle 1 down sets the clock to tomorrow's noon, and up returns it. The pedal types the same keys as the laptop, so the laptop keys always work as a backup.

Flash it once. Build the binary from sonido's `crates/sonido-daisy` on the branch `claude/serene-fermat-5408rg`:

```
cargo objcopy --example grid_pedal --release -- -O binary -R .sram1_bss grid_pedal.bin
```

Press RESET on the Seed. While its LED pulses, which lasts 2.5 seconds, run the line below. Pressing BOOT while the LED pulses makes it wait longer. Do not hold BOOT while you press RESET: that starts the chip's own bootloader, which cannot write this firmware. sonido's `docs/EMBEDDED.md` covers the tools and the bootloader.

```
dfu-util -a 0 -s 0x90040000:leave -D grid_pedal.bin
```

Then check it. `cat /dev/ttyACM0` shows one line every 50 ms, and pressing footswitch 1 in a text editor types `e`.

## The screen

Sway workspace 1 is HUM. Workspace 2 is a terminal in the Mentl checkout, for `mentl check examples/grid/station-leak.mn` if a judge asks to see the refusal after the finals. Stop the screen from sleeping (`pkill swayidle`) and turn notifications off. Nothing else open.
