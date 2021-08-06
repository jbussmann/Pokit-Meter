import tkinter as tk
from bleak import BleakClient
from UUIDs import uuids


class InfoFrame(tk.Frame):

    def __init__(self, parent, loop):
        super().__init__(parent)
        self.parent = parent
        self.loop = loop
        self.stop_flag = False
        self['bg'] = '#fff2cc'
        self['bd'] = 5

        self.columnconfigure(0, weight=1)
        self.columnconfigure(100, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(100, weight=1)

        self.label_1 = tk.Label(self, text="Model Number")
        self.label_1.grid(row=1, column=1)
        self.label_2 = tk.Label(self, text="FW Revision")
        self.label_2.grid(row=2, column=1)
        self.label_3 = tk.Label(self, text="HW Revision")
        self.label_3.grid(row=3, column=1)
        self.label_4 = tk.Label(self, text="SW Revision")
        self.label_4.grid(row=4, column=1)
        self.label_5 = tk.Label(self, text="Manufacturer")
        self.label_5.grid(row=5, column=1)
        self.label_6 = tk.Label(self, text="Device Name")
        self.label_6.grid(row=6, column=1)
        self.label_7 = tk.Label(self, text="Appearance")
        self.label_7.grid(row=7, column=1)

        self.entry_1 = tk.Entry(self, state='disabled')
        self.entry_1.grid(row=1, column=2)
        self.entry_2 = tk.Entry(self, state='disabled')
        self.entry_2.grid(row=2, column=2)
        self.entry_3 = tk.Entry(self, state='disabled')
        self.entry_3.grid(row=3, column=2)
        self.entry_4 = tk.Entry(self, state='disabled')
        self.entry_4.grid(row=4, column=2)
        self.entry_5 = tk.Entry(self, state='disabled')
        self.entry_5.grid(row=5, column=2)
        self.entry_6 = tk.Entry(self, state='disabled')
        self.entry_6.grid(row=6, column=2)
        self.entry_7 = tk.Entry(self, state='disabled')
        self.entry_7.grid(row=7, column=2)

        self.btn_led = tk.Button(self, text="Blink LED", command=self.led)
        self.btn_led.grid(row=8, column=1, columnspan=2, padx='0', pady='2', sticky='nesw')

    def led(self):
        print("led")

    async def read_info(self, client: BleakClient):
        model = await client.read_gatt_char(uuids['info_model_no'])
        fw = await client.read_gatt_char(uuids['info_fw_rev'])
        hw = await client.read_gatt_char(uuids['info_hw_rev'])
        sw = await client.read_gatt_char(uuids['info_sw_rev'])
        manufacturer = await client.read_gatt_char(uuids['info_manufact'])
        name = await client.read_gatt_char(uuids['generic_name'])
        appearance = await client.read_gatt_char(uuids['generic_appear'])
        self.update_disabled_texts(self.entry_1, model.decode())
        self.update_disabled_texts(self.entry_2, fw.decode())
        self.update_disabled_texts(self.entry_3, hw.decode())
        self.update_disabled_texts(self.entry_4, sw.decode())
        self.update_disabled_texts(self.entry_5, manufacturer.decode())
        self.update_disabled_texts(self.entry_6, name.decode())
        self.update_disabled_texts(self.entry_7, appearance.decode())
        print("all infos read")

    def update_disabled_texts(self, entry: tk.Entry, text):
        state = entry['state']
        entry['state'] = 'normal'
        entry.delete(0, 'end')
        entry.insert(0, text)
        entry['state'] = state


if __name__ == "__main__":
    import os
    os.system("PokitMeter")
