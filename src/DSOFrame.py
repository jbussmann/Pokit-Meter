import tkinter as tk
import tkinter.ttk as ttk
from bleak import BleakClient
from UUIDs import uuids
import struct
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy


class DSOFrame(tk.Frame):

    def __init__(self, parent, loop):
        super().__init__(parent)
        self.parent = parent
        self.loop = loop
        self.change_mode_flag = False
        self.acquisition_flag = False
        self.reception_flag = False
        self.config = None
        self.metadata = {}
        self.sample_values = numpy.array([])
        # self.transmission_complete = False
        self['bg'] = '#dae3f3'
        self['bd'] = 5

        self.rowconfigure(9, weight=1)
        self.columnconfigure(1, weight=1)

        self.label_1 = tk.Label(self, text="Select Oscilloscope Mode")
        self.label_1.grid(row=0, column=0)

        modes = ('DC Voltage', 'AC Voltage', 'DC Current', 'AC Current')
        self.cb_modes = ttk.Combobox(self, state='readonly', values=modes)
        # self.cb_modes.current(0)
        self.cb_modes.bind('<<ComboboxSelected>>', self.set_ranges)
        self.cb_modes.grid(row=1, column=0)

        self.label_1 = tk.Label(self, text="Measurement Range")
        self.label_1.grid(row=2, column=0)

        self.cb_ranges = ttk.Combobox(self, state='readonly', values=("Select Mode",))
        self.cb_ranges.current(0)
        # self.cb_vranges.bind('<<ComboboxSelected>>', self.start_acquisition)
        self.cb_ranges.grid(row=3, column=0)

        self.label_2 = tk.Label(self, text="Sampling Window [ms]")
        self.label_2.grid(row=4, column=0)
        self.entry_2 = tk.Entry(self)
        self.entry_2.grid(row=5, column=0)
        self.entry_2.insert(0, '40')
        self.label_3 = tk.Label(self, text="Number of Samples (1...8192)")
        self.label_3.grid(row=6, column=0)
        self.entry_3 = tk.Entry(self)
        self.entry_3.grid(row=7, column=0)
        self.entry_3.insert(0, '10')

        self.btn_start = tk.Button(
            self, text="Start", command=self.start_acquisition)
        self.btn_start.grid(row=8, column=0, padx='0', pady='2', sticky='nesw')

        self.figure = Figure(tight_layout=True)
        self.axes = self.figure.add_subplot()
        self.line, = self.axes.plot(numpy.random.rand(10))
        self.plotcanvas = FigureCanvasTkAgg(self.figure, self)
        self.plotcanvas.get_tk_widget().grid(row=0, column=1, rowspan=10)

    def set_ranges(self, event=None):
        if 0 <= self.cb_modes.current() <= 1:
            print("voltage ranges")
            self.cb_ranges['values'] = ("0-0.3V", "0.3-2V", "2-6V", "6-12V", "12-30V", "30-60V")
            self.cb_ranges.current(0)
        if 2 <= self.cb_modes.current() <= 3:
            print("current ranges")
            self.cb_ranges['values'] = ("0-10mA", "10-30mA", "30-150mA", "150-300mA", "0.3-3A",)
            self.cb_ranges.current(0)

    def start_acquisition(self, event=None):
        command = 0
        trigger = 0
        mode = self.cb_modes.current() + 1
        range = self.cb_ranges.current()
        window = int(float(self.entry_2.get())*1000)
        # prevent entry of value out of range
        samples = min(int(self.entry_3.get()), 8192)
        # self.entry_3.delete(0)
        # self.entry_3.insert(0, str(samples))
        self.config = struct.pack(
            '< B f B B L H', command, trigger, mode, range, window, samples)
        # clear previous values
        self.sample_values = numpy.array([])
        self.change_mode_flag = True

    def read_notification(self, sender, data):
        print(data.hex())
        print("dso notified")
        values = struct.unpack(f'< {len(data)//2}h', data)
        self.sample_values = numpy.append(self.sample_values, values)

    async def read_meta(self, client: BleakClient):
        meta = await client.read_gatt_char(uuids['dso_metadata'])
        meta = struct.unpack('< B f B B L H L', meta)
        labels = ("status", "scale", "mode", "range", "window", "samples", "rate")
        self.metadata = dict(zip(labels, meta))
        print("reading metadata")
        print(self.metadata)
        self.check_completeness()

    def check_completeness(self):
        if len(self.sample_values) == self.metadata["samples"]:
            print("all samples received")
            x = numpy.linspace(0, self.metadata["window"], self.metadata["samples"], endpoint=False)
            print(x.shape)
            y = numpy.array(self.sample_values) * self.metadata["scale"]
            print(y.shape)
            self.axes.clear()
            self.axes.plot(x, y)
            self.plotcanvas.draw()


if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(__file__)
    main_dir = current_dir[:-4]
    os.system(f"{main_dir}/.venv/Scripts/python.exe {current_dir}/PokitMeter.py")
