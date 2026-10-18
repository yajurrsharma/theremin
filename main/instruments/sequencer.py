import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading
import time
import os
from flask import Flask, render_template, Response, request, jsonify, send_file
import wave
import numpy as np
from engine import synth

app = Flask(__name__, template_folder='../templates', static_folder='../static')

from kickdrum import KickDrum
from snare import Snare
from hihat import HiHat
from bass import Bass
from synth import Synth

instruments = {
    "kick": KickDrum(),
    "snare": Snare(),
    "hi-hat": HiHat(),
    "bass": Bass(),
    "synth": Synth()
}

instrument_sequence = []
current_step_index = 0
active_tracks = {}
recorded_events = []
is_recording = False
session_playback_active = False

script_dir = os.path.dirname(os.path.abspath(__file__))
task_path = os.path.abspath(os.path.join(script_dir, '../hand_landmarker.task'))

base_options = python.BaseOptions(model_asset_path=task_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.IMAGE
)

detector = vision.HandLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)

def trigger_instrument(inst_name, subtype="default", note=60, velocity=100):
    inst = instruments.get(inst_name)
    if not inst:
        return
    if inst_name in ["kick", "snare"]:
        inst.hit()
    elif inst_name == "hi-hat":
        if subtype == "open":
            inst.hit_open()
        else:
            inst.hit_close()
    elif inst_name in ["bass", "synth"]:
        inst.note_on(int(note), int(velocity))

def background_loop_player():
    global session_playback_active
    while session_playback_active:
        tracks_snapshot = list(active_tracks.items())
        if not tracks_snapshot:
            time.sleep(0.1)
            continue
            
        def play_track(inst_name, events):
            if not events:
                return
            first_event_time = events[0]["time"]
            while session_playback_active:
                track_start_wall = time.time()
                for event in events:
                    if not session_playback_active:
                        break
                    target_offset = event["time"] - first_event_time
                    while session_playback_active and (time.time() - track_start_wall) < target_offset:
                        time.sleep(0.005)
                    if not session_playback_active:
                        break
                    trigger_instrument(inst_name, event.get("subtype", "default"), event.get("note", 60), event.get("velocity", 100))
                while session_playback_active and (time.time() - track_start_wall) < (events[-1]["time"] - first_event_time + 0.5):
                    time.sleep(0.05)

        threads = [threading.Thread(target=play_track, args=(name, evs), daemon=True) for name, evs in tracks_snapshot]
        for t in threads:
            t.start()
            
        while session_playback_active:
            if len(active_tracks) != len(tracks_snapshot):
                break
            time.sleep(0.5)

def lock_current_track():
    global current_step_index, recorded_events, active_tracks, session_playback_active, instrument_sequence, is_recording
    is_recording = False
    if current_step_index < len(instrument_sequence):
        inst_name = instrument_sequence[current_step_index]
        active_tracks[inst_name] = list(recorded_events)
        recorded_events = []
        current_step_index += 1
        if current_step_index < len(instrument_sequence):
            global session_playback_active
            if not session_playback_active:
                session_playback_active = True
                threading.Thread(target=background_loop_player, daemon=True).start()

