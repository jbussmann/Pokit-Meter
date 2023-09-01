import tkinter as tk
import tkinter.ttk as ttk
from bleak import BleakClient
from UUIDs import uuids
import struct


class MultimeterFrame(tk.Frame):

    def __init__(self, parent, loop):
        super().__init__(parent)
        self.parent = parent
        self.loop = loop
        self.change_mode_flag = False
        self.config = None
        self['bg'] = '#dae3f3'
        self['bd'] = 5

        self.columnconfigure(0, weight=1)
        self.columnconfigure(100, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(100, weight=1)

        self.label_1 = tk.Label(self, text="- - - - - -")
        self.label_1.grid(row=1, column=1)
        self.label_2 = tk.Label(self, text="Select Multimeter Mode")
        self.label_2.grid(row=2, column=1)

        modes = ('DC Voltage', 'AC Voltage', 'DC Current', 'AC Current',
                 'Resistance', 'Diode', 'Continuity', 'Temperature')
        self.cb_modes = ttk.Combobox(self, state='readonly', values=modes)
        self.cb_modes.bind('<<ComboboxSelected>>', self.calc_config)
        self.cb_modes.grid(row=3, column=1)

    def calc_config(self, event):
        mode = event.widget.current() + 1
        range = 0
        interval = 512
        self.config = struct.pack('< B B L', mode, range, interval)
        self.change_mode_flag = True

    def read_notification(self, sender, data):
        print("mm notified")
        value = struct.unpack('f', data[1:5])[0]
        print(value)
        self.label_1['text'] = f"{value:.3f}"


if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(__file__)
    main_dir = current_dir[:-4]
    os.system(f"{main_dir}/.venv/Scripts/python.exe {current_dir}/PokitMeter.py")
