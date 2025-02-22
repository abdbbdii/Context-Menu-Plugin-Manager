import ctypes
import time
import asyncio
import flet as ft
from pathlib import Path



class LoadDLL:
    def __init__(self, page: ft.Page = None, on_entered=None, on_leaved=None, on_dropped=None, is_working: bool = True, drop_zone_dll_path: Path | str = "DropZone.dll"):
        super().__init__()
        self.page = page
        self.title = page.title
        self.state_active = is_working
        self.is_entered = ctypes.c_bool(False)
        self.is_leaved = ctypes.c_bool(False)
        self.is_over = ctypes.c_bool(False)
        self.is_dropped = ctypes.c_bool(False)
        self.drop_zone_dll_path = Path(drop_zone_dll_path).resolve()

        self.on_entered = on_entered
        self.on_leaved = on_leaved
        self.on_dropped = on_dropped

        self.__load_library()
        time.sleep(0.01)
        self.page.run_task(self.__execute)

    @property
    def is_working(self):
        return self.state_active

    @is_working.setter
    def is_working(self, value: bool = None):
        self.state_active = value

    def __window_exists(self):
        hwnd = ctypes.windll.user32.FindWindowW(None, self.title)
        return hwnd != 0

    def __get_file_names(self):
        num = self.dll.GetFilesCount()
        file_names_ptr = self.dll.GetFilesNames()
        file_names = []

        for i in range(num):
            try:
                file_names.append(file_names_ptr[i].decode())
            except:
                pass
        return file_names

    def __load_library(self):
        self.dll = ctypes.WinDLL(self.drop_zone_dll_path)
        self.dll.GetFilesNames.restype = ctypes.POINTER(ctypes.c_char_p)
        self.dll.AttachDLL.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_bool), ctypes.POINTER(ctypes.c_bool), ctypes.POINTER(ctypes.c_bool), ctypes.POINTER(ctypes.c_bool)]

        self.dll.AttachDLL(self.title.encode("utf-8"), ctypes.byref(self.is_entered), ctypes.byref(self.is_leaved), ctypes.byref(self.is_over), ctypes.byref(self.is_dropped))

    def __check_state(self):

        if self.is_over.value == True:
            if self.is_entered.value == True:  # ENTERED
                self.is_entered.value = False
                if self.on_entered != None:
                    self.on_entered("None")

            if self.is_leaved.value:  # LEAVED
                self.is_leaved.value = False
                if self.on_leaved != None:
                    self.on_leaved("None")

            if self.is_dropped.value:  # DROPPED
                self.is_dropped.value = False
                if self.on_dropped != None:
                    paths = self.__get_file_names()
                    self.on_dropped(paths)

    async def __execute(self):
        try:
            while self.__window_exists():
                if self.state_active:
                    self.__check_state()
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Error occured: {e}")
            raise
