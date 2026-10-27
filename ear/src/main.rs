//! grid_ear: the HUM ear. Reads a mains hum, measures the grid's frequency
//! three independent ways, and prints one line every 50 ms (the C1 contract
//! in `demos/grid-rush-hour/CONTRACTS.md`).
//!
//! Sources, one per run:
//!   --stdin-f32            raw float32 mono samples on stdin (live capture)
//!   --wav <path>           a recording (any channel count; averaged to mono)
//!   --tone <hz>            a synthesized hum with harmonics and noise
//!   --replay <t,hz csv>    a synthesized hum whose frequency follows a series
//!   --silence              nothing but noise at -90 dBFS (the hum died)
//! Options:
//!   --rate <hz>            sample rate for synthetic and stdin sources (48000)
//!   --seconds <s>          length of a synthetic run (20)
//!   --wobble               ±20 mHz at 0.05 Hz on the tone, so the trace moves
//!   --cut-at <s>           a synthetic hum that cuts to silence at this time
//!   --realtime             pace the output at wall-clock speed
//!   --tee <path>           append every line to this file as well
//!   --emit-decimated <p>   the tracked band at 480 Hz, one float per line
//!   --source <label>       override the "source" field
//!
//! Three estimators: zero crossings on the loudest harmonic band (hz_fast over
//! three cycles, hz over one second, from `sonido_core::grid::GridEar`), and the
//! spectral peak of a two-second Hann window with quadratic interpolation
//! (hz_stft). THD is read off the same spectrum. All three should agree to a
//! few millihertz on a clean hum; the page shows them side by side.
//!
//!   cargo run -p sonido-analysis --release --example grid_ear -- --tone 60.050 --seconds 5

use rustfft::FftPlanner;
use rustfft::num_complex::Complex;
use sonido_core::grid::GridEar;
use std::fs::{File, OpenOptions};
use std::io::{self, BufWriter, Read, Write};
use std::thread::sleep;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const NOMINAL_HZ: f32 = 60.0;
const STFT_SECONDS: usize = 2;
const NFFT: usize = 1 << 18;
const STFT_EVERY_TICKS: usize = 10;

enum Mode {
    Tone(f32),
    Replay(String),
    Silence,
    Wav(String),
    Stdin,
}

struct Opts {
    mode: Mode,
    rate: f32,
    seconds: f32,
    wobble: bool,
    cut_at: Option<f32>,
    realtime: bool,
    tee: Option<String>,
    decimated: Option<String>,
    source: Option<String>,
}

fn parse_args() -> Opts {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut mode = None;
    let mut opts = Opts {
        mode: Mode::Silence,
        rate: 48000.0,
        seconds: 20.0,
        wobble: false,
        cut_at: None,
        realtime: false,
        tee: None,
        decimated: None,
        source: None,
    };
    let mut i = 0;
    let next = |i: &mut usize| -> String {
        *i += 1;
        args.get(*i).cloned().unwrap_or_else(|| {
            eprintln!("grid_ear: missing value after {}", args[*i - 1]);
            std::process::exit(2)
        })
    };
    while i < args.len() {
        match args[i].as_str() {
            "--stdin-f32" => mode = Some(Mode::Stdin),
            "--wav" => mode = Some(Mode::Wav(next(&mut i))),
            "--tone" => mode = Some(Mode::Tone(next(&mut i).parse().expect("--tone <hz>"))),
            "--replay" => mode = Some(Mode::Replay(next(&mut i))),
            "--silence" => mode = Some(Mode::Silence),
            "--rate" => opts.rate = next(&mut i).parse().expect("--rate <hz>"),
            "--seconds" => opts.seconds = next(&mut i).parse().expect("--seconds <s>"),
            "--wobble" => opts.wobble = true,
            "--cut-at" => opts.cut_at = Some(next(&mut i).parse().expect("--cut-at <s>")),
            "--realtime" => opts.realtime = true,
            "--tee" => opts.tee = Some(next(&mut i)),
            "--emit-decimated" => opts.decimated = Some(next(&mut i)),
            "--source" => opts.source = Some(next(&mut i)),
            other => {
                eprintln!("grid_ear: unknown argument {other}");
                std::process::exit(2);
            }
        }
        i += 1;
    }
    opts.mode = mode.unwrap_or_else(|| {
        eprintln!("grid_ear: one of --stdin-f32, --wav, --tone, --replay, --silence");
        std::process::exit(2)
    });
    opts
}

/// A hum synthesizer: fundamental, a second at -20 dB, a third at -10 dB,
/// white noise at -30 dB, the fundamental's frequency following `freq_at`.
struct Hum {
    rate: f64,
    phase: f64,
    n: u64,
    lcg: u64,
    amplitude: f64,
}

