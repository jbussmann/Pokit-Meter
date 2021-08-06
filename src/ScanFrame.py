import tkinter as tk
import asyncio
from bleak import BleakScanner
from UUIDs import uuids

from bleak.backends.device import BLEDevice
from winrt.windows.devices.bluetooth.advertisement import (
    BluetoothLEAdvertisementReceivedEventArgs)


class ScanFrame(tk.Frame):

    def __init__(self, parent, loop):
        super().__init__(parent)
        self.parent = parent
        self.loop = loop
        self.stop_flag = False
        self['bg'] = '#fbe5d6'
        self['bd'] = 5

        self.columnconfigure(0, weight=1)
        self.columnconfigure(100, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(100, weight=1)

        self.discovered_devices = []

        self.device_list = tk.Listbox(self, height=5)
        self.device_list.insert(1, "No Devices")
        self.device_list.grid(row=1, column=1, padx='0',
                              pady='2', sticky='nesw')

        self.btn_scan = tk.Button(
            self, text="Start Scan", command=self.start_scan)
        self.btn_scan.grid(row=2, column=1, padx='0', pady='2', sticky='nesw')

        self.btn_connect = tk.Button(
            self, text="Connect", command=self.connect, state='disabled')
        self.btn_connect.grid(row=3, column=1, padx='0',
                              pady='2', sticky='nesw')

        self.btn_test = tk.Button(
            self, text="Connect dummy", command=self.connect_dummy)
        self.btn_test.grid(row=4, column=1, padx='0', pady='2', sticky='nesw')

    def start_scan(self):
        self.btn_scan['text'] = "Stop Scan"
        self.btn_scan['command'] = self.stop_scan
        self.stop_flag = False
        self.discovered_devices = []
        self.update_list()
        self.loop.create_task(self.scan())

    def stop_scan(self):
        self.btn_scan['text'] = "Start Scan"
        self.btn_scan['command'] = self.start_scan
        self.stop_flag = True

    def connect(self):
        self.stop_scan()
        index = self.device_list.curselection()
        index = index[0]
        device = self.discovered_devices[index]
        self.parent.device = device
        self.parent.connect_flag = True

    def connect_dummy(self):
        dummy = BLEDevice("90:FD:9F:5C:B9:32", "dummy")
        dummy.details = BluetoothLEAdvertisementReceivedEventArgs
        dummy.details.bluetooth_address = 159418974779698
        self.parent.device = dummy
        self.parent.connect_flag = True

    async def scan(self):
        self.scanner = BleakScanner()
        self.scanner.register_detection_callback(self.detection_callback)
        await self.scanner.start()
        while(not self.stop_flag):
            await asyncio.sleep(0.01)
        await self.scanner.stop()

    def detection_callback(self, device, advertisement_data):
        # check if device is a Pokit Meter and add it
        is_pokit_meter = False
        is_new_device = True

        if uuids['pokit_service'] in device.metadata['uuids']:
            is_pokit_meter = True
        else:
            self.update_names()
            return

        for d in self.discovered_devices:
            if d.address == device.address:
                is_new_device = False

        if is_pokit_meter and is_new_device:
            self.discovered_devices.append(device)
            print(f"added {device}")
            self.update_list()

        self.update_names()

    def update_names(self):
        # replace address with name if available
        for device in self.discovered_devices:
            for d in self.scanner.discovered_devices:
                if device.address == d.address \
                        and device.name == '':
                    device.name = d.name
                    self.update_list()

    def update_list(self):
        index = self.device_list.curselection()
        print(f"current selection {index}")
        if index:
            index = index[0]

        self.device_list.delete(0, 'end')
        self.btn_connect['state'] = 'disabled'

        for device in self.discovered_devices:
            if device.name == '':
                self.device_list.insert('end', device.address)
            else:
                self.device_list.insert('end', device.name)

        if len(self.discovered_devices):
            if index:
                self.device_list.activate(index)
                print(f"activated {index}")
            else:
                self.device_list.activate(0)
                print(f"activated {0}")
            self.btn_connect['state'] = 'normal'
        else:
            self.device_list.insert('end', "No Devices")


if __name__ == "__main__":
    import os
    os.system("PokitMeter")
