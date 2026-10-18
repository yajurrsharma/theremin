# # import time
# # import fluidsynth

# # fs = fluidsynth.Synth()
# # fs.start(driver="alsa")

# # sfid = fs.sfload("/usr/share/sounds/sf2/TimGM6mb.sf2")
# # fs.program_select(0, sfid, 0, 80)

# # try:
# #     midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]
    
# #     for note in midi_notes:
# #         fs.noteon(0, note, 100)
# #         time.sleep(0.4)
# #         fs.noteoff(0, note)
        
# # finally:
# #     fs.delete() 


# import time
# from synth import Synth
# from bass import Bass
# from hihat import HiHat
# from kickdrum import KickDrum
# from snare import Snare

# synth = Synth(track=0, program=80)
# bass = Bass(track=1, program=38)
# hihat = HiHat()
# kickdrum = KickDrum()
# snare = Snare()

# try:

#     print("first beat")
#     kickdrum.hit(120)
#     hihat.hit_close(100)
#     bass.note_on(36, 100)
#     synth.note_on(60, 100)
#     time.sleep(0.5)
#     synth.note_off()  
#     bass.note_off()

#     print("second beat")
#     kickdrum.hit(120)
#     hihat.hit_open(100)
#     bass.note_on(38, 100)
#     synth.note_on(62, 100)
#     time.sleep(0.5)
#     synth.note_off()
#     bass.note_off()


# finally:
#     synth.note_off()
#     bass.note_off()


