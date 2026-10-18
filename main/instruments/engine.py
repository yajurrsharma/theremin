import fluidsynth


class Engine:

    _instance = None

    def __init__(self):

        if Engine._instance is None:
            self.fs = fluidsynth.Synth()
            self.fs.start(driver="alsa")
            self.sfid = self.fs.sfload("/usr/share/sounds/sf2/TimGM6mb.sf2")
            Engine._instance = self


    def get_synth(self):

        return self.fs


engine = Engine()
synth = engine.get_synth()
sfid = engine.sfid