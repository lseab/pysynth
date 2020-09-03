import tkinter as tk
from tkinter import ttk

class LogScale(tk.Frame):
    def __init__(self, parent, command, **kwargs):
        super().__init__(parent)
        self.command = command
        self.number = 0
        self.slide = tk.Scale(self, command=self.logValue, showvalue=0, **kwargs)
        self.text = tk.Label(self, text=10)
        self.text.pack()
        self.slide.pack()

    def logValue(self, val):
        if 10**float(val) > 1000:
            text = str(round(10**float(val) / 1000, 1)) + " k"
        else: text = str(int(10**float(val)))
        self.text.configure(text=text)
        self.command()

    def get(self):
        return self.slide.get()

    def set(self, value):
        self.slide.set(value)


class ScrollFrame(tk.Frame):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected 
    to canvas scrollregion.

    2. self.scrollwindow is created and inserted into canvas

    Usage Guideline:
    Assign any widgets as children of <ScrolledWindow instance>.scrollwindow
    to get them inserted into canvas
    """

    def __init__(self, parent, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)

        # creating a scrollbars
        self.xscrlbr = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.xscrlbr.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.TRUE)
        self.yscrlbr = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.yscrlbr.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.TRUE)
        # creating a canvas
        self.canv = tk.Canvas(self, bd=0, highlightthickness=0,
                        xscrollcommand = self.xscrlbr.set,
                        yscrollcommand=self.yscrlbr.set)
        # placing a canvas into frame
        self.canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        # accociating scrollbar comands to canvas scroling
        self.xscrlbr.config(command=self.canv.xview)
        self.yscrlbr.config(command=self.canv.yview)

        # creating a frame to inserto to canvas
        self.scrollwindow = ttk.Frame(self)

        self.canv.create_window(0, 0, window=self.scrollwindow, anchor='nw')

        self.yscrlbr.lift(self.scrollwindow)        
        self.xscrlbr.lift(self.scrollwindow)
        self.scrollwindow.bind('<Configure>', self._configure_window)  
        self.scrollwindow.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollwindow.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.canv.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _unbound_to_mousewheel(self, event):
        self.canv.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1*(event.delta/120)), "units")

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight())
        self.canv.config(scrollregion='0 0 %s %s' % size)
        if self.scrollwindow.winfo_reqwidth() != self.canv.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canv.config(width = self.scrollwindow.winfo_reqwidth())
        if self.scrollwindow.winfo_reqheight() != self.canv.winfo_height():
            # update the canvas's width to fit the inner frame
            self.canv.config(height = self.scrollwindow.winfo_reqheight())