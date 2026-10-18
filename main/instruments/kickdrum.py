from engine import synth, sfid


class KickDrum:

    def __init__(self):

        self.track = 9
        self.note = 36
        synth.program_select(self.track, sfid, 128, 0)

    def hit(self, v=120):

        synth.noteon(self.track, self.note, int(v))

