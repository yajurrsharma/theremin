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



# import cv2
# import mediapipe as mp
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision

# base_options = python.BaseOptions(model_asset_path='main/hand_landmarker.task')
# options = vision.HandLandmarkerOptions(
#     base_options=base_options,
#     num_hands=2,
#     running_mode=vision.RunningMode.IMAGE
# )

# detector = vision.HandLandmarker.create_from_options(options)

# cap = cv2.VideoCapture(0)

# try:
#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             print("empty camera frame")
#             continue

#         frame = cv2.flip(frame, 1)
#         h,w,c = frame.shape

#         mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

#         results = detector.detect(mp_image)

#         if results.hand_landmarks:

#            for idx, hand_landmarks in enumerate(results.hand_landmarks):

#                 raw_label = results.handedness[idx][0].category_name
#                 hand_label = "Right" if raw_label == "Left" else "Left"

#                 index = hand_landmarks[8]
#                 x_px, y_px = int(index.x * w), int(index.y * h)

            
#                 cv2.putText(frame, f"{hand_label} hand", (x_px - 20, y_px - 20),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#                 cv2.circle(frame, (x_px, y_px), 8, (0, 0, 255), -1)

        
#         cv2.imshow("Hand Tracking", frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# finally:
#     cap.release()
#     cv2.destroyAllWindows()