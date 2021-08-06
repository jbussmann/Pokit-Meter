from DSOFrame import DSOFrame
from UUIDs import uuids
from bleak.backends.device import BLEDevice
from ControlFrame import ControlFrame
from ScanFrame import ScanFrame
from InfoFrame import InfoFrame
from MultimeterFrame import MultimeterFrame
from DSOFrame import DSOFrame
from LoggerFrame import LoggerFrame
import tkinter as tk
import asyncio
from bleak import BleakClient


class MainWindow(tk.Tk):

    def __init__(self, loop):
        super().__init__()
        self.title("Pokit Meter")
        width = 600
        height = 400

        self.app_exit_flag = False
        self.connect_flag = False
        self.device = BLEDevice
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.loop = loop
        self.gui_task = self.loop.create_task(self.gui_loop())
        self.connection_task = self.loop.create_task(self.connection_loop())

        # Place in the middle of the screen
        xpos = (self.winfo_screenwidth() - width) // 2
        ypos = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{xpos}+{ypos}")
        self.minsize(600, 400)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.control_frame = ControlFrame(self)
        self.control_frame.grid(row=0, column=0, padx='5', pady='5', sticky='nesw')

        self.frames = {}
        # self.scan_frame = ScanFrame(self, loop)
        # self.info_frame = InfoFrame(self, loop)
        # self.mm_frame = MultimeterFrame(self, loop)
        # self.dso_frame = DSOFrame(self, loop)

        for frame in (ScanFrame, InfoFrame, MultimeterFrame, DSOFrame, LoggerFrame):
            f = frame(self, loop)
            f.grid(row=1, column=0, padx='5', pady='5', sticky='nesw')
            self.frames[frame] = f

        self.raise_frame('scan')

    def raise_frame(self, frame):
        if frame == 'scan':
            self.frames[ScanFrame].tkraise()
        elif frame == 'info':
            self.frames[InfoFrame].tkraise()
        elif frame == 'mm':
            self.frames[MultimeterFrame].tkraise()
        elif frame == 'dso':
            self.frames[DSOFrame].tkraise()
        elif frame == 'log':
            self.frames[LoggerFrame].tkraise()

    async def gui_loop(self):
        while True:
            self.update()
            await asyncio.sleep(0.02)

    async def connection_loop(self):
        while True:
            if self.connect_flag:
                self.connect_flag = False
                await self.connect_device()
            await asyncio.sleep(0.1)

    async def connect_device(self):
        print(f"connecting to {self.device}")
        self.client = BleakClient(self.device)
        try:
            await self.client.connect(timeout=300.0)
            self.raise_frame('info')
            await self.frames[InfoFrame].read_info(self.client)
            while not self.app_exit_flag:
                await self.application_loop()
        except Exception as e:
            print(f"Terminating with Exception {e}")
        finally:
            print("disconnecting")
            await self.client.disconnect()

    async def application_loop(self):
        if self.frames[MultimeterFrame].change_mode_flag:
            mmFrame = self.frames[MultimeterFrame]
            mmFrame.change_mode_flag = False
            print(f"changing mm config to {mmFrame.config}")
            await self.client.write_gatt_char(
                uuids['mm_settings'], mmFrame.config, True)
            await self.client.start_notify(uuids['mm_reading'], mmFrame.mm_reading_notify)

        if self.frames[DSOFrame].change_mode_flag:
            dso_frame = self.frames[DSOFrame]
            dso_frame.change_mode_flag = False            
            print(f"changing dso config to {dso_frame.config}")
            await dso_frame.read_meta(self.client)
            await self.client.write_gatt_char(
                uuids['dso_settings'], dso_frame.config, True)
            await dso_frame.read_meta(self.client)
            await self.client.start_notify(uuids['dso_reading'], dso_frame.dso_reading_notify)
            await dso_frame.read_meta(self.client)

        await asyncio.sleep(0.1)

    def close(self):
        self.app_exit_flag = True
        self.gui_task.cancel()
        self.connection_task.cancel()
        self.loop.stop()


# Main function, executed when file is invoked directly.
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    MainWindow(loop)
    loop.run_forever()
    loop.close()
