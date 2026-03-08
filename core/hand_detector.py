import cv2
import mediapipe as mp
import time

class HandDetector:

    def __init__(self, model_path="hand_landmarker.task", num_hands=2):
        self.BaseOptions = mp.tasks.BaseOptions
        self.HandLandmarker = mp.tasks.vision.HandLandmarker
        self.HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        self.RunningMode = mp.tasks.vision.RunningMode

        options = self.HandLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=model_path),
            running_mode=self.RunningMode.VIDEO,
            num_hands=num_hands
        )

        self.detector = self.HandLandmarker.create_from_options(options)
        self.timestamp = 0
        self.results = None

    def find_hands(self, img, draw=True):
        """Détecte les mains dans une image"""

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        self.timestamp += 1
        self.results = self.detector.detect_for_video(mp_image, self.timestamp)

        if draw and self.results.hand_landmarks:
            h, w, _ = img.shape

            for hand in self.results.hand_landmarks:
                for lm in hand:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 5, (0,255,0), -1)

        return img


    def find_position(self, img, hand_index=0):
        """Retourne les coordonnées des landmarks"""

        landmarks = []

        if self.results and self.results.hand_landmarks:

            if hand_index < len(self.results.hand_landmarks):

                h, w, _ = img.shape
                hand = self.results.hand_landmarks[hand_index]

                for id, lm in enumerate(hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks.append([id, cx, cy])

        return landmarks