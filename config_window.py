import asyncio
from tkinter import ttk, Tk, messagebox
import tkinter as tk
from config import Config
from notification import NotificationService

class ConfigWindow(tk.Toplevel):
    def __init__(self, master, on_config_save=None, **kwargs):
        super().__init__(**kwargs  )
        
        self.resizable(False, False)
        
        self.on_config_save = on_config_save
        self.title('Configuration')

        self.config = Config()
        self.config.load()
        
        self.var_enable_ssl = tk.BooleanVar()
        self.var_enable_ssl.set(self.config.email_ssl)

        self.var_recipient_email = tk.StringVar()
        self.var_recipient_email.set(self.config.email_receiver)

        self.var_server = tk.StringVar()
        self.var_server.set(self.config.email_server)

        self.var_port = tk.IntVar()
        self.var_port.set(self.config.email_port)

        self.var_logon_email = tk.StringVar()
        self.var_logon_email.set(self.config.email_username)

        self.var_password = tk.StringVar()
        self.var_password.set(self.config.email_password)

        self.var_objects_detect = tk.IntVar()
        self.var_objects_detect.set(self.config.objects_to_detect)

        self.var_marker_location = tk.IntVar()
        self.var_marker_location.set(self.config.detection_marker_location)

        self.var_marker_direction = tk.IntVar()
        self.var_marker_direction.set(self.config.detection_marker_direction)
        
        self.var_status = tk.StringVar()
        self.var_status.set('')

        self.create_page()

        self.event_loop = asyncio.get_event_loop()
    
    def create_page(self):
        email_frame = ttk.LabelFrame(self, text="Email settings")
        email_frame.pack(padx=15, pady=15, fill=tk.X)

        self.draw_input(email_frame, 'Recipient Email:', "text", 0, self.var_recipient_email)
        self.draw_input(email_frame, 'Server:', "text", 1, self.var_server)
        self.draw_input(email_frame, 'Port:', "text", 2, self.var_port)
        self.draw_input(email_frame, 'Logon Email:', "text", 3, self.var_logon_email)
        self.draw_input(email_frame, 'Password:', "text", 4, self.var_password, True)
        self.draw_input(email_frame, 'Enable SSL', "check",5, self.var_enable_ssl)
        
        row_status = ttk.Frame(email_frame)
        row_status.pack(anchor='w')
        self.lbl_status = ttk.Label(row_status, textvariable=self.var_status)
        self.lbl_status.pack()

        row_test_email = ttk.Frame(email_frame)
        row_test_email.pack(anchor='w')
        btn_test_email = ttk.Button(row_test_email, text='Test Email',command=self.on_email_test)
        btn_test_email.pack()

        objects_frame = ttk.LabelFrame(self, text='Objects to detect')
        objects_frame.pack(fill=tk.X, padx=15)

        row_objects = ttk.Frame(objects_frame)
        row_objects.pack(anchor='w', expand=1)

        rad_helmet = ttk.Radiobutton(row_objects,text='Helmet', value=0, variable=self.var_objects_detect)
        rad_helmet.pack(side=tk.LEFT,fill=tk.X, expand=1)
        
        rad_vest = ttk.Radiobutton(row_objects,text='Vest', value=1, variable=self.var_objects_detect)
        rad_vest.pack(side=tk.LEFT,fill=tk.X)
        # rad_vest.grid(row=7, column=1)
        rad_helmet_vest = ttk.Radiobutton(row_objects,text='Helmet & Vest', value=2, variable=self.var_objects_detect)
        rad_helmet_vest.pack(side=tk.LEFT,fill=tk.X)

        # rad_helmet_vest.grid(row=7, column=2)
        rad_lab_coat = ttk.Radiobutton(row_objects,text='Lab Coat', value=3, variable=self.var_objects_detect)
        rad_lab_coat.pack(side=tk.LEFT,fill=tk.X)

        marker_frame = ttk.LabelFrame(self, text="Detection marker position")
        marker_frame.pack(padx=15, pady=15, fill=tk.X)

        # objects_frame = ttk.LabelFrame(self, text='Objects to detect')
        # objects_frame.pack(fill=tk.X, padx=15)
        direction_frame = ttk.LabelFrame(marker_frame, text='Direction of the marker')
        direction_frame.pack(fill=tk.X)

        row_direction = ttk.Frame(direction_frame)
        row_direction.pack(anchor='w', expand=1)

        rad_horizontal = ttk.Radiobutton(row_direction,text='Horizontal', value=0, variable=self.var_marker_direction)
        rad_horizontal.pack(side=tk.LEFT,fill=tk.X, expand=1)
        
        rad_vertical = ttk.Radiobutton(row_direction,text='Vertical', value=1, variable=self.var_marker_direction)
        rad_vertical.pack(side=tk.LEFT,fill=tk.X)

        self.draw_input(marker_frame, 'Location %: (0 - 100)', "text", 2, self.var_marker_location)

        buttons_frame = ttk.LabelFrame(self)
        buttons_frame.pack(padx=15, pady=15, fill=tk.X)

        row_btn_save = ttk.Frame(buttons_frame)
        row_btn_save.pack(anchor='w')

        btn_save = ttk.Button(row_btn_save, text="Ok",width=10,command=self.on_save)
        btn_save.pack(side=tk.LEFT)
        
        btn_cancel = ttk.Button(row_btn_save, text="Cancel", command=self.destroy)
        btn_cancel.pack(side=tk.LEFT)
        
    def draw_input(self, master, label, type, index, variable=None, is_password=False):
        row = ttk.Frame(master)
        row.pack(anchor='w')

        if type=="text":
            lbl = ttk.Label(row, width=20, text=label)
            lbl.pack(anchor='w')

            txt = ttk.Entry(row, width=50, textvar=variable)
            
            if is_password:
                txt.config(show="*")
        elif type=="check":
            txt = ttk.Checkbutton(row, var=variable, text=label)
        elif type=="number":
            lbl = ttk.Label(row, width=20, text=label)
            lbl.pack(anchor='w')
            txt = ttk.Spinbox(master, increment=1)
        
        txt.pack(anchor='w')

    def on_email_test(self):
        print('on_email_test')

        try:
            noti = NotificationService(self.var_server.get(),
                                        self.var_port.get(),
                                        self.var_logon_email.get(),
                                       self.var_password.get(),
                                       self.var_enable_ssl.get())

            loop = asyncio.new_event_loop()
            ss = loop.run_until_complete( noti.notify(0, self.var_recipient_email.get(), 'Test Email') )
            loop.close()
            
            self.var_status.set('Test Success')
            self.lbl_status.configure(foreground="green")

        except Exception as inst:
            self.lbl_status.configure(foreground="red")
            self.var_status.set(f'Error:{inst}')

    def on_save(self):
        config = Config()
        config.load()
        
        config.email_ssl = self.var_enable_ssl.get()
        config.email_receiver = self.var_recipient_email.get()
        config.email_server = self.var_server.get()
        config.email_port = self.var_port.get()
        config.email_username = self.var_logon_email.get()
        config.email_password = self.var_password.get()
        config.objects_to_detect = self.var_objects_detect.get()
        config.detection_marker_direction = self.var_marker_direction.get()
        config.detection_marker_location = self.var_marker_location.get()
        config.save()

        if(self.on_config_save != None):
            self.on_config_save()
        
        self.destroy()

if __name__ == '__main__':
    mw = tk.Tk()
    fw = ConfigWindow(mw)
    mw.mainloop()