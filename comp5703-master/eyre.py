# importing modules required
import asyncio
import threading
from tkinter import ttk, Tk, BooleanVar, Menu, messagebox, E, W, N, S, CENTER, Label, LabelFrame, BOTH, X, StringVar
from config_window import ConfigWindow

import cv2
from PIL import Image, ImageTk
import os

from notification import NotificationService
from detection import DetectionService, DetectionMarker
from config import Config
from datetime import datetime, timedelta


def image_resize(image, width=None, height=None):
    width_0, height_0 = image.size

    percent_width = float(width) / float(width_0)
    percent_height = float(height) / float(height_0)

    percent = min(percent_width, percent_height)

    newWidth = int(width_0 * percent)
    newHeight = int(height_0 * percent)

    return image.resize((newWidth, newHeight), 0)


class App:

    def __init__(self, root, event_loop):
        self.event_loop = event_loop

        self.last_notify_time = datetime.now()
        self.last_violation_count = 0

        self.config = Config()
        self.config.load()
        username = self.config.email_username
        password = self.config.email_password
        host = self.config.email_server
        port = self.config.email_port
        ssl = self.config.email_ssl

        self.notification_service = NotificationService(
            host, port, username, password, ssl)

        self.root = root
        self.init_camera()
        self.init_detection_service()

        self.init_gui()
        threading.Thread(target=self.asyncio_thread,
                         args=(self.event_loop,)).start()

    def init_camera(self):
        """
        Initialize camera
        """
        # self.camera = cv2.VideoCapture('IMG_8198.mov')
        self.camera = cv2.VideoCapture(0)
        width_value = self.root.winfo_screenwidth()
        height_value = self.root.winfo_screenheight()

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width_value)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,  height_value)

    def init_detection_service(self):
        """
        Initializes detection service. Detection marker is placed in the centre, vertically
        """

        # cam_img = self.capture_cam()
        # height, width, channels = cam_img.shape      
     

        self.detection_service = DetectionService()

    def init_gui(self):
        self.create_top_menu()
        self.create_page()

    def asyncio_thread(self, event_loop):
        """Schedule Video capture on different thread. So that main GUI won't freeze"""
        while True:
            event_loop.run_until_complete(self.show_vid())

    def quit(self):
        self.recording = False

        if messagebox.askokcancel("Quit", "Are you sure to close?"):
            self.detection_service.release()
            self.root.destroy()

    def create_top_menu(self):
        """
        Create a menu
        """
        self.menu_bar = Menu(self.root)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Settings", command=self.config_click)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.root.config(menu=self.menu_bar)

    def create_page(self):
        """
        Create video feed page
        """
        self.top_text = StringVar()

        self.l_top = Label(
            self.root, textvariable=self.top_text, bg='black', fg='white')
        self.l_top.pack(fill=X)

        self.lmain = Label(self.root, anchor=CENTER, bg='black')
        self.lmain.pack(fill=BOTH, expand=True)

        # self.bottom_text = StringVar()
        # self.l_bottom = Label(
        #     self.root, textvariable=self.bottom_text, text='Bottom', bg='black', fg='white')
        # self.l_bottom.pack(fill=X)

    def capture_cam(self):
        """
        Capture camera
        """
        if not self.camera.isOpened():  # checks for the opening of camera
            print("cant open the camera")

        flag, frame = self.camera.read()

        if flag is None:
            print("Major error!")
            return

        return frame

    def get_detection_marker(self, height, width):
        """Return locations of detection marker"""
        direction = self.config.detection_marker_direction
        location = self.config.detection_marker_location
        location_percentage = location/100

        if direction == 0:
            detection_location = int(width * location_percentage)
            return DetectionMarker(detection_location,0, detection_location, height)
        else:
            detection_location = int(height * location_percentage)
            return DetectionMarker(0, detection_location, width, detection_location)

    async def show_vid(self):
        """
        Display camera on a screen
        """
        frame = self.capture_cam()
        frame = cv2.flip(frame, 1)
        image_height, image_width, _ = frame.shape
        detection_marker = self.get_detection_marker(image_height, image_width)

        ret, frame = await self.detection_service.detection(frame, self.config.mode, detection_marker)
        print(ret)
        await self.notify(ret)

        pic = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(pic)

        imgtk = ImageTk.PhotoImage(image=img)

        self.lmain.configure(image=imgtk)
        self.lmain.imgtk = imgtk

        self.update_status(ret)

    def update_status(self, ret):
        """
        Update the top and bottom status labels
        """
        violation = ret['TotalViolation']
        total_people = ret['TotalPeople']
        
        top_text = f'Mode: {self.config.mode}, Total: {total_people}, Missing PPE: {violation}'

        self.top_text.set(top_text)

    def save_click():
        print('save_click')

    def config_click(self):
        self.open_config_window()

    def open_config_window(self):
        ConfigWindow(self, on_config_save=self.on_config_save)

    def on_config_save(self):
        self.config = Config()
        self.config.load()
        print('end')

    async def notify(self, ret):
        # Check time interval to send notifications
        now = datetime.now()
        delta = now - self.last_notify_time
        receiver = self.config.email_receiver

        # To test the notification, change the parameters in timedelta. Default is 12 hours.
        if delta > timedelta(hours=12, minutes=0, seconds=0):
            print(ret)
            try:   # Notify

                await self.notification_service.notify(0, receiver, "Without PPE:\n"+str(
                    ret['TotalViolation'])+"\n"+str(now)+"\nWith PPE: "+str(ret['TotalPeople']))

                # Update time
                self.last_notify_time = now

            except Exception as inst:
                pass


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()

    root = Tk()
    # dirname = os.path.dirname(__file__)
    # file_name = os.path.join(dirname, 'eyre.ico')
    root.title('Eyre')
    root.attributes('-fullscreen', True)
    root.configure(background="red")

    # root.iconbitmap(file_name)
    app = App(root, event_loop)
    root.mainloop()
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    app.camera.release()
    cv2.destroyAllWindows()
