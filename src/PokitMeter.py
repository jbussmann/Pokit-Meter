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

        self.is_app_running = True
        self.connect_flag = False
        self.device = BLEDevice
        self.protocol("WM_DELETE_WINDOW", self.window_close)
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

        for f in (ScanFrame, InfoFrame, MultimeterFrame, DSOFrame, LoggerFrame):
            frame = f(self, loop)
            frame.grid(row=1, column=0, padx='5', pady='5', sticky='nesw')
            self.frames[f] = frame

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
        while self.is_app_running:
            if self.connect_flag:
                self.connect_flag = False
                await self.connect_device()
            await asyncio.sleep(0.1)
        print("ending loop, closing app")
        self.loop.stop()

    async def connect_device(self):
        print(f"connecting to {self.device}")
        self.client = BleakClient(self.device)
        try:
            await self.client.connect(timeout=30.0)
            self.raise_frame('info')
            await self.frames[InfoFrame].read_info(self.client)
            while self.is_app_running:
                # await self.frame_handler()
                await self.frames[MultimeterFrame].change_mode(self.client)
                await self.frames[DSOFrame].change_mode(self.client)
                await self.frames[LoggerFrame].change_mode(self.client)
                await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Terminating with Exception {e}")
        finally:
            print("disconnecting")
            await self.client.disconnect()
            self.raise_frame('scan')

    def window_close(self):
        self.is_app_running = False

    def set_device(self, device):
        self.device = device
        self.connect_flag = True


# Main function, executed when file is invoked directly.
if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    MainWindow(event_loop)
    event_loop.run_forever()
    event_loop.close()
