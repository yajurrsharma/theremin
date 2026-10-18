from engine import synth, sfid

class HiHat:

    def __init__(self):

        self.track = 9
        self.closed_note = 42
        self.open_note = 46
        synth.program_select(self.track, sfid, 128, 0)


    def hit_close(self, v=100):

        synth.noteoff(self.track, self.closed_note)
        synth.noteon(self.track, self.closed_note, int(v))

    def hit_open(self, v=100):

        synth.noteon(self.track, self.open_note, int(v))

