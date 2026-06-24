"""
Generation of GIF for DIYA illumination protocol with DELAYED HALF-PANEL
===========================================
This code allows to create a GIF without passing by DIYA GUI Software, which is useful for automation and reproducibility.
The generated GIF will follow the protocol described in the DIYA documentation, with a first pulse of 5 minutes ON, followed by cycles of 5 minutes OFF and 10 seconds ON, repeated until the total duration is reached.

SPECIAL FEATURE: The RIGHT HALF of the LED panel is delayed by 2 hours relative to the LEFT HALF.
- LEFT HALF:  follows the protocol from start (immediate)
- RIGHT HALF: black (OFF) for 2 hours, then follows the same protocol

- Frames ON  : red light (R=255, G=0, B=0)
- Frames OFF : black light (R=0,   G=0, B=0)

Workflow after generation :
  1. Convert the GIF to MP4 (VLC or ffmpeg)
  2. Send via HDPlayer to the DIYA machine

Dependency : pip install pillow
"""

from PIL import Image
# ══════════════════════════════════════════════════
#  VARIABLE PARAMETERS
# ══════════════════════════════════════════════════
OUTPUT_FILE      = r'C:\Users\canne\Downloads\protocol_delayed.gif'
TOTAL_MIN        = 1435   # Total duration of cycles in minutes (without the initial pulse)
CYCLE_SEC        = 130   # Duration of a complete cycle ON+OFF in seconds (300 = 5 min)
ON_SEC           = 10    # Duration of ON pulses in seconds (except the first one)
FIRST_PULSE_SEC  = 300   # Duration of the first pulse in seconds (300 = 5 min)
FPS              = 1     # frames per second (1 = 1 frame per second, do not change)
DELAY_SEC        = 7200  # Delay for the right half in seconds (7200 = 2 hours)
# ══════════════════════════════════════════════════

OFF_SEC    = CYCLE_SEC - ON_SEC
IMG_SIZE   = (64, 64)
HALF_SIZE  = (32, 64)

# Color definitions
RED   = (255, 0, 0)
BLACK = (0, 0, 0)

def create_composite_frame(left_state, right_state):
    """Create a frame with different states on left and right halves"""
    left_color = RED if left_state == 'ON' else BLACK
    right_color = RED if right_state == 'ON' else BLACK
    
    frame = Image.new('RGB', IMG_SIZE, BLACK)
    left_half = Image.new('RGB', HALF_SIZE, left_color)
    right_half = Image.new('RGB', HALF_SIZE, right_color)
    frame.paste(left_half, (0, 0))
    frame.paste(right_half, (32, 0))
    return frame

def generate_protocol_states(duration_sec, first_pulse_sec):
    """Generate list of (on/off) states for the protocol"""
    protocol = []
    
    # First pulse: ON
    n = int(first_pulse_sec * FPS)
    protocol.extend(['ON'] * n)
    
    # Cycles: OFF then ON
    total_sec = duration_sec
    n_cycles = total_sec // CYCLE_SEC
    remaining = total_sec % CYCLE_SEC
    
    for i in range(int(n_cycles)):
        # OFF phase
        n = int(OFF_SEC * FPS)
        protocol.extend(['OFF'] * n)
        # ON phase
        n = int(ON_SEC * FPS)
        protocol.extend(['ON'] * n)
    
    if remaining >= ON_SEC:
        n = int(OFF_SEC * FPS)
        protocol.extend(['OFF'] * n)
        n = int(ON_SEC * FPS)
        protocol.extend(['ON'] * n)
        leftover = remaining - ON_SEC
        if leftover > 0:
            n = int(leftover * FPS)
            protocol.extend(['OFF'] * n)
    
    return protocol

frames   = []
durations = []

# Generate protocol states
total_cycle_sec = TOTAL_MIN * 60
protocol = generate_protocol_states(total_cycle_sec, FIRST_PULSE_SEC)

# Total duration including the delay
total_duration_with_delay = DELAY_SEC + FIRST_PULSE_SEC + total_cycle_sec

