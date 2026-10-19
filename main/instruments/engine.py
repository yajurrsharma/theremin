
import sys
from pathlib import Path
import fluidsynth


class Engine:
    _instance = None

    def __init__(self):

        if Engine._instance is not None:
            return

        Engine._instance = self

        self.fs = fluidsynth.Synth()

        if sys.platform == "win32":
            drivers = ["dsound", "wasapi", "portaudio"]
        else:
            drivers = ["pulseaudio", "alsa", "pipewire"]

        started = False

        for driver in drivers:
            try:
                print(f"Trying audio driver: {driver}")
                self.fs.start(driver=driver)
                print(f"Audio driver started: {driver}")
                started = True
                break
            except Exception as e:
                print(f"Could not start {driver}: {e}")

        if not started:
            try:
                self.fs.start()
                started = True
            except Exception as e:
                print(f"WARNING: Could not start audio: {e}")

        if getattr(sys, "frozen", False):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parent

        soundfont_path = base_dir / "instruments" / "TimGM6mb.sf2"


        if not getattr(sys, "frozen", False):
            soundfont_path = base_dir / "TimGM6mb.sf2"

        print(f"DEBUG: Frozen build: {getattr(sys, 'frozen', False)}")
        print(f"DEBUG: Base directory: {base_dir}")
        print(f"DEBUG: SoundFont path: {soundfont_path}")
        print(f"DEBUG: SoundFont exists: {soundfont_path.is_file()}")

        if not soundfont_path.is_file():
            raise FileNotFoundError(
                f"SoundFont file not found: {soundfont_path}"
            )

        self.sfid = self.fs.sfload(str(soundfont_path))

        print(f"DEBUG: Loaded SoundFont ID: {self.sfid}")

        if self.sfid == -1:
            raise RuntimeError(
                f"FluidSynth failed to load SoundFont: {soundfont_path}"
            )

    def get_synth(self):
        return self.fs


engine = Engine()
synth = engine.get_synth()
sfid = engine.sfid
