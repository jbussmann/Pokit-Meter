import tkinter as tk


class ControlFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self['bg'] = '#fbe5d6'
        self['bd'] = 5

        self.columnconfigure(0, weight=1)
        self.columnconfigure(100, weight=1)

        self.btn_info = tk.Button(self, text="Info",
                                  command=lambda: parent.raise_frame('info'))
        self.btn_info.grid(row=1, column=1, padx='2', pady='3', sticky='nesw')
        
        self.btn_mm = tk.Button(self, text="Multimeter",
                                command=lambda: parent.raise_frame('mm'))
        self.btn_mm.grid(row=1, column=2, padx='2', pady='3', sticky='nesw')
        
        self.btn_dso = tk.Button(
            self, text="Oscilloscope", command=lambda: parent.raise_frame('dso'))
        self.btn_dso.grid(row=1, column=3, padx='2', pady='3', sticky='nesw')
        
        self.btn_log = tk.Button(
            self, text="Logger", command=lambda: parent.raise_frame('log'))
        self.btn_log.grid(row=1, column=4, padx='2', pady='3', sticky='nesw')


if __name__ == "__main__":
    import os
    os.system("PokitMeter")
