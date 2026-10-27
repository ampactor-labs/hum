# The venue setup

Do this before the judges sit down, so everything is running when they arrive.

1. **Record a fallback first.** On arrival, plug in the guitar and record one minute of the room's hum: `arecord -D pipewire -f S16_LE -r 48000 -c 1 -d 60 samples/hum_aernata.wav`.
2. **Power.** Power strip in, laptop on power.
3. **The rig: guitar, pedal, Scarlett.** Guitar into the pedal's input. The pedal's output into the Scarlett's channel 1, INST lit, gain at the rehearsed mark, then leave it alone. The pedal's USB cable into the laptop, so its footswitches work. `wpctl status` must show the Scarlett as the default source; if not, `wpctl set-default <id>`. Run `./run.sh live`. The laptop gets the full signal, so the stage shows the waveform and sonido's tuner.
   - Without the Scarlett: `./run.sh pedal` reads the pedal's own measurements over USB. The number and the needle work, but the waveform does not.
   - Without the pedal: guitar straight into the Scarlett, and use the laptop keys.
4. **Check the stage.** The kiosk window opens on the stage. Within five seconds the chip reads LIVE and the number moves.
5. **If it stays on WAITING.** Hold the pickup against a wall wart. If it still waits after ten seconds, run `./run.sh wav samples/hum_aernata.wav`. The chip then reads RECORDING, and the pitch does not change.
6. **Sound.** A small speaker at a quarter volume on the Scarlett's output, with direct monitoring on. The room hears the hum.
7. **Reset.** Press `0`. Then leave the keyboard alone until you start.

## The keys

`H` tomorrow's noon, and back · `E` replay the 2019 event · `I` cut the hum, and bring it back · `P` proven · `R` refused · `K` thank you · `Esc` close a card · `D` the engineers' dashboard · `0` reset.

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

Sway workspace 1 is HUM. Workspace 2 is a terminal in the Mentl checkout, for `mentl check examples/grid/station-leak.mn` if a judge asks to see the refusal live. Stop the screen from sleeping (`pkill swayidle`) and turn notifications off. Nothing else open.
