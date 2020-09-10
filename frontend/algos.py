import tkinter as tk
from os.path import join
from PIL import ImageTk, Image
from pysynth.output import Algorithms


class AlgorithmGUI(tk.Frame):

    def __init__(self, master, gui):
        super().__init__(master)
        self.gui = gui
        self.algo_var = tk.StringVar(self, value='stack')
        self.algo_var.trace("w", self.change_algorithm)
        self.algo_buttons()
        self.change_algorithm()

    def algo_buttons(self):
        self.images = [
            join('images', 'algorithms', 'stack.png'),
            join('images', 'algorithms', 'parallel.png'),
            join('images', 'algorithms', 'square.png'),
            join('images', 'algorithms', '3to1.png'),
            join('images', 'algorithms', 'custom.png')
        ]

        self.top_frame = tk.Frame(self)
        self.top_frame.pack()
        # Stack Algorithm
        self.stack_image = ImageTk.PhotoImage(Image.open(self.images[0]).convert('RGBA').resize((20,100)))
        self.stack = tk.Radiobutton(self.top_frame, image=self.stack_image, value='stack', variable=self.algo_var)
        self.stack.grid(row=0, column=0, padx=20)
        # Parallel Algorithm
        self.para_image = ImageTk.PhotoImage(Image.open(self.images[1]).convert('RGBA').resize((90,22)))
        self.parallel = tk.Radiobutton(self.top_frame, image=self.para_image, value='parallel', variable=self.algo_var)
        self.parallel.grid(row=0, column=1, padx=20)
        # Square Algorithm
        self.square_image = ImageTk.PhotoImage(Image.open(self.images[2]).convert('RGBA').resize((40,45)))
        self.square = tk.Radiobutton(self.top_frame, image=self.square_image, value='square', variable=self.algo_var)
        self.square.grid(row=0, column=2, padx=20)

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack()
        # 3 to 1 algorithm
        self.three_image = ImageTk.PhotoImage(Image.open(self.images[3]).convert('RGBA').resize((70,55)))
        self.three = tk.Radiobutton(self.bottom_frame, image=self.three_image, value='3to1', variable=self.algo_var)
        self.three.grid(row=0, column=0, padx=20)
        # Custom Algorithm
        self.custom_image = ImageTk.PhotoImage(Image.open(self.images[4]).convert('RGBA').resize((70,22)))
        self.custom = tk.Radiobutton(self.bottom_frame, image=self.custom_image, value='custom', variable=self.algo_var)
        self.custom.grid(row=0, column=1, padx=20)

    def change_algorithm(self, *args):
        if self.algo_var.get() == 'custom':
            for o in self.gui.oscillators[:-1]:
                if o.fm_frame is None: o.freq_mod_frame()
            self.gui.output.choose_algorithm("parallel")
        else:
            for o in self.gui.oscillators[:-1]:
                try: 
                    o.fm_frame.destroy()
                    o.fm_frame = None
                except: pass
            self.gui.output.choose_algorithm(self.algo_var.get())
        try:
            self.gui.change_algorithm_image()
        except: pass