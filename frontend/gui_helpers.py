from tkinter import *

class LogScale(Frame):
    def __init__(self, parent=None ):
        Frame.__init__(self, parent)
        self.number = 0
        self.slide = Scale(self, orient=HORIZONTAL, command=self.setValue, showvalue=0, resolution=.01, from_=1, to=4)
        self.text = Label(self, text=10)
        self.slide.pack()
        self.text.pack()

    def setValue(self, val):
        self.number = (10**float(val))
        self.text.configure(text=int(self.number))
