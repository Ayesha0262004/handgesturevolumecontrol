import tkinter as tk
from tkinter import ttk
from threading import Thread
import cv2
import mediapipe as mp
import pyautogui
from PIL import Image, ImageTk
import numpy as np

class HandVolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Volume Control")
        self.root.geometry("640x600")
        self.root.configure(bg='#2e2e2e')

        self.style = ttk.Style()
        self.style.configure("TButton",font=("Helvetica", 12),padding=10,background='#4d4d4d',foreground='#000000')
        self.style.map("TButton",background=[('active', '#666666')],foreground=[('active', '#ffffff')],relief=[('pressed', 'groove'), ('!pressed', 'ridge')])

        self.is_running = False
        self.camera_visible = True
        self.volume_control_active = False

        # Frame for logo, heading, and menu
        header_frame = tk.Frame(root, bg='#2e2e2e')
        header_frame.pack(pady=10, fill=tk.X)

        # Placeholder for logo (update with actual logo if available)
        self.logo = tk.Label(header_frame, text="HVCA", font=("Bell Gothic Std Light", 20, "bold"), bg='#2e2e2e', fg='#ffffff')
        self.logo.pack(side=tk.LEFT, padx=10)

        self.heading = tk.Label(header_frame, text="Hand Volume Control App", font=("Century Gothic", 10, "bold"), bg='#2e2e2e', fg='#ffffff')
        self.heading.pack(side=tk.LEFT, padx=10)


        # Load and display image
        self.image_path = r"C:\Users\Zaheer\PycharmProjects\collageproject\image1.jpg"  # Using raw string
        self.image = Image.open(self.image_path)
        self.image = self.image.resize((50, 50), Image.LANCZOS)  # Updated to Image.LANCZOS
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_label = tk.Label(header_frame, image=self.image_tk, bg='#2e2e2e')
        self.image_label.pack(side=tk.RIGHT, padx=10)


        # Create Menu
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New File", command=None)
        file_menu.add_command(label="Open...", command=None)
        file_menu.add_command(label="Save", command=None)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=None)
        edit_menu.add_command(label="Copy", command=None)
        edit_menu.add_command(label="Paste", command=None)
        edit_menu.add_command(label="Select All", command=None)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=None)
        edit_menu.add_command(label="Find again", command=None)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Tk Help", command=None)
        help_menu.add_command(label="Demo", command=None)
        help_menu.add_separator()
        help_menu.add_command(label="About Tk", command=None)
        menubar.add_cascade(label="Help", menu=help_menu)

        root.config(menu=menubar)

        button_frame = tk.Frame(root, bg='#2e2e2e')
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_control, style="TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_control, state=tk.DISABLED, style="TButton")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = ttk.Button(button_frame, text="Quit", command=self.quit_app, style="TButton")
        self.quit_button.pack(side=tk.LEFT, padx=5)

        self.toggle_button = ttk.Button(button_frame, text="Hide Camera", command=self.toggle_camera, style="TButton")
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        self.video_label = tk.Label(root)
        self.video_label.pack()

    def start_control(self):
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.thread = Thread(target=self.hand_volume_control)
        self.thread.start()

    def stop_control(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def quit_app(self):
        self.stop_control()
        self.root.quit()

    def toggle_camera(self):
        self.camera_visible = not self.camera_visible
        if self.camera_visible:
            self.video_label.pack()
            self.toggle_button.config(text="Hide Camera")
            self.root.geometry("640x600")
        else:
            self.video_label.pack_forget()
            self.toggle_button.config(text="Show Camera")
            self.root.geometry("640x200")

    def hand_volume_control(self):
        webcam = cv2.VideoCapture(0)
        my_hands = mp.solutions.hands.Hands()
        drawing_utils = mp.solutions.drawing_utils

        while self.is_running:
            ret, image = webcam.read()
            if not ret:
                break

            image = cv2.flip(image, 1)
            frame_height, frame_width, _ = image.shape
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            output = my_hands.process(rgb_image)
            hands = output.multi_hand_landmarks

            if hands and len(hands) == 2:
                hand1, hand2 = hands

                # Drawing landmarks on both hands
                drawing_utils.draw_landmarks(image, hand1)
                drawing_utils.draw_landmarks(image, hand2)

                # Getting thumb tips from both hands
                thumb_tip1 = hand1.landmark[4]
                thumb_tip2 = hand2.landmark[4]

                # Converting normalized coordinates to pixel values
                x1, y1 = int(thumb_tip1.x * frame_width), int(thumb_tip1.y * frame_height)
                x2, y2 = int(thumb_tip2.x * frame_width), int(thumb_tip2.y * frame_height)

                # Checking if thumbs are close to each other
                distance_between_thumbs = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                if distance_between_thumbs < 50:  # Threshold for thumb distance to toggle volume control
                    self.volume_control_active = not self.volume_control_active

                if self.volume_control_active:
                    for hand in hands:
                        drawing_utils.draw_landmarks(image, hand)
                        landmarks = hand.landmark

                        for id, landmark in enumerate(landmarks):
                            x = int(landmark.x * frame_width)
                            y = int(landmark.y * frame_height)

                            if id == 8:  # Index finger tip
                                cv2.circle(img=image, center=(x, y), radius=8, color=(0, 255, 255), thickness=3)
                                x1, y1 = x, y
                            elif id == 4:  # Thumb tip
                                cv2.circle(img=image, center=(x, y), radius=8, color=(0, 0, 255), thickness=3)
                                x2, y2 = x, y

                        dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                        if dist > 50:
                            pyautogui.press("volumeup")
                        else:
                            pyautogui.press("volumedown")

                        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 5)

            if hands and len(hands) == 1:
                hand = hands[0]

                # Check if all fingers are joined together
                finger_tips = [hand.landmark[i] for i in [4, 8, 12, 16, 20]]
                finger_tip_coords = [(int(finger.x * frame_width), int(finger.y * frame_height)) for finger in finger_tips]

                distances = [np.sqrt((finger_tip_coords[i][0] - finger_tip_coords[i+1][0]) ** 2 +(finger_tip_coords[i][1] - finger_tip_coords[i+1][1]) ** 2)
                        for i in range(len(finger_tip_coords) - 1)]

                if all(dist < 40 for dist in distances):  # Threshold for finger tips distance to mute/unmute
                    pyautogui.press("volumemute")

            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)

            if self.camera_visible:
                self.video_label.imgtk = img_tk
                self.video_label.configure(image=img_tk)
                self.video_label.update()

        webcam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = HandVolumeControlApp(root)
    root.mainloop()