def generate_frames():
    global current_step_index, recorded_events, is_recording, instrument_sequence
    
    box_x1, box_y1, box_x2, box_y2 = 220, 140, 420, 340
    hh_box1_x1, hh_box1_y1, hh_box1_x2, hh_box1_y2 = 80, 140, 260, 340
    hh_box2_x1, hh_box2_y1, hh_box2_x2, hh_box2_y2 = 380, 140, 560, 340
    
    note_boxes = [
        (40, 140, 120, 240),
        (130, 140, 210, 240),
        (220, 140, 300, 240),
        (310, 140, 390, 240),
        (400, 140, 480, 240),
        (490, 140, 570, 240)
    ]
    
    was_in_box = False
    smooth_x, smooth_y = None, None
    alpha = 0.4

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        results = detector.detect(mp_image)

        current_inst_name = instrument_sequence[current_step_index] if (is_recording and instrument_sequence and current_step_index < len(instrument_sequence)) else "IDLE"

        cv2.putText(frame, f"TRACK: {current_inst_name.upper()}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        overlay = frame.copy()
        if current_inst_name == "hi-hat":
            cv2.rectangle(overlay, (hh_box1_x1, hh_box1_y1), (hh_box1_x2, hh_box1_y2), (50, 50, 200), -1)
            cv2.rectangle(overlay, (hh_box2_x1, hh_box2_y1), (hh_box2_x2, hh_box2_y2), (200, 50, 50), -1)
        elif current_inst_name in ["synth", "bass"]:
            for bx1, by1, bx2, by2 in note_boxes:
                cv2.rectangle(overlay, (bx1, by1), (bx2, by2), (80, 150, 80), -1)
        elif current_inst_name not in ["IDLE", "DONE"]:
            cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), (100, 100, 100), -1)
        
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # crisp borders
        if current_inst_name == "hi-hat":
            cv2.rectangle(frame, (hh_box1_x1, hh_box1_y1), (hh_box1_x2, hh_box1_y2), (255, 255, 255), 2)
            cv2.rectangle(frame, (hh_box2_x1, hh_box2_y1), (hh_box2_x2, hh_box2_y2), (255, 255, 255), 2)
        elif current_inst_name in ["synth", "bass"]:
            for bx1, by1, bx2, by2 in note_boxes:
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 255, 255), 2)
        elif current_inst_name not in ["IDLE", "DONE"]:
            cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (255, 255, 255), 2)

        valid_right_hand_found = False
        if results.hand_landmarks and results.handedness and is_recording:
            for idx, hand_landmarks in enumerate(results.hand_landmarks):
                hand_label = results.handedness[idx][0].category_name
                if hand_label == "Left":  # Right hand on mirrored view
                    valid_right_hand_found = True
                    index = hand_landmarks[8]
                    raw_x, raw_y = int(index.x * w), int(index.y * h)

                    if smooth_x is None:
                        smooth_x, smooth_y = raw_x, raw_y
                    else:
                        smooth_x = int(alpha * raw_x + (1 - alpha) * smooth_x)
                        smooth_y = int(alpha * raw_y + (1 - alpha) * smooth_y)

                    cv2.circle(frame, (smooth_x, smooth_y), 8, (0, 0, 255), -1)

                    in_box = False
                    hit_subtype = "default"
                    note_val = 60

                    if current_inst_name == "hi-hat":
                        if hh_box1_x1 <= smooth_x <= hh_box1_x2 and hh_box1_y1 <= smooth_y <= hh_box1_y2:
                            in_box = True
                            hit_subtype = "close"
                        elif hh_box2_x1 <= smooth_x <= hh_box2_x2 and hh_box2_y1 <= smooth_y <= hh_box2_y2:
                            in_box = True
                            hit_subtype = "open"
                    elif current_inst_name in ["synth", "bass"]:
                        scale_notes = [60, 62, 64, 65, 67, 72] if current_inst_name == "synth" else [36, 38, 40, 41, 43, 48]
                        for box_idx, (bx1, by1, bx2, by2) in enumerate(note_boxes):
                            if bx1 <= smooth_x <= bx2 and by1 <= smooth_y <= by2:
                                in_box = True
                                note_val = scale_notes[box_idx]
                                break
                    elif current_inst_name not in ["IDLE", "DONE"]:
                        in_box = (box_x1 <= smooth_x <= box_x2 and box_y1 <= smooth_y <= box_y2)

                    current_time = time.time()
                    if in_box and not was_in_box and current_inst_name not in ["IDLE", "DONE"]:
                        trigger_instrument(current_inst_name, hit_subtype, note=note_val)
                        recorded_events.append({
                            "time": current_time,
                            "inst_name": current_inst_name,
                            "subtype": hit_subtype,
                            "note": note_val
                        })
                        was_in_box = True
                    elif not in_box:
                        was_in_box = False
                    break

        if not valid_right_hand_found:
            was_in_box = False

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/set_sequence', methods=['POST'])
def set_sequence():
    global instrument_sequence, current_step_index, active_tracks, recorded_events, is_recording
    data = request.json
    seq = data.get('sequence', [])
    instrument_sequence = [x.strip().lower() for x in seq]
    current_step_index = 0
    active_tracks = {}
    recorded_events = []
    is_recording = False
    return jsonify({"status": "success", "sequence": instrument_sequence})

@app.route('/api/start_recording', methods=['POST'])
def start_recording():
    global is_recording, recorded_events
    recorded_events = []
    is_recording = True
    return jsonify({"status": "success", "current_step": current_step_index})

@app.route('/api/stop_track', methods=['POST'])
def stop_track():
    lock_current_track()
    return jsonify({"status": "success", "current_step": current_step_index})

@app.route('/finalize_and_play', methods=['POST'])
def finalize_and_play():
    global session_playback_active, is_recording
    if not session_playback_active:
        is_recording = False
        lock_current_track()
        session_playback_active = True
        threading.Thread(target=background_loop_player, daemon=True).start()
    return jsonify({"status": "success", "playback_active": session_playback_active})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)