from tkinter import *

class LogScale(Frame):
    def __init__(self, parent, command, **kwargs):
        super().__init__(parent)
        self.command = command
        self.number = 0
        self.slide = Scale(self, command=self.logValue, showvalue=0, **kwargs)
        self.text = Label(self, text=10)
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