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
