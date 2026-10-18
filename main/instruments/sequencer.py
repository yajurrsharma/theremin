import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading
import time
from flask import Flask, render_template, Response, request, jsonify



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



base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
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
            
        max_dur = 0.0
        normalized_tracks = []
        for inst_name, events in tracks_snapshot:
            if not events:
                continue
            first_t = events[0]["time"]
            norm_events = []
            for ev in events:
                offset = ev["time"] - first_t
                norm_events.append((offset, ev))
                if offset > max_dur:
                    max_dur = offset
            normalized_tracks.append((inst_name, norm_events))

        loop_length = (max_dur + 0.5) if max_dur > 0 else 4.0
        loop_start_wall = time.time()

        def play_track(inst_name, norm_events):
            event_idx = 0
            total_events = len(norm_events)
            
            while session_playback_active and event_idx < total_events:
                target_offset, ev = norm_events[event_idx]
                elapsed = time.time() - loop_start_wall
                sleep_time = target_offset - elapsed
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                if not session_playback_active:
                    break
                    
                note_val = ev.get("note", 60)
                trigger_instrument(
                    inst_name,
                    ev.get("subtype", "default"),
                    note_val,
                    ev.get("velocity", 100)
                )
                
                if inst_name in ["synth", "bass"]:
                    time.sleep(0.15)
                    try:
                        inst_obj = instruments.get(inst_name)
                        if inst_obj and hasattr(inst_obj, 'note_off'):
                            inst_obj.note_off(note_val)
                    except Exception:
                        pass
                        
                event_idx += 1

        threads = [threading.Thread(target=play_track, args=(name, evs), daemon=True) for name, evs in normalized_tracks]
        for t in threads:
            t.start()
            
        while session_playback_active:
            if (time.time() - loop_start_wall) >= loop_length:
                break
            if set(active_tracks.keys()) != set(dict(tracks_snapshot).keys()):
                break
            time.sleep(0.05)

def lock_current_track():
    global current_step_index, recorded_events, active_tracks, session_playback_active, is_recording
    is_recording = False
    
    if current_step_index < len(instrument_sequence):
        inst_name = instrument_sequence[current_step_index]
        active_tracks[inst_name] = list(recorded_events)
        print(f"Locked track for '{inst_name}' with {len(recorded_events)} events. All active tracks: {list(active_tracks.keys())}")
        
    recorded_events = []
    current_step_index += 1
    
    if not session_playback_active and active_tracks:
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

        current_inst_name = instrument_sequence[current_step_index] if (is_recording and instrument_sequence and current_step_index < len(instrument_sequence)) else "idle"

        cv2.putText(frame, f"instrument: {current_inst_name.upper()}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        overlay = frame.copy()
        if current_inst_name == "hi-hat":
            cv2.rectangle(overlay, (hh_box1_x1, hh_box1_y1), (hh_box1_x2, hh_box1_y2), (50, 50, 200), -1)
            cv2.rectangle(overlay, (hh_box2_x1, hh_box2_y1), (hh_box2_x2, hh_box2_y2), (200, 50, 50), -1)
        elif current_inst_name in ["synth", "bass"]:
            for bx1, by1, bx2, by2 in note_boxes:
                cv2.rectangle(overlay, (bx1, by1), (bx2, by2), (80, 150, 80), -1)
        elif current_inst_name not in ["idle", "done"]:
            cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), (100, 100, 100), -1)
        
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        if current_inst_name == "hi-hat":
            cv2.rectangle(frame, (hh_box1_x1, hh_box1_y1), (hh_box1_x2, hh_box1_y2), (255, 255, 255), 2)
            cv2.rectangle(frame, (hh_box2_x1, hh_box2_y1), (hh_box2_x2, hh_box2_y2), (255, 255, 255), 2)
        elif current_inst_name in ["synth", "bass"]:
            for bx1, by1, bx2, by2 in note_boxes:
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 255, 255), 2)
        elif current_inst_name not in ["idle", "done"]:
            cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (255, 255, 255), 2)

        valid_right_hand_found = False
        if results.hand_landmarks and results.handedness and is_recording:
            for idx, hand_landmarks in enumerate(results.hand_landmarks):
                hand_label = results.handedness[idx][0].category_name
                if hand_label == "Left":
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
                    elif current_inst_name not in ["idle", "done"]:
                        in_box = (box_x1 <= smooth_x <= box_x2 and box_y1 <= smooth_y <= box_y2)

                    current_time = time.time()
                    if in_box and not was_in_box and current_inst_name not in ["idle", "done"]:
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
    global session_playback_active
    
    session_playback_active = False
    time.sleep(0.1)
    
    def play_once():
        tracks_snapshot = list(active_tracks.items())
        if not tracks_snapshot:
            return
            
        max_dur = 0.0
        normalized_tracks = []
        for inst_name, events in tracks_snapshot:
            if not events:
                continue
            first_t = events[0]["time"]
            norm_events = []
            for ev in events:
                offset = ev["time"] - first_t
                norm_events.append((offset, ev))
                if offset > max_dur:
                    max_dur = offset
            normalized_tracks.append((inst_name, norm_events))

        start_wall = time.time()
        
        def play_track_once(inst_name, norm_events):
            event_idx = 0
            total_events = len(norm_events)
            while event_idx < total_events:
                target_offset, ev = norm_events[event_idx]
                elapsed = time.time() - start_wall
                sleep_time = target_offset - elapsed
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
                note_val = ev.get("note", 60)
                trigger_instrument(
                    inst_name,
                    ev.get("subtype", "default"),
                    note_val,
                    ev.get("velocity", 100)
                )
                
                if inst_name in ["synth", "bass"]:
                    time.sleep(0.15)
                    try:
                        inst_obj = instruments.get(inst_name)
                        if inst_obj and hasattr(inst_obj, 'note_off'):
                            inst_obj.note_off(note_val)
                    except Exception:
                        pass
                event_idx += 1

        threads = [threading.Thread(target=play_track_once, args=(name, evs), daemon=True) for name, evs in normalized_tracks]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for inst_name in ["synth", "bass"]:
            inst_obj = instruments.get(inst_name)
            if inst_obj and hasattr(inst_obj, 'note_off'):
                try:
                    inst_obj.note_off()
                except Exception:
                    pass

    threading.Thread(target=play_once, daemon=True).start()
    return {"status": "success", "message": "playing final seq"}


app.run(host='0.0.0.0', port=5000, debug=False)