print(f"╔════════════════════════════════════════════╗")
print(f"║  DIYA Protocol - LEFT/RIGHT DELAYED HALF   ║")
print(f"╚════════════════════════════════════════════╝\n")
print(f"LEFT HALF (immediate start):")
print(f"  Pulse initial : ON {FIRST_PULSE_SEC}s ({FIRST_PULSE_SEC//60} min)")
print(f"  Then {TOTAL_MIN} min of cycles (OFF {OFF_SEC}s → ON {ON_SEC}s)\n")
print(f"RIGHT HALF (delayed by {DELAY_SEC//3600}h = {DELAY_SEC//60} min):")
print(f"  First {DELAY_SEC//3600}h : OFF (black)")
print(f"  Then same protocol as LEFT HALF\n")

# ── BUILD FRAMES ─────────────────────────────────

# Phase 1: LEFT advances through protocol, RIGHT is OFF (waiting)
delay_frames = int(DELAY_SEC * FPS)
print(f"  Building Phase 1: {delay_frames} frames (~{DELAY_SEC//60} min delay)...")
print(f"    LEFT progresses in protocol | RIGHT remains OFF")
for i in range(delay_frames):
    if i < len(protocol):
        left_state = protocol[i]
    else:
        left_state = 'OFF'
    right_state = 'OFF'
    frames.append(create_composite_frame(left_state, right_state))
    durations.append(int(1000 / FPS))

# Phase 2: LEFT continues where it was, RIGHT starts ITS OWN complete protocol
print(f"  Building Phase 2: LEFT continues + RIGHT starts its protocol...")
print(f"    LEFT at position {delay_frames} in its protocol")
print(f"    RIGHT begins its full protocol (5 min initial + cycles)")
for i in range(len(protocol)):
    # LEFT: continues from where it was (at delay_frames index)
    left_index = delay_frames + i
    if left_index < len(protocol):
        left_state = protocol[left_index]
    else:
        left_state = 'OFF'
    
    # RIGHT: starts its complete protocol from index 0
    right_state = protocol[i]
    
    frames.append(create_composite_frame(left_state, right_state))
    durations.append(int(1000 / FPS))

# ── SAVING OF THE GIF ─────────────────────────────
print(f"\nSaving GIF...")
frames[0].save(
    OUTPUT_FILE,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0
)

total_duration = DELAY_SEC + FIRST_PULSE_SEC + total_cycle_sec
print(f"\n✓ GIF generated : {OUTPUT_FILE}")
print(f"  {len(frames)} frames in total")
print(f"  Total duration : {total_duration // 3600}h {(total_duration % 3600) // 60}m\n")

left_protocol_duration = FIRST_PULSE_SEC + total_cycle_sec
right_total_duration = DELAY_SEC + FIRST_PULSE_SEC + total_cycle_sec

print(f"Timeline:")
print(f"  ┌─ LEFT HALF ────────────────────────────────┐")
print(f"  │ t=0h 0m      : Starts protocol (5 min + cycles)")
print(f"  │ t=0h 5m      : Enters cycle phase")
print(f"  │ t≈{left_protocol_duration // 3600}h {(left_protocol_duration % 3600) // 60}m       : Completes (all done)")
print(f"  └─────────────────────────────────────────────┘")
print(f"")
print(f"  ┌─ RIGHT HALF ───────────────────────────────┐")
print(f"  │ t=0h 0m      : OFF (waiting)")
print(f"  │ t=2h 0m      : Starts protocol (5 min + cycles)")
print(f"  │ t=2h 5m      : Enters cycle phase")
print(f"  │ t≈{right_total_duration // 3600}h {(right_total_duration % 3600) // 60}m       : Completes")
print(f"  └─────────────────────────────────────────────┘")
print(f"\n  🎯 Key point: RIGHT has its OWN 5-min initial pulse (not biased by LEFT)")
print(f"\nNext steps :")
print(f"  1. Convert to MP4 (ffmpeg or VLC)")
print(f"  2. Send via HDPlayer to DIYA")
