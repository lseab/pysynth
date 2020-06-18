import tkinter as tk
from pysynth.output import VoiceChannel

class Keys:

    @staticmethod
    def white_keys():
        return [131.8, 146.8, 164.8, 174.6, 196, 220, 246.9]

    @staticmethod
    def black_keys():
        return [138.6, 155.5, 185, 207.7, 233.1]


class KeyboardGUI(tk.Frame):

    def __init__(self, master, output):
        super().__init__(master)
        output = output
        white_key_width = 40
        white_key_height = 150
        black_key_width = white_key_width * 0.5
        black_key_height = white_key_height * 0.6
        num_octaves = 4
        first_octave = 0
        x_offset = 3
        y_offset = 20
        canvas = tk.Canvas(self, width=white_key_width*7*num_octaves+5, height=white_key_height+10+y_offset)

        # white keys:
        for n, key in enumerate([0,1,2,3,4,5,6]*num_octaves):

            octave = first_octave + n // 7
            note = Keys.white_keys()[key]
            frequency = note * (2 ** octave)

            def press_key(event, frequency=frequency, octave=octave):
                voice = VoiceChannel(output, frequency=frequency)
                output.add_new_voice(voice)
                output.play()

            def release_key(event, frequency=frequency):
                output.release_notes(frequency)

            x = n * white_key_width
            key_rect = canvas.create_rectangle(x+x_offset, y_offset,
                                               x+white_key_width+x_offset, white_key_height+y_offset,
                                               fill="light sky blue", outline="gray50", width=1, activewidth=2)

            canvas.tag_bind(key_rect, "<ButtonPress-1>", press_key)
            canvas.tag_bind(key_rect, "<ButtonRelease-1>", release_key)

        # black keys:
        for n, key in enumerate([0,1,None,2,3,4,None]*num_octaves):
            
            if key is not None:

                octave = first_octave + n // 7
                note = Keys.black_keys()[key]
                frequency = note * (2 ** octave)

                def press_key(event, frequency=frequency, octave=octave):
                    voice = VoiceChannel(output, frequency=frequency)
                    output.add_new_voice(voice)
                    output.play()

                def release_key(event, frequency=frequency):
                    output.release_notes(frequency)
                
                x = n * white_key_width + white_key_width*0.75
                key_rect = canvas.create_rectangle(x+x_offset, y_offset,
                                                   x+black_key_width+x_offset, black_key_height+y_offset,
                                                   fill="midnight blue", outline="gray50", width=1, activewidth=2)

                canvas.tag_bind(key_rect, "<ButtonPress-1>", press_key)
                canvas.tag_bind(key_rect, "<ButtonRelease-1>", release_key)
                
        canvas.pack(padx=20)