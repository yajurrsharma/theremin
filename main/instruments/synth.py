from engine import synth

class Synth:

    def __init__ (self, track=0, program=80):

        self.track = track
        synth.program_select(self.track, synth.sfload("TimGM6mb.sf2"), 0, program)
        self.current_note = None


    def note_on(self, note, v=100):

        if self.current_note and self.current_note != note:
            synth.noteoff(self.track, self.current_note)

        synth.noteon(self.track, note, v)

        self.current_note = note

    def note_off(self):

        if self.current_note:
            synth.noteoff(self.track, self.current_note)
            self.current_note = None


    def pitch_bend(self, value):

        synth.pitch_bend(self.track, int(value))

    def set_expression(self, value):

        synth.cc(self.track, 11, int(value))

