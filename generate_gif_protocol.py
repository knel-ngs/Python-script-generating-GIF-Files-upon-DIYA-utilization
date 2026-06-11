"""
Generation of GIF for DIYA illumination protocol
===========================================
This code allows to create a GIF without passing by DIYA GUI Software, which is useful for automation and reproducibility.
The generated GIF will follow the protocol described in the DIYA documentation, with a first pulse of 5 minutes ON, followed by cycles of 5 minutes OFF and 10 seconds ON, repeated until the total duration is reached.
- Frames ON  : entire LED pannel displaying red light (R=255, G=0, B=0)
- Frames OFF : entire LED pannel displaying black light (R=0,   G=0, B=0)

Workflow after generation :
  1. Convert the GIF to MP4 (VLC or ffmpeg)
  2. Send via HDPlayer to the DIYA machine

Dependency : pip install pillow
"""

from PIL import Image

# ══════════════════════════════════════════════════
#  VARIABLE PARAMETERS
# ══════════════════════════════════════════════════
OUTPUT_FILE      = r'C:\Users\canne\Downloads\protocol.gif'
TOTAL_MIN        = 360   # Total duration of cycles in minutes (without the initial pulse)
CYCLE_SEC        = 310   # Duration of a complete cycle ON+OFF in seconds (300 = 5 min)
ON_SEC           = 10    # Duration of ON pulses in seconds (except the first one)
FIRST_PULSE_SEC  = 300   # Duration of the first pulse in seconds (300 = 5 min)
FPS              = 1     # frames per second (1 = 1 frame per second, do not change)
# ══════════════════════════════════════════════════

OFF_SEC    = CYCLE_SEC - ON_SEC
IMG_SIZE   = (64, 64)
FRAME_ON   = Image.new('RGB', IMG_SIZE, (255, 0, 0))   # red
FRAME_OFF  = Image.new('RGB', IMG_SIZE, (0,   0, 0))   # black

def frames_for_duration(sec, frame):
    """Returns a list of frames for a given duration in seconds"""
    return [frame] * int(sec * FPS)

frames   = []
durations = []  # duration of each frame in ms

def add_frames(sec, frame):
    n = int(sec * FPS)
    frames.extend([frame] * n)
    durations.extend([int(1000 / FPS)] * n)

# ── FIRST PULSE : 5 min ON ──────────────────────
print(f"  Pulse initial : ON {FIRST_PULSE_SEC}s ({FIRST_PULSE_SEC//60} min)")
add_frames(FIRST_PULSE_SEC, FRAME_ON)

# ── CYCLES : OFF then ON ──────────────────────────
total_sec = TOTAL_MIN * 60
n_cycles  = total_sec // CYCLE_SEC
remaining = total_sec % CYCLE_SEC

for i in range(int(n_cycles)):
    print(f"  Cycle {i+1:02d} : OFF {OFF_SEC}s → ON {ON_SEC}s")
    add_frames(OFF_SEC, FRAME_OFF)
    add_frames(ON_SEC,  FRAME_ON)

if remaining >= ON_SEC:
    add_frames(OFF_SEC, FRAME_OFF)
    add_frames(ON_SEC,  FRAME_ON)
    leftover = remaining - ON_SEC
    if leftover > 0:
        add_frames(leftover, FRAME_OFF)

# ── SAVING OF THE GIF ─────────────────────────────
frames[0].save(
    OUTPUT_FILE,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0
)

total_duration = FIRST_PULSE_SEC + TOTAL_MIN * 60
print(f"\nGIF generated : {OUTPUT_FILE}")
print(f"  {len(frames)} frames in total")
print(f"  Total duration : {total_duration // 60} min")
print(f"  ({FIRST_PULSE_SEC//60} min initial pulse + {TOTAL_MIN} min cycles)")
print(f"\nNext steps :")
print(f"  1. Convert to MP4")
print(f"  2. Send via HDPlayer")
