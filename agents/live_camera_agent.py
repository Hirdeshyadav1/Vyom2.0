"""
Vyom - Live Camera Agent
Agar cv2 install nahi hai, ye module fail nahi hoga import ke time —
sirf camera-methods use karne par clear error dega.
"""

import time
import os

CV2_AVAILABLE = True
try:
    import cv2
except ImportError:
    CV2_AVAILABLE = False


class LiveCameraAgent:
    def __init__(self, vision_agent, security):
        self.vision_agent = vision_agent
        self.security = security
        self._cap = None
        self._running = False

    def start(self, user_id, user_level, camera_index=0):
        if not CV2_AVAILABLE:
            return {"ok": False, "error": "OpenCV (cv2) install nahi hai is device par."}

        auth = self.security.authorize(user_id, user_level, "camera_access", details={"mode": "live_stream"})
        if not auth["allowed"]:
            return {"ok": False, "error": "Blocked: " + auth["reason"]}

        self._cap = cv2.VideoCapture(camera_index)
        if not self._cap.isOpened():
            return {"ok": False, "error": "Camera nahi mila ya open nahi ho paya."}
        self._running = True
        return {"ok": True, "message": "Camera live capture started."}

    def capture_frame(self, save_path="vyom_live_frame.jpg"):
        if not CV2_AVAILABLE:
            return {"ok": False, "error": "OpenCV (cv2) install nahi hai."}
        if not self._cap or not self._running:
            return {"ok": False, "error": "Camera start nahi hua."}
        ret, frame = self._cap.read()
        if not ret:
            return {"ok": False, "error": "Frame capture fail hua."}
        cv2.imwrite(save_path, frame)
        return {"ok": True, "path": save_path}

    def watch_and_describe(self, user_id, user_level, interval_seconds=3.0, max_frames=5, on_description=None):
        start_result = self.start(user_id, user_level)
        if not start_result["ok"]:
            return start_result

        descriptions = []
        try:
            for i in range(max_frames):
                frame_result = self.capture_frame(save_path="vyom_live_frame_" + str(i) + ".jpg")
                if not frame_result["ok"]:
                    descriptions.append(frame_result["error"])
                    continue

                analysis = self.vision_agent.analyze_image(
                    user_id, user_level, frame_result["path"],
                    question="Abhi camera ke saamne kya ho raha hai, short mein batao.",
                )
                desc = analysis.get("answer") or analysis.get("error", "Unknown error")
                descriptions.append(desc)
                if on_description:
                    on_description(desc)

                os.remove(frame_result["path"])
                time.sleep(interval_seconds)
        finally:
            self.stop()

        return {"ok": True, "descriptions": descriptions}

    def watch_continuously(self, user_id, user_level, interval_seconds=3.0, on_description=None, stop_flag=None, change_threshold=15.0):
        if not CV2_AVAILABLE:
            if on_description:
                on_description("OpenCV (cv2) install nahi hai.")
            return

        import numpy as np

        start_result = self.start(user_id, user_level)
        if not start_result["ok"]:
            if on_description:
                on_description(start_result["error"])
            return

        prev_frame_gray = None
        frame_index = 0
        try:
            while True:
                if stop_flag and stop_flag():
                    break

                ret, frame = self._cap.read()
                if not ret:
                    time.sleep(interval_seconds)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                should_describe = True
                if prev_frame_gray is not None:
                    diff = cv2.absdiff(gray, prev_frame_gray)
                    mean_diff = float(np.mean(diff))
                    should_describe = mean_diff > change_threshold

                prev_frame_gray = gray

                if should_describe:
                    path = "vyom_continuous_frame_" + str(frame_index) + ".jpg"
                    cv2.imwrite(path, frame)
                    frame_index += 1

                    analysis = self.vision_agent.analyze_image(
                        user_id, user_level, path,
                        question="Abhi camera ke saamne kya change hua hai, short mein batao.",
                    )
                    desc = analysis.get("answer") or analysis.get("error", "Unknown error")
                    if on_description:
                        on_description(desc)
                    os.remove(path)

                time.sleep(interval_seconds)
        finally:
            self.stop()

    def stop(self):
        if self._cap:
            self._cap.release()
        self._running = False
