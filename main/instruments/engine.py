import fluidsynth
import sys


class Engine:

    _instance = None

    def __init__(self):

        if Engine._instance is None:
            self.fs = fluidsynth.Synth()

            if sys.platform == "win32":
                drivers = ["dsound", "wasapi", "portaudio"]
            else:
                drivers = ["alsa", "pulseaudio"]

            started = False
            for driver in drivers:
                try:
                    self.fs.start(driver=driver)
                    started = True
                    break
                except Exception:
                    continue
            if not started:
                try:
                    self.fs.start()
                except Exception as e:
                    print(f"Warning: Could not start default audio driver: {e}")
                    
            self.sfid = self.fs.sfload("TimGM6mb.sf2")
            Engine._instance = self


    def get_synth(self):

        return self.fs


engine = Engine()
synth = engine.get_synth()
sfid = engine.sfid
