from engine import synth, sfid

class Bass:

    def __init__(self, track=1, program=38):

        self.track = track
        synth.program_select(self.track, sfid, 0, program)
        self.current_note = None


    def note_on(self, note, v=100):

        if self.current_note is not None and self.current_note != note:
            synth.noteoff(self.track, self.current_note)

        synth.noteon(self.track, note, int(v))
        self.current_note = note

    def note_off(self):
        if self.current_note:
            synth.noteoff(self.track, self.current_note)
            self.current_note = None