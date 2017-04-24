#Pulling the cursor/system info
from ctypes import windll

#Cursor observation
from cursor import CursorObserver

#IO Trickery
from io import BytesIO

#Concurency
import threading
import queue

#plotting
import matplotlib.pyplot as plt
from PIL import Image

#Patience
from time import sleep
import os

#Number of batchs before a 'snapshot'
COLLECTION_LIMIT    = 300 #pretty arbitrary choice

#Codes for querying screen resolution
SM_CXVIRTUALSCREEN  = 0x4e
SM_CYVIRTUALSCREEN  = 0x4f

'''
Two initial issues were had when implimenting this system:
    1. If the system was implimented to first gather data, then process it
    all at once in a large batch, that batch took a very long time to run
    due to the method of highlighting overlapping sections requiring a large number
    of small lines to be drawn.

    The solution of this problem was to build the output incrimentally while
    the input was being generated

    2. This solution brought about another problem in that the memory and cpu
    usage was climbing uncomfortably fast for what would be a program that should
    run for hours at a time. 

    To fix that we take incremental 'snapshots' of the plot, composite them into 
    a PIL image, and whipe the plot. This puts an upper bound on the number of objects 
    in that matplotlib plot.
'''
def update_plot(graph, ax, result):
    #After plotting the max/min ranges need to be specified
    ax.set_xlim([0, 1920])
    ax.set_ylim([0, 1080])
    with BytesIO() as f:
        #I currently do not know of a better way to do this then 'writting'
        #out the data from matplotlib and reading it back into PIL
        graph.savefig(f, transparent=True, format='png')
        f.seek(0) #Required?
        with Image.open(f) as im:
            new_composite = Image.alpha_composite(result, im)
    plt.cla()

    return new_composite

def track(outfile, listener):
    history = []

    last_point = []
    point_queue = queue.Queue()

    width = windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    height = windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

    '''
    The observer collects the cursor locations and puts them into the
    queue in batches (currently of size 10)
    '''
    observer = CursorObserver(theQueue=point_queue, height=height)
    observer.start()

    #Configuring the matplotlib graph to not show the axis
    graph = plt.figure(frameon=False, figsize=(24, 13.5), dpi=80)
    ax = graph.add_axes([0, 0, 1, 1])
    ax.axis('off')
    current = 0

    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    while True:
        if (listener.flag.is_set()):
            observer.stop()

        #Collect the points that 
        try:
            points = point_queue.get(timeout=3)
        except queue.Empty:
            result = update_plot(graph, ax, result)
            break

        '''
        In order for the batches to not have a small broken section between the
        end of the previous one and the start of the next one, we store the end
        point of every batch, and stick it on the beginning of the next one.
        '''
        points = last_point + points

        x, y, state = zip(*points)
        for i in range(len(x)-1):
            '''
            The trick to the alpha stacking is here, we draw each line segment point to point as it's own
            plot, convienently matplotlib already handles overlapping plots in a nice looking way
            '''
            colour = 'r' if state[i] else 'b'
            ax.plot(x[i:i+2], y[i:i+2], alpha=0.1, lw=2, solid_capstyle="butt", c=colour)

        if (current > COLLECTION_LIMIT):
            result = update_plot(graph, ax, result)
            current = 0
            
        last_point = [(x[-1], y[-1], state[-1])]
        current += 1
        point_queue.task_done()

    #Create required directories structure if not already present
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    result.save(outfile)