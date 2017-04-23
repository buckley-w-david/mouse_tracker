import logging
import os
import psutil
import threading
from time import sleep

REFRESH_RATE = 0.25 #1 iteration every 4 seconds
SLEEP_TIME = 1/REFRESH_RATE

class ResourceLogger(threading.Thread):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		logging.basicConfig(filename='resource_usage_{}.log'.format(os.getpid()), level=logging.DEBUG)
		self.process = psutil.Process()
		self.running = True

	def stop(self):
		self.running = False

	def run(self):
		process = self.process
		while self.running:
			mem_usage = process.memory_info().rss
			cpu_usage = process.cpu_percent()
			logging.info('MEM={}, CPU={}%'.format(mem_usage, cpu_usage))
			sleep(SLEEP_TIME)

	def resources(self):
		w = WMI('.')
		result = w.query("SELECT WorkingSet, PercentProcessorTime FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % self.pid)
		return int(result[0].WorkingSet), int(result[0].PercentProcessorTime)

if __name__ == '__main__':
	logger = ResourceLogger()
	logger.start()

	x = list(range(2**10))
	z = []
	for i in x:
		for j in x:
			z.append(i+j)


