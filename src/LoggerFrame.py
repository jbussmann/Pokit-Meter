import tkinter as tk
import tkinter.ttk as ttk
from bleak import BleakClient
from UUIDs import uuids
import struct
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy


class LoggerFrame(tk.Frame):

    def __init__(self, parent, loop):
        super().__init__(parent)
        self.parent = parent
        self.loop = loop
        self.change_mode_flag = False
        self.acquisition_flag = False
        self.reception_flag = False
        self.config = None
        self.scale = None
        self['bg'] = '#dae3f3'
        self['bd'] = 5

        self.rowconfigure(9, weight=1)
        self.columnconfigure(1, weight=1)

        self.label_1 = tk.Label(self, text="Select Logger Mode")
        self.label_1.grid(row=0, column=0)

        modes = ('DC Voltage', 'AC Voltage', 'DC Current', 'AC Current')
        self.cb_modes = ttk.Combobox(self, state='readonly', values=modes)
        self.cb_modes.current(0)
        self.cb_modes.bind('<<ComboboxSelected>>', self.start_acquisition)
        self.cb_modes.grid(row=1, column=0)

        self.label_2 = tk.Label(self, text="Sampling Window [ms]")
        self.label_2.grid(row=2, column=0)
        self.entry_2 = tk.Entry(self)
        self.entry_2.grid(row=3, column=0)
        self.entry_2.insert(0, '10')
        self.label_3 = tk.Label(self, text="Number of Samples (1...8192)")
        self.label_3.grid(row=4, column=0)
        self.entry_3 = tk.Entry(self)
        self.entry_3.grid(row=5, column=0)
        self.entry_3.insert(0, '10')

        self.btn_start = tk.Button(
            self, text="Start", command=self.start_acquisition)
        self.btn_start.grid(row=6, column=0, padx='0', pady='2', sticky='nesw')

        self.figure = Figure(tight_layout=True)
        self.axes = self.figure.add_subplot()
        self.line, = self.axes.plot(numpy.random.rand(10))
        self.plotcanvas = FigureCanvasTkAgg(self.figure, self)
        self.plotcanvas.get_tk_widget().grid(row=0, column=1, rowspan=10)

    def start_acquisition(self, event=None):
        command = 0
        trigger = 0
        mode = self.cb_modes.current() + 1
        range = 0
        window = int(float(self.entry_2.get())*1000)
        samples = int(self.entry_3.get())
        self.config = struct.pack(
            '< B f B B L H', command, trigger, mode, range, window, samples)
        self.change_mode_flag = True

    def dso_reading_notify(self, sender, data):
        print("dso notified")
        values = struct.unpack(f'<{len(data)//2}h', data)
        # x = numpy.linspace(0, len(values), len(values), False)
        y = numpy.array(values) * self.scale
        # self.line.set_data(x, y)
        # self.plotcanvas.draw()
        self.axes.clear()
        self.axes.plot(y)
        self.plotcanvas.draw()

    async def read_meta(self, client: BleakClient):
        meta = await client.read_gatt_char(uuids['dso_metadata'])
        meta = struct.unpack('< B f B B L H L', meta)
        status, scale, mode, range, window, samples, rate = meta
        print(f"metadata: {meta}")
        self.scale = scale


if __name__ == "__main__":
    import os
    os.system("PokitMeter")
