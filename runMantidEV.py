import sys
import time

sys.path.insert(0,"/opt/mantidnightly/bin")

from mantid.simpleapi import *
from mantid.kernel import ConfigService
ConfigService.setLogLevel(1)

instrument = "TOPAZ"
seconds = 60
script = "./ReduceSCD_LiveRun.py"
StartLiveData(Instrument=instrument, UpdateEvery = seconds, PreserveEvents=True,
                  AccumulationMethod = "Add", AccumulationWorkspace="tmp",
                  OutputWorkspace="peaks_ws", PostProcessingScriptFilename=script)
print('Type Ctrl-C to cancel')
try:
    while True:
        time.sleep(1)
finally:
    AlgorithmManager.newestInstanceOf("MonitorLiveData").cancel()

