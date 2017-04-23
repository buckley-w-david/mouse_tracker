#Pulling the cursor/system info
from ctypes import windll, Structure, c_ulong, byref
from time import sleep

from StoppableThread import StoppableThread

#Concurency
import threading
import queue

REFRESH_RATE    = 50 #iterations per second
SLEEP_TIME      = 1/REFRESH_RATE

HISTORY_LIMIT = 10 #Number of data points before we process

class POINT(Structure):
    _fields_ = [("x", c_ulong), ("y", c_ulong)]

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return (pt.x, pt.y)

class CursorObserver(StoppableThread):
    def __init__(self, theQueue=None, height=1080, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theQueue = theQueue
        self.height = height

    def run(self):
        history = []
        while not self.stopped: 
            mouse_position = queryMousePosition()
            mouse_position = (mouse_position[0], self.height-mouse_position[1])
            history.append(mouse_position)

            if (len(history) > HISTORY_LIMIT):
                self.theQueue.put(history)
                history = []

            sleep(SLEEP_TIME)
        #Write the remaining history
        self.theQueue.put(history)