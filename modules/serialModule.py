from numpy import array
from zmq import device
from files.graphical_interface import *
from serial.tools.list_ports import comports
from serial import Serial
from time import sleep, time
from json import loads

def portChecker():
    PORTS=[]
    for i in comports(): PORTS.append(str(i).split(" ")[0])
    return PORTS

class serialCOM:
    def __init__(self):
        self.telemetryConnectionStatus = False 
        self.txBuffer = ['SM0']
        self.rxBuffer = []

class serialHandler(QtCore.QThread):
    
    # data signals
    angles      = QtCore.pyqtSignal(list)
    roll_angles = QtCore.pyqtSignal(list)

    # short signals    
    rxBufferLen = QtCore.pyqtSignal(int)
    txBufferLen = QtCore.pyqtSignal(int)
    init_signal = QtCore.pyqtSignal(bool)
    idle_signal = QtCore.pyqtSignal(bool)
    tx_signal   = QtCore.pyqtSignal(bool)
    rx_signal   = QtCore.pyqtSignal(bool)
    latency_signal = QtCore.pyqtSignal(int)
    mode_signal = QtCore.pyqtSignal(str)

    def __init__(self, port, baud, buffers, parent = None):
        super(serialHandler, self).__init__(parent)
        self.port = port
        self.baud = baud
        self.buffers = buffers
        self.ser = Serial(self.port,self.baud)
        
        self.angle_graph_len = 100
        self.angles_list = [[],[],[]]
        
        self.angleLastCheckTime = time()
        self.angleCheckInterval = 0.05
        self.latencyLastCheckTime = time()
        self.latencyCheckInterval = 1
        

    def run(self):
        
        while self.buffers.telemetryConnectionStatus or len(self.buffers.txBuffer):
            
            if len(self.buffers.txBuffer) > 0:
                self.tx_signal.emit(True)
                self.ser.write((self.buffers.txBuffer[0]+"\n").encode())
                self.buffers.txBuffer.pop(0)
                self.tx_signal.emit(False)        
            
            # 1ms delay for prevent loop from freze
            #sleep(0.0001)

            if self.ser.inWaiting()>0: 
                self.rx_signal.emit(True)
                data = self.ser.readline()[:-2].decode("UTF-8")
                if data not in ["code[200]", "code[417]"]:
                    try: self.buffers.rxBuffer.append(loads(data))
                    except Exception as e: pass
                self.rx_signal.emit(False)
        
            if len(self.buffers.rxBuffer) > 0:
                
                if type(self.buffers.rxBuffer[0]) == dict:
                    
                    if 'PD' in self.buffers.rxBuffer[0].keys():  
                        if len(self.angles_list[0]) >= self.angle_graph_len: 
                            self.angles_list[0].pop(0)
                            self.angles_list[0].append(self.buffers.rxBuffer[0]['PD'])
                        else: self.angles_list[0].append(self.buffers.rxBuffer[0]['PD'])
                        self.angles.emit(self.angles_list)
                    
                    if 'RD' in self.buffers.rxBuffer[0].keys():  
                        if len(self.angles_list[1]) >= self.angle_graph_len: 
                            self.angles_list[1].pop(0)
                            self.angles_list[1].append(self.buffers.rxBuffer[0]['RD'])
                        else: self.angles_list[1].append(self.buffers.rxBuffer[0]['RD'])
                        self.angles.emit(self.angles_list)

                    if 'GM' in self.buffers.rxBuffer[0].keys():
                        device_mode = self.buffers.rxBuffer[0]['GM']
                        if device_mode == 0: self.mode_signal.emit('BOOT Mode')
                        elif device_mode == 1: self.mode_signal.emit('STABILIZED Mode')
                        elif device_mode == 2: self.mode_signal.emit('DEBUG Mode')
                        else: self.mode_signal.emit('ERROR Mode')
                        
                try: 
                    ms = int((time() - float(self.buffers.rxBuffer[0]))*1000) 
                    self.latency_signal.emit(ms)
                except : pass

                self.buffers.rxBuffer.pop(0) 
            
            # angle check
            """if time()-self.angleLastCheckTime >= self.angleCheckInterval:
                self.buffers.txBuffer.append("PD")
                self.buffers.txBuffer.append("RD")
                self.angleLastCheckTime = time()"""
            
            # latency check
            if time()-self.latencyLastCheckTime >= self.latencyCheckInterval:
                self.latencyLastCheckTime = time()
                self.buffers.txBuffer.append(str(time()))

            self.rxBufferLen.emit(len(self.buffers.rxBuffer))
            self.txBufferLen.emit(len(self.buffers.txBuffer))
        
        self.ser.close()