impl Hum {
    fn new(rate: f32) -> Self {
        Self { rate: rate as f64, phase: 0.0, n: 0, lcg: 0x9E37_79B9_7F4A_7C15, amplitude: 0.3 }
    }

    fn noise(&mut self) -> f64 {
        self.lcg = self.lcg.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.lcg >> 11) as f64 / (1u64 << 53) as f64) * 2.0 - 1.0
    }

    fn sample(&mut self, hz: f64, silent: bool) -> f32 {
        self.phase += hz / self.rate;
        if self.phase >= 1.0 {
            self.phase -= 1.0;
        }
        self.n += 1;
        let noise = self.noise();
        if silent {
            // -90 dBFS of noise: the hum died, the wire is still there.
            return (noise * 3.16e-5) as f32;
        }
        let w = 2.0 * std::f64::consts::PI * self.phase;
        let s = w.sin() + 0.1 * (2.0 * w).sin() + 0.316 * (3.0 * w).sin() + 0.0316 * noise * 1.732;
        (self.amplitude * s) as f32
    }
}

/// A `t,hz` series, linearly interpolated, held at its ends.
struct Series {
    t: Vec<f64>,
    hz: Vec<f64>,
}

impl Series {
    fn load(path: &str) -> Self {
        let text = std::fs::read_to_string(path).unwrap_or_else(|e| {
            eprintln!("grid_ear: cannot read {path}: {e}");
            std::process::exit(2)
        });
        let mut t = Vec::new();
        let mut hz = Vec::new();
        for line in text.lines() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            let mut parts = line.split(',');
            let (Some(a), Some(b)) = (parts.next(), parts.next()) else { continue };
            let (Ok(a), Ok(b)) = (a.trim().parse::<f64>(), b.trim().parse::<f64>()) else { continue };
            t.push(a);
            hz.push(b);
        }
        if t.is_empty() {
            eprintln!("grid_ear: {path} holds no t,hz rows");
            std::process::exit(2);
        }
        Self { t, hz }
    }

    fn at(&self, time: f64) -> f64 {
        if time <= self.t[0] {
            return self.hz[0];
        }
        let last = self.t.len() - 1;
        if time >= self.t[last] {
            return self.hz[last];
        }
        let i = self.t.partition_point(|&x| x <= time) - 1;
        let span = self.t[i + 1] - self.t[i];
        let u = if span > 0.0 { (time - self.t[i]) / span } else { 0.0 };
        self.hz[i] + (self.hz[i + 1] - self.hz[i]) * u
    }
}

/// The spectral estimator: a Hann window over the last two seconds, zero-padded,
/// the peak nearest the nominal harmonic interpolated with a parabola on
/// log magnitude, and THD from the harmonics of the fundamental.
struct Spectral {
    planner_fft: std::sync::Arc<dyn rustfft::Fft<f32>>,
    buf: Vec<Complex<f32>>,
    window: Vec<f32>,
    rate: f32,
    len: usize,
}

impl Spectral {
    fn new(rate: f32) -> Self {
        let len = STFT_SECONDS * rate as usize;
        assert!(len <= NFFT, "two seconds must fit the FFT");
        let window: Vec<f32> = (0..len)
            .map(|i| 0.5 - 0.5 * (2.0 * std::f32::consts::PI * i as f32 / len as f32).cos())
            .collect();
        let mut planner = FftPlanner::<f32>::new();
        Self { planner_fft: planner.plan_fft_forward(NFFT), buf: vec![Complex::new(0.0, 0.0); NFFT], window, rate, len }
    }

