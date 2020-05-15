import tkinter as tk
from gui import SynthGUI

if __name__ == '__main__':
    root = tk.Tk()
    app = SynthGUI(master=root)
    app.pack()
    app.mainloop()