from track import track
from listener import KeyListener
import argparse

DEBUG               = False
VK_OEM_3           = 0xC0

if __name__ == '__main__':
    #Main argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', default="output\\plot.png",
            help="The output visualization of your mouse movement, default='output\\plot.png'")
    args = parser.parse_args()

    '''
    Memory usage was/still might be a concern. The ResourceLogger can be used to 
    log the memory and CPU usage to ensure it stays reasonable.
    '''
    if DEBUG:
        from resource_logging import ResourceLogger

        logger = ResourceLogger()
        logger.start()

    #Listens for the tildé key, and will signal when it happens
    #Used to exit the program
    listener = KeyListener(VK_OEM_3)
    listener.start()
    track(args.outfile, listener)

    if DEBUG:
        logger.stop()