    /// `(hz_stft, thd_percent)` for the samples in `ring` (oldest first), on the
    /// tracked `harmonic`. `None` when the band holds no peak above the noise.
    fn read(&mut self, ring: &[f32], harmonic: u8) -> Option<(f32, f32)> {
        let n = ring.len().min(self.len);
        let offset = ring.len() - n;
        let mean: f32 = ring[offset..].iter().sum::<f32>() / n as f32;
        for (i, c) in self.buf.iter_mut().enumerate() {
            *c = if i < n {
                Complex::new((ring[offset + i] - mean) * self.window[i], 0.0)
            } else {
                Complex::new(0.0, 0.0)
            };
        }
        self.planner_fft.process(&mut self.buf);
        let bin_hz = self.rate / NFFT as f32;
        let mag = |k: usize| self.buf[k].norm();
        let peak_near = |center_hz: f32, half_width_hz: f32| -> Option<(usize, f32)> {
            let lo = ((center_hz - half_width_hz) / bin_hz).max(1.0) as usize;
            let hi = ((center_hz + half_width_hz) / bin_hz) as usize;
            let mut best = None;
            for k in lo..=hi {
                let m = mag(k);
                if best.map_or(true, |(_, bm)| m > bm) {
                    best = Some((k, m));
                }
            }
            best
        };
        let (k, m) = peak_near(NOMINAL_HZ * harmonic as f32, 3.0 * harmonic as f32)?;
        if m < 1e-6 || k == 0 || k + 1 >= NFFT / 2 {
            return None;
        }
        let a = mag(k - 1).max(1e-12).ln();
        let b = m.ln();
        let c = mag(k + 1).max(1e-12).ln();
        let denom = a - 2.0 * b + c;
        let delta = if denom.abs() > 1e-12 { 0.5 * (a - c) / denom } else { 0.0 };
        let hz_stft = (k as f32 + delta) * bin_hz / harmonic as f32;

        // THD of the hum as heard: harmonics 2..=10 of the fundamental over the fundamental.
        let (_, fund) = peak_near(NOMINAL_HZ, 3.0)?;
        let mut harm_power = 0.0f32;
        for h in 2..=10u32 {
            if let Some((_, hm)) = peak_near(NOMINAL_HZ * h as f32, 3.0) {
                harm_power += hm * hm;
            }
        }
        let thd = if fund > 1e-9 { 100.0 * harm_power.sqrt() / fund } else { 0.0 };
        Some((hz_stft, thd))
    }
}

fn now_unix() -> f64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs_f64()).unwrap_or(0.0)
}

fn fmt_opt(v: Option<f32>, decimals: usize) -> String {
    match v {
        Some(x) => format!("{x:.decimals$}"),
        None => "null".to_string(),
    }
}

fn load_wav(path: &str) -> (Vec<f32>, f32) {
    let mut reader = hound::WavReader::open(path).unwrap_or_else(|e| {
        eprintln!("grid_ear: cannot open {path}: {e}");
        std::process::exit(2)
    });
    let spec = reader.spec();
    let channels = spec.channels as usize;
    let interleaved: Vec<f32> = match spec.sample_format {
        hound::SampleFormat::Float => reader.samples::<f32>().map(|s| s.unwrap_or(0.0)).collect(),
        hound::SampleFormat::Int => {
            let full = (1i64 << (spec.bits_per_sample - 1)) as f32;
            reader.samples::<i32>().map(|s| s.unwrap_or(0) as f32 / full).collect()
        }
    };
    let mono: Vec<f32> = interleaved
        .chunks(channels)
        .map(|frame| frame.iter().sum::<f32>() / channels as f32)
        .collect();
    (mono, spec.sample_rate as f32)
}

