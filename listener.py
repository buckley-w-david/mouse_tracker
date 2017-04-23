#Concurency
import threading
from ctypes import windll, Structure, c_ulong, byref
from time import sleep

from StoppableThread import StoppableThread

class KeyListener(StoppableThread):
    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vk_key = key
        self.flag = threading.Event()

    def run(self):
        history = []
        while(not self.stopped): 
            if (windll.user32.GetKeyState(self.vk_key) & 0x8000):
                self.flag.set()
                return


if __name__ == '__main__':
    x = other()
    x.start()
    sleep(3)
    x.stop()
    x.join()