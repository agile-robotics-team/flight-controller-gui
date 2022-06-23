from serial.tools.list_ports import comports
from files.graphical_interface import *
from collections import deque
from time import sleep, time
from serial import Serial
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
    angles          = QtCore.pyqtSignal(list)
    roll_angles     = QtCore.pyqtSignal(list)
    receiver_data_signal = QtCore.pyqtSignal(list)
    ch0_signal      = QtCore.pyqtSignal(str)
    ch1_signal      = QtCore.pyqtSignal(str)
    ch2_signal      = QtCore.pyqtSignal(str)
    ch3_signal      = QtCore.pyqtSignal(str)
    ch4_signal      = QtCore.pyqtSignal(str)
    ch5_signal      = QtCore.pyqtSignal(str)
    ch6_signal      = QtCore.pyqtSignal(str)
    ch7_signal      = QtCore.pyqtSignal(str)
    ch8_signal      = QtCore.pyqtSignal(str)
    gpp_signal      = QtCore.pyqtSignal(float)
    gpi_signal      = QtCore.pyqtSignal(float)
    gpd_signal      = QtCore.pyqtSignal(float)
    grp_signal      = QtCore.pyqtSignal(float)
    gri_signal      = QtCore.pyqtSignal(float)
    grd_signal      = QtCore.pyqtSignal(float)
    esc1_signal     = QtCore.pyqtSignal(int)
    esc2_signal     = QtCore.pyqtSignal(int)
    esc3_signal     = QtCore.pyqtSignal(int)
    esc4_signal     = QtCore.pyqtSignal(int)
    tem1_signal     = QtCore.pyqtSignal(float)
    
    # short signals    
    rxBufferLen     = QtCore.pyqtSignal(int)
    txBufferLen     = QtCore.pyqtSignal(int)
    init_signal     = QtCore.pyqtSignal(bool)
    idle_signal     = QtCore.pyqtSignal(bool)
    tx_signal       = QtCore.pyqtSignal(bool)
    rx_signal       = QtCore.pyqtSignal(bool)
    latency_signal  = QtCore.pyqtSignal(int)
    mode_signal     = QtCore.pyqtSignal(str)
 
    def __init__(self, port, baud, buffers, parent = None):
        super(serialHandler, self).__init__(parent)
        self.port = port
        self.baud = baud
        self.buffers = buffers
        self.ser = Serial(self.port,self.baud)
        
        self.angle_graph_len = 50
        self.receiver_maxlen = 50
        self.angles_list = [[],[],[]]
        self.ch0 = deque(maxlen = self.receiver_maxlen)
        self.ch1 = deque(maxlen = self.receiver_maxlen)
        self.ch2 = deque(maxlen = self.receiver_maxlen)
        self.ch3 = deque(maxlen = self.receiver_maxlen)
        self.ch4 = deque(maxlen = self.receiver_maxlen)
        self.ch5 = deque(maxlen = self.receiver_maxlen)
        self.ch6 = deque(maxlen = self.receiver_maxlen)
        self.ch7 = deque(maxlen = self.receiver_maxlen)
        self.ch8 = deque(maxlen = self.receiver_maxlen)
        for i in range(50):
             self.ch0.append(0)
             self.ch1.append(0)
             self.ch2.append(0)
             self.ch3.append(0)
             self.ch4.append(0)
             self.ch5.append(0)
             self.ch6.append(0)
             self.ch7.append(0)
             self.ch8.append(0)

        self.angleLastCheckTime = time()
        self.angleCheckInterval = 0.05
        self.latencyLastCheckTime = time()
        self.latencyCheckInterval = 1
        

    def run(self):
        
        while self.buffers.telemetryConnectionStatus or len(self.buffers.txBuffer):
            
            try :
                # transmit commands to flight controller
                if len(self.buffers.txBuffer) > 0:
                    self.ser.write((self.buffers.txBuffer[0]+"\n").encode())
                    self.buffers.txBuffer.pop(0)   
                
                # 1ms delay for prevent loop from freze
                # sleep(0.0000001)

                # receive commands from flight controller
                if self.ser.inWaiting()>0:
                    try:
                        
                        data = self.ser.readline().decode("UTF-8").strip('\n').strip('\r')
                        data = str.replace(data, "\x00", "", -1)

                        if data not in ["code[200]", "code[417]"]:
                            try: 
                                #print(type(data), len(data), data)
                                self.buffers.rxBuffer.append(loads(data))
                                #print(loads(data))
                            except Exception as e: print(e)
                        
                    except: print("Serial Reading Error")
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
                        if 'GPP' in self.buffers.rxBuffer[0].keys(): self.gpp_signal.emit(float(self.buffers.rxBuffer[0]['GPP']))
                        if 'GPI' in self.buffers.rxBuffer[0].keys(): self.gpi_signal.emit(float(self.buffers.rxBuffer[0]['GPI']))
                        if 'GPD' in self.buffers.rxBuffer[0].keys(): self.gpd_signal.emit(float(self.buffers.rxBuffer[0]['GPD']))
                        if 'GRP' in self.buffers.rxBuffer[0].keys(): self.grp_signal.emit(float(self.buffers.rxBuffer[0]['GRP']))
                        if 'GRI' in self.buffers.rxBuffer[0].keys(): self.gri_signal.emit(float(self.buffers.rxBuffer[0]['GRI']))
                        if 'GRD' in self.buffers.rxBuffer[0].keys(): self.grd_signal.emit(float(self.buffers.rxBuffer[0]['GRD']))
                        if 'ESC1' in self.buffers.rxBuffer[0].keys(): self.esc1_signal.emit(self.buffers.rxBuffer[0]['ESC1'])
                        if 'ESC2' in self.buffers.rxBuffer[0].keys(): self.esc2_signal.emit(self.buffers.rxBuffer[0]['ESC2'])
                        if 'ESC3' in self.buffers.rxBuffer[0].keys(): self.esc3_signal.emit(self.buffers.rxBuffer[0]['ESC3'])
                        if 'ESC4' in self.buffers.rxBuffer[0].keys(): self.esc4_signal.emit(self.buffers.rxBuffer[0]['ESC4'])
                        if 'CH1' in self.buffers.rxBuffer[0].keys():                             
                            self.ch0.append(int(self.buffers.rxBuffer[0]['CH1']))
                            self.ch0_signal.emit(str(self.buffers.rxBuffer[0]['CH1']))
                        elif 'CH2' in self.buffers.rxBuffer[0].keys():                             
                            self.ch1.append(int(self.buffers.rxBuffer[0]['CH2']))
                            self.ch1_signal.emit(str(self.buffers.rxBuffer[0]['CH2']))
                        elif 'CH3' in self.buffers.rxBuffer[0].keys():                             
                            self.ch2.append(int(self.buffers.rxBuffer[0]['CH3']))
                            self.ch2_signal.emit(str(self.buffers.rxBuffer[0]['CH3']))
                        elif 'CH4' in self.buffers.rxBuffer[0].keys():                             
                            self.ch3.append(int(self.buffers.rxBuffer[0]['CH4']))
                            self.ch3_signal.emit(str(self.buffers.rxBuffer[0]['CH4']))
                        elif 'CH5' in self.buffers.rxBuffer[0].keys():                             
                            self.ch4.append(int(self.buffers.rxBuffer[0]['CH5']))
                            self.ch4_signal.emit(str(self.buffers.rxBuffer[0]['CH5']))
                        elif 'CH6' in self.buffers.rxBuffer[0].keys():                             
                            self.ch5.append(int(self.buffers.rxBuffer[0]['CH6']))
                            self.ch5_signal.emit(str(self.buffers.rxBuffer[0]['CH6']))
                        elif 'CH7' in self.buffers.rxBuffer[0].keys():                             
                            self.ch6.append(int(self.buffers.rxBuffer[0]['CH7']))
                            self.ch6_signal.emit(str(self.buffers.rxBuffer[0]['CH7']))
                        elif 'CH8' in self.buffers.rxBuffer[0].keys():                             
                            self.ch7.append(int(self.buffers.rxBuffer[0]['CH8']))
                            self.ch7_signal.emit(str(self.buffers.rxBuffer[0]['CH8']))
                        elif 'CH9' in self.buffers.rxBuffer[0].keys():                             
                            self.ch8.append(int(self.buffers.rxBuffer[0]['CH9']))
                            self.ch8_signal.emit(str(self.buffers.rxBuffer[0]['CH9']))
                            self.receiver_data_signal.emit([self.ch0, self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6, self.ch7, self.ch8])
                        elif 'CH' in self.buffers.rxBuffer[0].keys():
                            data = self.buffers.rxBuffer[0]['CH'].split(",")

                            self.ch0.append(int(data[0]))
                            self.ch0_signal.emit(data[0])
                            self.ch1.append(int(data[1]))
                            self.ch1_signal.emit(data[1])
                            self.ch2.append(int(data[2]))
                            self.ch2_signal.emit(data[2])
                            self.ch3.append(int(data[3]))
                            self.ch3_signal.emit(data[3])
                            self.ch4.append(int(data[4]))
                            self.ch4_signal.emit(data[4])
                            self.ch5.append(int(data[5]))
                            self.ch5_signal.emit(data[5])
                            self.ch6.append(int(data[6]))
                            self.ch6_signal.emit(data[6])
                            self.ch7.append(int(data[7]))
                            self.ch7_signal.emit(data[7])
                            self.ch8.append(int(data[8]))
                            self.ch8_signal.emit(data[8])

                            self.receiver_data_signal.emit([self.ch0, self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6, self.ch7, self.ch8])
                        if 'TEM1' in self.buffers.rxBuffer[0].keys(): self.tem1_signal.emit(self.buffers.rxBuffer[0]['TEM1'])

                    else:     
                        try: 
                            ms = int((time() - float(self.buffers.rxBuffer[0]))*1000) 
                            self.latency_signal.emit(ms)
                        except : pass
                    self.buffers.rxBuffer.pop(0) 
                
                # latency check
                if time()-self.latencyLastCheckTime >= self.latencyCheckInterval:
                    self.latencyLastCheckTime = time()
                    self.buffers.txBuffer.append(str(time()))

                # update buffer lengths
                if len(self.buffers.rxBuffer) >= 10: self.rxBufferLen.emit(len(self.buffers.rxBuffer))
                if len(self.buffers.txBuffer) >= 10: self.txBufferLen.emit(len(self.buffers.txBuffer))

            except:pass
        self.ser.close()