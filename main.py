import threading
import tkinter as tk
from os.path import isfile, getsize
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
from compression import compress
from tkinter.ttk import Progressbar
import queue


class ImageContainer(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.btn_action = tk.Button(text='Action Text', master=self)
        self.lbl_title = tk.Label(text='Title Text', master=self)
        self.lbl_size = tk.Label(text='Size = N/A', master=self)
        self.image_view = ImageView(self)
        self.__setup()

    def set_title(self, title):
        self.lbl_title.config(text=title)

    def set_action_text(self, action_text):
        self.btn_action.config(text=action_text)

    def hide_size(self):
        self.lbl_size.pack_forget()

    def show_size(self):
        self.lbl_size.pack(side=tk.LEFT)

    def __setup(self):
        self.lbl_title.pack(side=tk.TOP)
        self.image_view.pack(fill=tk.BOTH, expand=True)
        self.btn_action.pack(side=tk.BOTTOM, pady=(16, 0))
        self.lbl_size.pack(side=tk.LEFT)

    def set_on_action_click_listener(self, on_action_click_listener):
        self.btn_action.bind("<Button-1>", on_action_click_listener)

    def set_image(self, filename):
        image_size = getsize(filename)
        self.lbl_size.config(text="Size: {} KB".format((image_size + 1023) // 1024))
        self.image_view.set_image(Image.open(filename))


class ImageView(tk.Frame):
    DEFAULT_IMAGE_WIDTH = 350
    DEFAULT_IMAGE_HEIGHT = 350

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.config(width=ImageView.DEFAULT_IMAGE_HEIGHT, height=ImageView.DEFAULT_IMAGE_WIDTH)
        self.img_width = ImageView.DEFAULT_IMAGE_WIDTH
        self.img_height = ImageView.DEFAULT_IMAGE_HEIGHT
        self.image_instance = None
        self.relief = 'ridge'
        self.borderwidth = 3
        self.lbl_image = tk.Label(master=self)

    def set_image(self, image):
        resized_image = image.resize((self.img_width, self.img_height), Image.ANTIALIAS)
        self.image_instance = ImageTk.PhotoImage(resized_image)
        self.lbl_image.config(image=self.image_instance)
        self.lbl_image.pack(fill=tk.BOTH, expand=True)
        self.__reshape()

    def __reshape(self):
        self.config(
            width=self.img_width,
            height=self.img_height
        )


class TkApp:
    def __init__(self):
        self.window = tk.Tk()
        self.container_original_image = ImageContainer(self.window)
        self.container_compressed_image = ImageContainer(self.window)
        self.pb = Progressbar(
            self.window,
            orient='horizontal',
            mode='indeterminate',
            length=280
        )
        self.queue = queue.Queue(maxsize=1)
        self.window.after(500, self.event_loop_tasks)

    def event_loop_tasks(self):
        if self.queue.full():
            compressed_path = self.queue.get()
            self.container_compressed_image.set_image(compressed_path)
            self.pb.stop()
            self.pb.grid_remove()
        self.window.after(500, self.event_loop_tasks)

    def setup(self):
        self.__setup_grid()
        self.__setup_frame_original_image()
        self.__setup_frame_compressed_image()

    def __setup_frame_original_image(self):
        c = self.container_original_image

        c.set_title('Original Image')
        c.set_action_text('Browse...')
        c.set_on_action_click_listener(self.on_load_image_clicked)
        c.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)

    def __setup_frame_compressed_image(self):
        c = self.container_compressed_image

        c.set_title('Compressed Image')
        c.set_action_text('Start Compression')
        c.set_on_action_click_listener(self.on_start_compression_clicked)
        c.grid(row=0, column=1, sticky='nsew', padx=16, pady=16)

    def __setup_grid(self):
        self.window.columnconfigure([0, 1], weight=1)
        self.window.rowconfigure(0, weight=1)

    def start(self):
        self.window.mainloop()

    def on_load_image_clicked(self, event):
        filename = askopenfilename()
        if self.validate_image(filename):
            self.selected_image_file = filename
            self.container_original_image.set_image(filename)
        return "break"

    def validate_image(self, path):
        if not isfile(path):
            return False

        file_format = path.split('.')[-1]
        return file_format in ['jpg', 'jpeg', 'png', 'tiff']

    def on_start_compression_clicked(self, event):
        if self.selected_image_file is not None:
            self.pb.grid(row=2, column=0, columnspan=2, pady=(0, 16))
            self.pb.start()
            compression_worker_thread = threading.Thread(target=compress, args=(self.selected_image_file, self.queue))
            compression_worker_thread.start()

    def load_image(self, filename):
        image = Image.open(filename)
        self.container_original_image.image_view.set_image(image)
        pass


if __name__ == '__main__':
    app = TkApp()
    app.setup()
    app.start()
