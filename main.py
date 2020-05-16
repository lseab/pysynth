import tkinter as tk
from frontend.synth import SynthGUI

if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(False, False)
    app = SynthGUI(master=root)
    app.pack()
    app.mainloop()