fn main() {
    let opts = parse_args();
    let (mut samples_from_wav, rate) = match &opts.mode {
        Mode::Wav(path) => {
            let (s, r) = load_wav(path);
            (Some(s), r)
        }
        _ => (None, opts.rate),
    };
    let block = (rate / 20.0).round() as usize;
    let source_label = opts.source.clone().unwrap_or_else(|| {
        match opts.mode {
            Mode::Tone(_) => "tone",
            Mode::Replay(_) => "replay",
            Mode::Silence => "silence",
            Mode::Wav(_) => "wav",
            Mode::Stdin => "live",
        }
        .to_string()
    });

    let mut ear = GridEar::new(NOMINAL_HZ, rate);
    let mut spectral = Spectral::new(rate);
    let stft_len = STFT_SECONDS * rate as usize;
    let mut ring: Vec<f32> = Vec::with_capacity(stft_len + block);
    let mut hum = Hum::new(rate);
    let series = match &opts.mode {
        Mode::Replay(path) => Some(Series::load(path)),
        _ => None,
    };
    let decim_factor = (rate / 480.0).round().max(1.0) as usize;
    let mut decim_count = 0usize;

    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());
    let mut tee = opts.tee.as_ref().map(|p| {
        OpenOptions::new().create(true).append(true).open(p).unwrap_or_else(|e| {
            eprintln!("grid_ear: cannot open {p}: {e}");
            std::process::exit(2)
        })
    });
    let mut decimated = opts.decimated.as_ref().map(|p| {
        BufWriter::new(File::create(p).unwrap_or_else(|e| {
            eprintln!("grid_ear: cannot create {p}: {e}");
            std::process::exit(2)
        }))
    });

    let start_unix = now_unix();
    let start_instant = Instant::now();
    let total_samples = match &opts.mode {
        Mode::Wav(_) => samples_from_wav.as_ref().map(|s| s.len()).unwrap_or(0),
        Mode::Stdin => usize::MAX,
        _ => (opts.seconds * rate) as usize,
    };
    let mut stdin = io::stdin().lock();
    let mut byte_buf = vec![0u8; block * 4];
    let mut chunk = vec![0f32; block];
    let mut fed = 0usize;
    let mut tick_index = 0usize;
    let mut last_spectral: Option<(f32, f32)> = None;
    let mut wav_pos = 0usize;

    loop {
        // Fill one 50 ms chunk from the source.
        let got = match &opts.mode {
            Mode::Stdin => {
                let mut read = 0usize;
                while read < byte_buf.len() {
                    match stdin.read(&mut byte_buf[read..]) {
                        Ok(0) => break,
                        Ok(k) => read += k,
                        Err(e) if e.kind() == io::ErrorKind::Interrupted => continue,
                        Err(_) => break,
                    }
                }
                let n = read / 4;
                for i in 0..n {
                    chunk[i] = f32::from_le_bytes([
                        byte_buf[4 * i],
                        byte_buf[4 * i + 1],
                        byte_buf[4 * i + 2],
                        byte_buf[4 * i + 3],
                    ]);
                }
                n
            }
            Mode::Wav(_) => {
                let s = samples_from_wav.as_mut().unwrap();
                let n = block.min(s.len().saturating_sub(wav_pos));
                chunk[..n].copy_from_slice(&s[wav_pos..wav_pos + n]);
                wav_pos += n;
                n
            }
            _ => {
                let n = block.min(total_samples.saturating_sub(fed));
                for i in 0..n {
                    let t = (fed + i) as f64 / rate as f64;
                    let silent = matches!(opts.mode, Mode::Silence)
                        || opts.cut_at.map_or(false, |c| t >= c as f64);
                    let hz = match &opts.mode {
                        Mode::Tone(f) => {
                            let wobble = if opts.wobble {
                                0.020 * (2.0 * std::f64::consts::PI * 0.05 * t).sin()
                            } else {
                                0.0
                            };
                            *f as f64 + wobble
                        }
                        Mode::Replay(_) => series.as_ref().unwrap().at(t),
                        _ => NOMINAL_HZ as f64,
                    };
                    chunk[i] = hum.sample(hz, silent);
                }
                n
            }
        };
        if got == 0 {
            break;
        }

        for &x in &chunk[..got] {
            let band_out = ear.process(x);
            if let Some(d) = decimated.as_mut() {
                decim_count += 1;
                if decim_count >= decim_factor {
                    decim_count = 0;
                    let _ = writeln!(d, "{band_out:.7}");
                }
            }
        }
        ring.extend_from_slice(&chunk[..got]);
        if ring.len() > stft_len {
            let excess = ring.len() - stft_len;
            ring.drain(..excess);
        }
        fed += got;
        tick_index += 1;

        let reading = ear.tick();
        let harmonic = ear.harmonic();
        if tick_index % STFT_EVERY_TICKS == 0 && ring.len() >= stft_len / 2 {
            last_spectral = reading.and_then(|_| spectral.read(&ring, harmonic));
        }
        let t = match opts.mode {
            Mode::Stdin => now_unix(),
            _ => start_unix + fed as f64 / rate as f64,
        };
        let level_db = reading.map(|r| r.level_db).unwrap_or_else(|| {
            // Before lock the level is still a real number: the ear's band energy.
            -120.0
        });
        let line = format!(
            "{{\"t\":{t:.3},\"hz_fast\":{},\"hz\":{},\"hz_stft\":{},\"rocof\":{},\"thd\":{},\"level_db\":{:.1},\"harmonic\":{},\"source\":\"{}\"}}",
            fmt_opt(reading.map(|r| r.hz_fast), 4),
            fmt_opt(reading.map(|r| r.hz), 4),
            fmt_opt(last_spectral.map(|(h, _)| h), 4),
            fmt_opt(reading.map(|r| r.rocof), 3),
            fmt_opt(last_spectral.map(|(_, d)| d), 1),
            level_db,
            harmonic,
            source_label,
        );
        let _ = writeln!(out, "{line}");
        let _ = out.flush();
        if let Some(f) = tee.as_mut() {
            let _ = writeln!(f, "{line}");
            let _ = f.flush();
        }

        if opts.realtime {
            let due = start_instant + Duration::from_secs_f64(fed as f64 / rate as f64);
            let now = Instant::now();
            if due > now {
                sleep(due - now);
            }
        }
        if got < block && !matches!(opts.mode, Mode::Stdin) {
            break;
        }
    }
    if let Some(mut d) = decimated {
        let _ = d.flush();
    }
}
