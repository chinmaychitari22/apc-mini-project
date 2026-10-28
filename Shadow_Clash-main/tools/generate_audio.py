"""SHADOW CLASH - Procedural Audio Asset Generator.

Generates high-quality 44.1kHz 16-bit stereo sound effects and looping music
tracks using NumPy and the standard wave module. Ensures 100% offline, standalone
audio asset availability without external binary dependencies.
"""

from __future__ import annotations
import math
from pathlib import Path
import struct
import wave
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "audio"
SAMPLE_RATE = 44100


def save_wave(filename: str, samples_left: np.ndarray, samples_right: np.ndarray | None = None) -> Path:
    """Save stereo or mono audio samples to 16-bit PCM WAV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / filename
    
    if samples_right is None:
        samples_right = samples_left
        
    # Clip to -1.0 to 1.0
    s_l = np.clip(samples_left, -1.0, 1.0)
    s_r = np.clip(samples_right, -1.0, 1.0)
    
    # Interleave and convert to int16
    int_l = (s_l * 32767).astype(np.int16)
    int_r = (s_r * 32767).astype(np.int16)
    interleaved = np.empty((len(int_l) * 2,), dtype=np.int16)
    interleaved[0::2] = int_l
    interleaved[1::2] = int_r
    
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(interleaved.tobytes())
        
    return out_path


def gen_light_punch() -> None:
    """Crisp martial snap with fast impact thud."""
    duration = 0.16
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Quick pitch sweep from 240Hz down to 60Hz
    freq = 240.0 * np.exp(-t * 28.0)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    body = np.sin(phase)
    # Noise burst for the whip/fist snap
    noise = np.random.uniform(-1.0, 1.0, len(t))
    noise_env = np.exp(-t * 45.0)
    env = np.exp(-t * 22.0)
    sig = (body * 0.7 + noise * noise_env * 0.45) * env
    save_wave("light_punch.wav", sig)


def gen_heavy_punch() -> None:
    """Deep concussive punch with sub-bass impact and bone shock."""
    duration = 0.28
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = 180.0 * np.exp(-t * 16.0) + 40.0
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    body = np.sin(phase) + 0.3 * np.sin(phase * 0.5)
    # Distorted crunch
    body = np.tanh(body * 1.8)
    noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 30.0)
    env = np.exp(-t * 12.0)
    sig = (body * 0.8 + noise * 0.4) * env
    save_wave("heavy_punch.wav", sig)


def gen_kick() -> None:
    """Solid martial arts kick impact with snappy whoosh."""
    duration = 0.22
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = 210.0 * np.exp(-t * 20.0) + 45.0
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    body = np.sin(phase) + 0.25 * np.sin(phase * 2.0)
    noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 35.0)
    env = np.exp(-t * 16.0)
    sig = (body * 0.75 + noise * 0.35) * env
    save_wave("kick.wav", sig)


def gen_heavy_kick() -> None:
    """Heavy spin kick with sweeping whoosh and explosive impact."""
    duration = 0.32
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = 160.0 * np.exp(-t * 14.0) + 38.0
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    body = np.sin(phase) + 0.4 * np.sin(phase * 1.5)
    body = np.tanh(body * 2.0)
    noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 24.0)
    env = np.exp(-t * 10.0)
    sig = (body * 0.85 + noise * 0.4) * env
    save_wave("heavy_kick.wav", sig)


def gen_block() -> None:
    """Metallic/wood solid guard deflection with resonant ring."""
    duration = 0.25
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Clang frequencies
    clang = (np.sin(2 * np.pi * 580 * t) * 0.5 +
             np.sin(2 * np.pi * 920 * t) * 0.35 +
             np.sin(2 * np.pi * 1420 * t) * 0.2)
    noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 50.0)
    env = np.exp(-t * 18.0)
    sig = (clang * 0.7 + noise * 0.4) * env
    save_wave("block.wav", sig)


def gen_weapon_strike() -> None:
    """Razor-sharp blade slice slash sound."""
    duration = 0.26
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Sharp whoosh plus metallic scrape
    freq = 1200.0 * np.exp(-t * 18.0) + 300.0
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    blade = np.sin(phase) * 0.4 + np.sin(phase * 2.2) * 0.25
    noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 20.0)
    env = np.exp(-t * 14.0)
    sig = (blade * 0.5 + noise * 0.6) * env
    save_wave("weapon_strike.wav", sig)


def gen_jump() -> None:
    """Swift whoosh for leap."""
    duration = 0.18
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = 100.0 + 350.0 * (t / duration)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    whoosh = np.sin(phase) * 0.4
    noise = np.random.uniform(-1.0, 1.0, len(t)) * 0.35
    env = np.sin(np.pi * (t / duration))  # smooth rise and fall
    sig = (whoosh + noise) * env * 0.55
    save_wave("jump.wav", sig)


def gen_land() -> None:
    """Solid footing ground landing."""
    duration = 0.15
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = 110.0 * np.exp(-t * 30.0)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    thud = np.sin(phase) * 0.7
    noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 40.0) * 0.4
    env = np.exp(-t * 25.0)
    sig = (thud + noise) * env * 0.7
    save_wave("land.wav", sig)


def gen_special_charge() -> None:
    """Rising mystical energy hum."""
    duration = 0.55
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = 120.0 + 520.0 * (t / duration)**1.8
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    shimmer = np.sin(phase) + 0.35 * np.sin(phase * 1.5) + 0.2 * np.sin(phase * 2.0)
    env = (t / duration) * np.exp(-(duration - t) * 3.0) + (t / duration)**2 * 0.6
    sig = shimmer * env * 0.6
    save_wave("special_charge.wav", sig)


def gen_special_attack() -> None:
    """Explosive Shadow Burst blast wave with bass detonation."""
    duration = 0.65
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Sub boom
    boom_freq = 140.0 * np.exp(-t * 7.0) + 30.0
    boom = np.sin(2 * np.pi * np.cumsum(boom_freq) / SAMPLE_RATE)
    boom = np.tanh(boom * 2.2)
    # Energy crackle
    crackle = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 8.0)
    # Ethereal harmonic
    ethereal = np.sin(2 * np.pi * 440.0 * t) * np.exp(-t * 5.0) * 0.3
    env = np.exp(-t * 5.5)
    sig = (boom * 0.7 + crackle * 0.45 + ethereal) * env
    save_wave("special_attack.wav", sig)


def gen_victory() -> None:
    """Triumphant resonant bronze gong and martial harmony."""
    duration = 2.2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Eastern pentatonic gong chords (A, C, D, E, G)
    notes = [220.0, 261.6, 293.7, 329.6, 392.0]
    chord = np.zeros_like(t)
    for i, f in enumerate(notes):
        # Slightly staggered attack
        offset = i * 0.08
        mask = t >= offset
        t_sub = t[mask] - offset
        chord[mask] += np.sin(2 * np.pi * f * t_sub) * np.exp(-t_sub * 1.4) * (1.0 / (i + 1.2))
    gong = np.sin(2 * np.pi * 110.0 * t) * np.exp(-t * 1.1) * 0.5
    sig = (chord * 0.6 + gong * 0.5) * 0.8
    save_wave("victory.wav", sig)


def gen_defeat() -> None:
    """Somber low drone and descending bell."""
    duration = 2.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    drone = (np.sin(2 * np.pi * 65.4 * t) * 0.5 + 
             np.sin(2 * np.pi * 98.0 * t) * 0.35) * np.exp(-t * 0.9)
    bell_freq = 180.0 * np.exp(-t * 0.6)
    bell = np.sin(2 * np.pi * np.cumsum(bell_freq) / SAMPLE_RATE) * np.exp(-t * 1.8) * 0.35
    sig = (drone + bell) * 0.75
    save_wave("defeat.wav", sig)


def gen_ui_sounds() -> None:
    """Generate crisp UI click and hover sound effects."""
    # Click: snappy wooden/bamboo clack
    dur = 0.08
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    click = np.sin(2 * np.pi * 880 * t) * np.exp(-t * 70.0) + np.random.uniform(-1, 1, len(t)) * np.exp(-t * 90.0) * 0.3
    save_wave("menu_click.wav", click * 0.6)
    
    # Hover: subtle soft chime
    dur_h = 0.06
    th = np.linspace(0, dur_h, int(SAMPLE_RATE * dur_h), endpoint=False)
    hover = np.sin(2 * np.pi * 660 * th) * np.exp(-th * 55.0) * 0.35
    save_wave("menu_hover.wav", hover)


def gen_bgm_track(filename: str, tempo_bpm: float, duration_sec: float, track_type: str = "combat") -> None:
    """Synthesize seamless looping martial arts battle / ambient tracks."""
    num_samples = int(SAMPLE_RATE * duration_sec)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    beat_sec = 60.0 / tempo_bpm
    sub_beat = beat_sec / 2.0
    
    left = np.zeros(num_samples)
    right = np.zeros(num_samples)
    
    # Taiko / percussion drum pattern
    num_beats = int(duration_sec / sub_beat)
    for b in range(num_beats):
        b_time = b * sub_beat
        idx_start = int(b_time * SAMPLE_RATE)
        drum_dur = 0.35
        drum_samples = min(int(drum_dur * SAMPLE_RATE), num_samples - idx_start)
        if drum_samples <= 0:
            continue
            
        dt_arr = np.linspace(0, drum_dur, drum_samples, endpoint=False)
        
        # Heavy Taiko on downbeats
        if b % 4 == 0:
            freq = 75.0 * np.exp(-dt_arr * 16.0) + 38.0
            drum = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE) * np.exp(-dt_arr * 8.0) * 0.7
            left[idx_start:idx_start + drum_samples] += drum * 0.65
            right[idx_start:idx_start + drum_samples] += drum * 0.65
        elif b % 2 == 0:
            # Medium rim / tom
            freq = 130.0 * np.exp(-dt_arr * 22.0) + 50.0
            drum = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE) * np.exp(-dt_arr * 14.0) * 0.45
            left[idx_start:idx_start + drum_samples] += drum * 0.5
            right[idx_start:idx_start + drum_samples] += drum * 0.3
        else:
            # Shaker / hi-hat
            shaker = np.random.uniform(-0.15, 0.15, drum_samples) * np.exp(-dt_arr * 35.0)
            left[idx_start:idx_start + drum_samples] += shaker * 0.3
            right[idx_start:idx_start + drum_samples] += shaker * 0.45
            
    # Bassline (E minor martial groove: E, G, A, B)
    if track_type == "boss":
        bass_notes = [41.2, 49.0, 55.0, 41.2, 43.65, 41.2, 61.7, 55.0]  # E1, G1, A1, F1, B1
    elif track_type == "menu":
        bass_notes = [55.0, 65.4, 73.4, 82.4]  # A1, C2, D2, E2 ambient
    else:
        bass_notes = [41.2, 41.2, 49.0, 55.0, 41.2, 61.7, 55.0, 49.0]
        
    bar_sec = beat_sec * 4.0
    num_bars = int(duration_sec / bar_sec)
    for bar in range(num_bars):
        for step in range(len(bass_notes)):
            step_time = bar * bar_sec + step * (bar_sec / len(bass_notes))
            idx_start = int(step_time * SAMPLE_RATE)
            note_dur = (bar_sec / len(bass_notes)) * 0.85
            note_samples = min(int(note_dur * SAMPLE_RATE), num_samples - idx_start)
            if note_samples <= 0:
                continue
            nt = np.linspace(0, note_dur, note_samples, endpoint=False)
            freq = bass_notes[step]
            # Sawtooth + sine bass
            saw = (2.0 * (freq * nt - np.floor(0.5 + freq * nt))) * 0.25
            sub = np.sin(2 * np.pi * freq * nt) * 0.5
            bass_env = np.sin(np.pi * (nt / note_dur))**0.6
            b_sig = (saw + sub) * bass_env * 0.55
            left[idx_start:idx_start + note_samples] += b_sig * 0.55
            right[idx_start:idx_start + note_samples] += b_sig * 0.55
            
    # Ambient pad / flute melody
    drone_freq = 164.81 if track_type != "menu" else 220.0  # E3 or A3
    pad = (np.sin(2 * np.pi * drone_freq * t) * 0.2 +
           np.sin(2 * np.pi * (drone_freq * 1.5) * t) * 0.12 +
           np.sin(2 * np.pi * (drone_freq * 2.0) * t) * 0.08)
    # Slow LFO panning
    pan_l = 0.5 + 0.3 * np.sin(2 * np.pi * 0.2 * t)
    pan_r = 0.5 - 0.3 * np.sin(2 * np.pi * 0.2 * t)
    left += pad * pan_l * 0.4
    right += pad * pan_r * 0.4
    
    # Soft limiter / normalization
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 0.001)
    if peak > 0.95:
        left = left / peak * 0.92
        right = right / peak * 0.92
        
    save_wave(filename, left, right)


def generate_all_audio() -> list[Path]:
    """Generate the full suite of required audio assets."""
    print("Generating sound effects...")
    gen_light_punch()
    gen_heavy_punch()
    gen_kick()
    gen_heavy_kick()
    gen_block()
    gen_weapon_strike()
    gen_jump()
    gen_land()
    gen_special_charge()
    gen_special_attack()
    gen_victory()
    gen_defeat()
    gen_ui_sounds()
    
    print("Generating looping battle & menu music tracks...")
    # Loopable 8-second combat track at 130 BPM
    gen_bgm_track("bgm_combat.wav", tempo_bpm=128.0, duration_sec=7.5, track_type="combat")
    # Boss track at 144 BPM
    gen_bgm_track("bgm_boss.wav", tempo_bpm=140.0, duration_sec=6.857, track_type="boss")
    # Ambient menu track at 90 BPM
    gen_bgm_track("bgm_menu.wav", tempo_bpm=90.0, duration_sec=8.0, track_type="menu")
    
    print(f"All audio files generated in {OUTPUT_DIR}")
    return list(OUTPUT_DIR.glob("*.wav"))


if __name__ == "__main__":
    generate_all_audio()
