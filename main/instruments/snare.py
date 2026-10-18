from engine import synth

class Snare:

    def __init__(self):

        self.track = 9
        self.note = 38


    def hit(self, v=110):
        synth.noteon(self.track, self.note, int(v))