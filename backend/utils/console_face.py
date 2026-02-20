"""Console face animation utility for MCP Helper."""
import sys
import time
import random
import threading
import os

# Enable ANSI escape codes on Windows
if sys.platform == 'win32':
    os.system("")

# ══════════════════════════════════════
# ANSI Color Codes
# ══════════════════════════════════════
CYAN    = "\033[96m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
WHITE   = "\033[97m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"
CLEAR   = "\033[K"

# ══════════════════════════════════════
# Big Face Frames (for boot & response)
# ══════════════════════════════════════
FACE_NORMAL = [
    "      .----------.",
    "      |  O    O  |",
    "      |    <>    |",
    "      |   ----   |",
    "      '----------'",
]

FACE_BLINK = [
    "      .----------.",
    "      |  -    -  |",
    "      |    <>    |",
    "      |   ----   |",
    "      '----------'",
]

FACE_TALK_1 = [
    "      .----------.",
    "      |  O    O  |",
    "      |    <>    |",
    "      |   (  )   |",
    "      '----------'",
]

FACE_TALK_2 = [
    "      .----------.",
    "      |  O    O  |",
    "      |    <>    |",
    "      |   (oo)   |",
    "      '----------'",
]

FACE_THINK = [
    "      .----------.",
    "      |  o    O  |",
    "      |    <>    |",
    "      |   ~~~~   |",
    "      '----------'",
]

FACE_HAPPY = [
    "      .----------.",
    "      |  ^    ^  |",
    "      |    <>    |",
    "      |   \\__/   |",
    "      '----------'",
]

FACE_ERROR = [
    "      .----------.",
    "      |  X    X  |",
    "      |    <>    |",
    "      |   /--\\   |",
    "      '----------'",
]

FACE_HEIGHT = len(FACE_NORMAL)

# ══════════════════════════════════════
# Inline Face Emojis (for status lines)
# ══════════════════════════════════════
INLINE = {
    "normal":    "(O_O)",
    "blink":     "(-_-)",
    "talk":      "(O_o)",
    "think":     "(o_~)",
    "happy":     "(^_^)",
    "error":     "(X_X)",
    "surprise":  "(O_O)!",
}


class ConsoleFace:
    """Animated ASCII face for console interactions."""

    def __init__(self, name="MCP"):
        self.name = name
        self._stop_event = threading.Event()
        self._anim_thread = None

    # ──────────────────────────────────
    # BOOT ANIMATION
    # ──────────────────────────────────
    def boot(self):
        """Show boot sequence with blinking face."""
        width = 32
        print(f"\n{BOLD}{CYAN}{'=' * width}{RESET}")

        # Print face
        for line in FACE_NORMAL:
            print(f"{CYAN}{line}{RESET}")
        print(f"{CYAN}{'':>6}{BOLD}{self.name}{RESET}")
        print(f"{BOLD}{CYAN}{'=' * width}{RESET}")

        # Blink animation
        time.sleep(0.5)
        self._redraw_face(FACE_BLINK, CYAN)
        time.sleep(0.15)
        self._redraw_face(FACE_NORMAL, CYAN)
        time.sleep(0.6)
        self._redraw_face(FACE_BLINK, CYAN)
        time.sleep(0.12)
        self._redraw_face(FACE_NORMAL, CYAN)
        print()

    def _redraw_face(self, frame, color):
        """Redraw face in-place (cursor moves up, redraws, moves back)."""
        up = FACE_HEIGHT + 2  # face + name + bottom separator
        sys.stdout.write(f"\033[{up}A")
        for line in frame:
            sys.stdout.write(f"\r{CLEAR}{color}{line}{RESET}\n")
        sys.stdout.write(f"\033[2B")  # skip name + separator
        sys.stdout.flush()

    # ──────────────────────────────────
    # THINKING ANIMATION (background)
    # ──────────────────────────────────
    def start_thinking(self, msg="Thinking"):
        """Start animated thinking indicator in background."""
        self._stop_event.clear()
        frames = [
            f"{INLINE['think']}",
            f"{INLINE['blink']}",
            f"{INLINE['think']}",
            f"{INLINE['normal']}",
        ]

        def animate():
            i = 0
            while not self._stop_event.is_set():
                face = frames[i % len(frames)]
                dots = "." * ((i % 3) + 1) + "  "
                sys.stdout.write(f"\r{CLEAR}{YELLOW}{face} {msg}{dots}{RESET}")
                sys.stdout.flush()
                i += 1
                self._stop_event.wait(0.35)
            # Clear the animation line
            sys.stdout.write(f"\r{CLEAR}")
            sys.stdout.flush()

        self._anim_thread = threading.Thread(target=animate, daemon=True)
        self._anim_thread.start()

    def stop_thinking(self):
        """Stop the thinking animation."""
        self._stop_event.set()
        if self._anim_thread:
            self._anim_thread.join(timeout=2)
            self._anim_thread = None

    # ──────────────────────────────────
    # TYPED PRINT (talking effect)
    # ──────────────────────────────────
    def typed_print(self, text, speed=0.018):
        """Print text character by character with face state changes."""
        talk_faces = [INLINE["talk"], INLINE["normal"]]
        toggle = 0
        char_count = 0

        # Show talking face before text
        sys.stdout.write(f"{GREEN}{BOLD}")
        sys.stdout.flush()

        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            char_count += 1

            # Speed varies slightly for natural feel
            delay = speed + random.uniform(-0.005, 0.01)

            # Faster for spaces and punctuation
            if char == ' ':
                delay = speed * 0.3
            elif char == '\n':
                delay = speed * 2
            elif char in '.!?':
                delay = speed * 4  # Pause at sentences

            time.sleep(max(0.002, delay))

        sys.stdout.write(f"{RESET}\n")
        sys.stdout.flush()

    # ──────────────────────────────────
    # STATUS OUTPUT
    # ──────────────────────────────────
    def status(self, msg, state="normal", color=CYAN):
        """Print a status message with inline face."""
        face = INLINE.get(state, INLINE["normal"])
        print(f"{color}{face} {msg}{RESET}", flush=True)

    def success(self, msg):
        self.status(msg, "happy", GREEN)

    def error(self, msg):
        self.status(msg, "error", RED)

    def info(self, msg):
        self.status(msg, "normal", CYAN)

    # ──────────────────────────────────
    # PROMPT
    # ──────────────────────────────────
    def get_prompt(self):
        """Return the styled input prompt string."""
        return f"\n{CYAN}{INLINE['normal']}{RESET} {BOLD}You:{RESET} "

    # ──────────────────────────────────
    # RESPONSE WRAPPER
    # ──────────────────────────────────
    def respond(self, text):
        """Full response: face label + typed text."""
        print(f"\n{GREEN}{BOLD}{INLINE['talk']} Assistant:{RESET}")
        self.typed_print(text)
        # End with happy face
        print(f"{DIM}{CYAN}{INLINE['happy']}{RESET}", flush=True)


# ══════════════════════════════════════
# Singleton instance
# ══════════════════════════════════════
face = ConsoleFace("MCP")
