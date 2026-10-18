import fluidsynth


class Engine:

    _instance = None

    def __init__(self):

        if Engine._instance is None:
            settings = fluidsynth.new_settings()
            settings.setint("audio.periods", 8)
            settings.setint("audio.period-size", 1024)
            settings.setint("synth.polyphony", 512)
            
            self.fs = fluidsynth.Synth(settings=settings)

            try:
                self.fs.start()
            except Exception as e:
                print(f"failed: {e}")
                for driver in ["alsa", "pulseaudio", "jack", "oss", "dsound", "coreaudio"]:
                    try:
                        self.fs.start(driver=driver)
                        print(f"Successfully started audio using driver: {driver}")
                        break
                    except Exception:
                        continue
            self.sfid = self.fs.sfload("TimGM6mb.sf2")
            Engine._instance = self


    def get_synth(self):

        return self.fs


engine = Engine()
synth = engine.get_synth()
sfid = engine.sfid
