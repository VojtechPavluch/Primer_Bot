import tkinter as tk
import designer
import threading
import ordermanager
import filemanager
from resource import resource_path

BG_COLOR = "#A6D1E6"
TEXT_COLOR = "#3D3C42"
BTN_COLOR = "#FEFBF6"
FONT = "Raleway 12 bold"


class UserInterface:

    def __init__(self):
        """Initializes user interface"""
        self.window = tk.Tk()
        self.window.title("Primer Bot")
        self.set_window()
        self.window.config(pady=5, padx=5, bg=BG_COLOR)
        self.canvas = tk.Canvas(width=540, height=140, bg=BG_COLOR, highlightthickness=0)
        self.logo = tk.PhotoImage(file=resource_path("images/png/001-microscope.png"))
        self.canvas.create_image(85, 70, image=self.logo)
        self.canvas.create_text(330, 70, text="PRIMER BOT", font="Raleway 36", fill=TEXT_COLOR)
        self.canvas.create_text(220, 110, text="v1.0.0 beta", font="Raleway 11", fill=TEXT_COLOR)
        self.canvas.grid(column=0, row=0, columnspan=2, sticky='W', padx=10, pady=10)
        self.variables = []
        self.frames = []
        self.question_mark = tk.PhotoImage(file=resource_path("images/png/002-question-mark.png"))
        self.gear = tk.PhotoImage(file=resource_path("images/png/001-settings.png"))
        self.done = tk.PhotoImage(file=resource_path("images/png/001-check.png"))
        self.reject = tk.PhotoImage(file=resource_path("images/png/001-rejected.png"))
        self.rows = 0
        self._create_layout()
        self.index = 0
        self.thread = None
        self.stop_thread = threading.Event()
        self.window.mainloop()

    def set_window(self):
        """Sets size of the user interface"""
        scr_width = self.window.winfo_screenwidth()
        scr_height = self.window.winfo_screenheight()
        x_cor = int(scr_width / 2 - 580 / 2)
        y_cor = int(scr_height / 2 - 540 / 2)
        self.window.geometry(f"580x540+{x_cor}+{y_cor}")
        self.window.resizable(False, False)

    def _create_layout(self):
        """Adds input fields and buttons for adding rows, searching and ordering primers"""
        for i in range(5):
            self._add_row()
        self.add_btn = tk.Button(self.window, width=12, fg=TEXT_COLOR, bg=BTN_COLOR, text="Add Row", font=FONT, command=self._add_row)
        self.add_btn.grid(column=1, row=1)
        self.search_btn = tk.Button(self.window, width=12, fg=TEXT_COLOR, bg=BTN_COLOR, text="Search", font=FONT, command=lambda: self._start_thread(self._proceed_genes))
        self.search_btn.grid(column=1, row=2)
        self.order_btn = tk.Button(self.window, width=12, fg=TEXT_COLOR, bg=BTN_COLOR, text="Order Primers", font=FONT, command=lambda: self._start_thread(self._proceed_order))
        self.order_btn.grid(column=1, row=3)
        self.order_btn['state'] = 'disabled'

    def _add_row(self):
        """Responsible for adding one individual row. Maximum allowed number of rows is 10."""
        self.variables.append(tk.IntVar(value=1))
        frame = tk.Frame(self.window, padx=5, pady=5, bg=BG_COLOR)
        label = tk.Label(frame, image=self.question_mark, bg=BG_COLOR)
        label.grid(column=0, row=0, padx=5)
        entry = tk.Entry(frame, font='Monserrat 13', width=15)
        entry.grid(column=1, row=0, padx=5)
        index = len(self.variables) - 1
        rad_human = tk.Radiobutton(frame, text="Human",fg=TEXT_COLOR, bg=BG_COLOR,font="Raleway 10 bold", variable=self.variables[index], value=1)
        rad_human.grid(column=2, row=0, padx=5)
        rad_mouse = tk.Radiobutton(frame, text="Mouse",fg=TEXT_COLOR, bg=BG_COLOR, font="Raleway 10 bold", variable=self.variables[index], value=2)
        rad_mouse.grid(column=3, row=0, padx=5)
        rad_rat = tk.Radiobutton(frame, text="Rat",fg=TEXT_COLOR, bg=BG_COLOR, font="Raleway 10 bold", variable=self.variables[index], value=3)
        rad_rat.grid(column=4, row=0, padx=5)
        self.frames.append(frame)
        self.frames[len(self.variables)-1].grid(column=0, row=len(self.variables))
        self.rows += 1
        if self.rows > 9:
            self.add_btn['state'] = 'disabled'

    def _start_thread(self, my_thread):
        self.stop_thread.clear()
        self.thread = threading.Thread(target=my_thread)
        self.thread.start()

    def _stop_thread(self):
        self.stop_thread.set()
        self.thread = None

    def _proceed_genes(self):
        """Gets strings/names of genes from all input fields and tries to design primers for them."""
        self.search_btn['state'] = 'disabled'
        while not self.stop_thread.is_set():
            data = []
            dict_ = {
                1: "homo sapiens",
                2: "mus musculus",
                3: "rattus norvegicus"
            }

            for i in range(len(self.frames)):
                children_widgets = self.frames[i].winfo_children()
                if len(children_widgets[1].get()):
                    data.append({"gene": children_widgets[1].get(), "organism": dict_[int(self.variables[i].get())]})

            my_designer = designer.Designer(data)
            my_filemanager = filemanager.FileManager()

            for i in range(len(my_designer.data)):
                self.frames[i].winfo_children()[0].config(image=self.gear)
                if not my_designer.find_gene(my_designer.data[i]):
                    self.frames[i].winfo_children()[0].config(image=self.reject)
                    continue
                else:
                    print(i, my_designer.data[i])
                    my_designer.design_primers(my_designer.data[i])
                    my_filemanager.export_to_xlsx(my_designer.forward, my_designer.reverse)
                    self.frames[i].winfo_children()[0].config(image=self.done)
            my_designer.driver.quit()

            self.order_btn['state'] = 'normal'
            self._stop_thread()

    def _proceed_order(self):
        """Orders generated sequences from 'order.json' file"""
        self._stop_thread()

        # Creates a new window
        cred_win = tk.Tk()
        cred_win.geometry("420x200")
        cred_win.title("Eastport.cz Credentials")
        cred_win.config(bg=BG_COLOR, pady=30)

        # Sets properties of the new window
        info_label = tk.Label(cred_win, text="Fill in your credentials for Easport.cz", font=FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        info_label.grid(column=2, row=1, pady=20, sticky='W')
        email_label = tk.Label(cred_win, text="Email:", font=FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        email_label.grid(column=1, row=2, sticky='W', padx=10)
        email_entry = tk.Entry(cred_win, width=28, font=FONT)
        email_entry.grid(column=2, row=2, sticky='W')
        password_label = tk.Label(cred_win, text="Password:", font=FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        password_label.grid(column=1, row=3, sticky='W', padx=10)
        password_entry = tk.Entry(cred_win, width=28, font=FONT, show="*")
        password_entry.grid(column=2, row=3, sticky='W')
        sub_btn = tk.Button(cred_win, text="Submit", font=FONT, bg=BTN_COLOR, fg=TEXT_COLOR, command=lambda: close_window(cred_win))
        sub_btn.grid(column=2, row=4, sticky='W', pady=5)
        email = ""
        password = ""

        def close_window(window):
            nonlocal email, password
            email = email_entry.get()
            password = password_entry.get()
            window.destroy()
            self.stop_thread.clear()
        cred_win.mainloop()

        while not self.stop_thread.is_set():
            credentials = {"email": email, "password": password}
            my_ordermanager = ordermanager.OrderManager(credentials)
            my_ordermanager.order_primers()
            self._stop_thread()
