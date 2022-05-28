#libraries for gui
from files.graphical_interface import *
from modules.serialModule import *
import pyqtgraph as pg
import sys

#libraries for mission planner
from PyQt6.QtWebEngineWidgets import QWebEngineView
import io, folium

class Arayuz(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_FC()
        self.ui.setupUi(self)

        self.fc_mode = 0
        self.warning_color  = "#FF0F0F"
        self.success_color  = "#FF4CAF50"
        self.info_color     = "#F6F6F6"
        self.baud_rates = [9600, 19200, 28800, 38400, 57600, 76800, 115200]
        self.telemetryConnectionStatus   = False
        self.pid_configurate_status      = False
        self.pid_p_default = 61
        self.pid_i_default = 18
        self.pid_d_default = 100

        self.telemetryRefresh()
        self.connections()
        self.initGui()
        self.initGraphs()
        
        '''self.ui.webView = QWebEngineView(self.ui.groupBox)
        self.ui.webView.setGeometry(QtCore.QRect(610, 30, 581, 581))
        self.ui.webView.setObjectName("webView")

        m = folium.Map( location=[41.08905409111161, 29.090750238423432], zoom_start=16 )

        data = io.BytesIO()
        m.save(data, close_file=False)
        self.ui.webView.setHtml(data.getvalue().decode())'''

    def connections(self):
        self.ui.initializeModule.clicked.connect(self.initModule)
        self.ui.arm_button.clicked.connect(self.arm_mode)
        self.ui.disarm_button.clicked.connect(self.disarm_mode)
        self.ui.debug_button.clicked.connect(self.debug_mode)
        self.ui.pid_lock_unlock_button.clicked.connect(self.pid_lock_unlock)
        self.ui.pid_p_slider.valueChanged.connect(self.pid_p_update)
        self.ui.pid_i_slider.valueChanged.connect(self.pid_i_update)
        self.ui.pid_d_slider.valueChanged.connect(self.pid_d_update)
        self.ui.total_esc.valueChanged.connect(self.total_esc_reporter)
        self.ui.esc_1.valueChanged.connect(self.esc_1_reporter)
        self.ui.esc_2.valueChanged.connect(self.esc_2_reporter)
        self.ui.esc_3.valueChanged.connect(self.esc_3_reporter)
        self.ui.esc_4.valueChanged.connect(self.esc_4_reporter)
        self.ui.pid_get_values_button.clicked.connect(self.pid_get_values_button_reporter)
        self.ui.set_default_pid.clicked.connect(self.set_default_pid_reporter)    
    def initModule(self):
        if self.telemetryConnectionStatus == False:
            self.ui.INITCheckBox.setChecked(True)
            QtCore.QCoreApplication.processEvents()
            port = self.ui.portSelectionBox.currentText()
            baud = int(self.ui.baudSelectionBox.currentText())
            self.ser = serialCOM()
            self.telemetryConnectionStatus = True
            self.ser.telemetryConnectionStatus = True
            self.GeneralSerialHandler = serialHandler(port, baud, self.ser)
            self.GeneralSerialHandler.rxBufferLen.connect(self.rxBufferTextUpdate)
            self.GeneralSerialHandler.txBufferLen.connect(self.txBufferTextUpdate)
            self.GeneralSerialHandler.angles.connect(self.angles_update)
            self.GeneralSerialHandler.tx_signal.connect(self.tx_signal_update)
            self.GeneralSerialHandler.rx_signal.connect(self.rx_signal_update)
            self.GeneralSerialHandler.latency_signal.connect(self.latency_signal_update)
            self.GeneralSerialHandler.gpp_signal.connect(self.gpp_signal_update)
            self.GeneralSerialHandler.gpi_signal.connect(self.gpi_signal_update)
            self.GeneralSerialHandler.gpd_signal.connect(self.gpd_signal_update)
            self.GeneralSerialHandler.grp_signal.connect(self.grp_signal_update)
            self.GeneralSerialHandler.gri_signal.connect(self.gri_signal_update)
            
            self.GeneralSerialHandler.grd_signal.connect(self.grd_signal_update)

            self.GeneralSerialHandler.esc1_signal.connect(self.esc_1_update)
            self.GeneralSerialHandler.esc2_signal.connect(self.esc_2_update)
            self.GeneralSerialHandler.esc3_signal.connect(self.esc_3_update)
            self.GeneralSerialHandler.esc4_signal.connect(self.esc_4_update)
            
            self.GeneralSerialHandler.start()
            self.ui.initializeModule.setText("Terminate The Module")
            self.ui.INITCheckBox.setChecked(False)
            QtCore.QCoreApplication.processEvents()
            self.ui.portSelectionBox.setEnabled(False)
            self.ui.baudSelectionBox.setEnabled(False)
            self.ui.arm_button.setEnabled(True)
            self.ui.disarm_button.setEnabled(True) 
            self.ui.debug_button.setEnabled(True)
            self.ui.pid_get_values_button.setEnabled(True)
            self.terminal('SUCCESS', 'Module initialized successfully.')
            self.ser.txBuffer.append("SFM3")
            self.ser.txBuffer.append("GPP")
            self.ser.txBuffer.append("GPI")
            self.ser.txBuffer.append("GPD")
            self.ser.txBuffer.append("GRP")
            self.ser.txBuffer.append("GRI")
            self.ser.txBuffer.append("GRD")
        else:
            self.ui.initializeModule.setText("Initialize The Module")
            self.disarm_mode()
            self.ser.txBuffer.append("SFM0")
            self.ser.telemetryConnectionStatus = False
            self.telemetryConnectionStatus = False  
            self.ui.portSelectionBox.setEnabled(True)
            self.ui.baudSelectionBox.setEnabled(True)
            self.ui.arm_button.setEnabled(False)
            self.ui.disarm_button.setEnabled(False)
            self.ui.pid_get_values_button.setEnabled(False)
            self.ui.pid_lock_unlock_button.setEnabled(False)
            self.ui.debug_button.setEnabled(False)
            self.terminal('SUCCESS', 'Module terminated successfully.')
    def initGraphs(self):
        self.ui.angleGraph.setMouseEnabled(x=False, y=False)
        self.ui.angleGraph.setBackground(background=None)
        self.ui.angleGraph.setRange(yRange=[-90,90])
        self.ui.angleGraph.getPlotItem().hideAxis('bottom')
        
        self.ui.channel_0_plot.hideAxis('bottom')
        self.ui.channel_0_plot.hideAxis('left') 
        self.ui.channel_0_plot.setRange(yRange=[0,2000])
        self.ui.channel_0_plot.setBackground(background=None)

        self.ui.channel_1_plot.hideAxis('bottom')
        self.ui.channel_1_plot.hideAxis('left') 
        self.ui.channel_1_plot.setRange(yRange=[0,2000])
        self.ui.channel_1_plot.setBackground(background=None)

        self.ui.channel_2_plot.hideAxis('bottom')
        self.ui.channel_2_plot.hideAxis('left') 
        self.ui.channel_2_plot.setRange(yRange=[0,2000])
        self.ui.channel_2_plot.setBackground(background=None)

        self.ui.channel_3_plot.hideAxis('bottom')
        self.ui.channel_3_plot.hideAxis('left') 
        self.ui.channel_3_plot.setRange(yRange=[0,2000])
        self.ui.channel_3_plot.setBackground(background=None)

        self.ui.channel_4_plot.hideAxis('bottom')
        self.ui.channel_4_plot.hideAxis('left') 
        self.ui.channel_4_plot.setRange(yRange=[0,2000])
        self.ui.channel_4_plot.setBackground(background=None)

        self.ui.channel_5_plot.hideAxis('bottom')
        self.ui.channel_5_plot.hideAxis('left') 
        self.ui.channel_5_plot.setRange(yRange=[0,2000])
        self.ui.channel_5_plot.setBackground(background=None)
    def initGui(self):
        self.ui.INITCheckBox.setChecked(False)
        self.ui.IDLECheckBox.setChecked(False)
        self.ui.RXCheckBox.setChecked(False)
        self.ui.TXCheckBox.setChecked(False)
        self.ui.arm_button.setEnabled(False)
        self.ui.disarm_button.setEnabled(False)
        self.ui.pid_get_values_button.setEnabled(False)
        self.ui.pid_lock_unlock_button.setEnabled(False)
        self.ui.debug_button.setEnabled(False)
        self.ui.total_esc.setEnabled(False)
        self.ui.esc_1.setEnabled(False)
        self.ui.esc_2.setEnabled(False)
        self.ui.esc_3.setEnabled(False)
        self.ui.esc_4.setEnabled(False)
        self.ui.set_default_pid.setEnabled(False)
        self.ui.pid_p_slider.setEnabled(False)
        self.ui.pid_i_slider.setEnabled(False)
        self.ui.pid_d_slider.setEnabled(False)
    def terminal(self, status, msg):

        if status ==      "INFO": self.ui.terminalBox.insertHtml(f'<font color={self.info_color     }><strong>INFO :: </strong></font><font color="white">{msg}</font><br>')
        elif status == "WARNING": self.ui.terminalBox.insertHtml(f'<font color={self.warning_color  }><strong>WARNING :: </strong></font><font color="white">{msg}</font><br>')
        elif status == "SUCCESS": self.ui.terminalBox.insertHtml(f'<font color={self.success_color  }><strong>SUCCESS :: </strong></font><font color="white">{msg}</font><br>')
        self.ui.terminalBox.verticalScrollBar().setValue(self.ui.terminalBox.verticalScrollBar().maximum())

    def debug_mode(self):
        self.fc_mode = 2
        self.ser.txBuffer.append("SFM2")
        self.ui.set_default_pid.setEnabled(True)
        self.ui.total_esc.setEnabled(True)
        self.ui.esc_1.setEnabled(True)
        self.ui.esc_2.setEnabled(True)
        self.ui.esc_3.setEnabled(True)
        self.ui.esc_4.setEnabled(True)
        self.ui.pid_get_values_button.setEnabled(True)
        self.ui.pid_lock_unlock_button.setEnabled(True)
        self.ui.set_default_pid.setEnabled(True) 
    def arm_mode(self): 
        self.fc_mode = 1
        self.ser.txBuffer.append("SFM1")
        if self.ui.pid_lock_unlock_button.text() == "Lock":
            print("clicked")
            self.ui.pid_lock_unlock_button.click()
        self.ui.total_esc.setEnabled(False)
        self.ui.esc_1.setEnabled(False)
        self.ui.esc_2.setEnabled(False)
        self.ui.esc_3.setEnabled(False)
        self.ui.esc_4.setEnabled(False)
        self.ui.pid_lock_unlock_button.setEnabled(False)
        self.ui.set_default_pid.setEnabled(False)
    def disarm_mode(self):
        self.fc_mode = 3
        self.ser.txBuffer.append("SFM3")
        if self.ui.pid_lock_unlock_button.text() == "Lock":
            print("clicked")
            self.ui.pid_lock_unlock_button.click()
        self.ui.total_esc.setEnabled(False)
        self.ui.esc_1.setEnabled(False)
        self.ui.esc_2.setEnabled(False)
        self.ui.esc_3.setEnabled(False)
        self.ui.esc_4.setEnabled(False)
        self.ui.pid_lock_unlock_button.setEnabled(False)
        self.ui.set_default_pid.setEnabled(False)

    def pid_lock_unlock(self):
        if self.pid_configurate_status == True:
            self.pid_configurate_status = False
            self.ui.pid_lock_unlock_button.setText('Unlock')
            self.ui.pid_p_slider.setEnabled(False)
            self.ui.pid_i_slider.setEnabled(False)
            self.ui.pid_d_slider.setEnabled(False)
        else:
            self.pid_configurate_status = True
            self.ui.pid_lock_unlock_button.setText('Lock')
            self.ui.pid_p_slider.setEnabled(True)
            self.ui.pid_i_slider.setEnabled(True)
            self.ui.pid_d_slider.setEnabled(True)
    def tx_signal_update(self, state): 
        self.ui.TXCheckBox.setChecked(state)
        QtCore.QCoreApplication.processEvents()
    def rx_signal_update(self, state): 
        self.ui.RXCheckBox.setChecked(state)
        QtCore.QCoreApplication.processEvents()
    def latency_signal_update(self, val): 
        if val < 0: val = 0
        elif val > 80000: val = 0
        self.ui.latencyArayuz.setText(str(val))
    def angles_update(self, angles):
        self.ui.angleGraph.clear()
        self.ui.angleGraph.plot(range(len(angles[0])), angles[0], pen=pg.mkPen('g', width=2), name ='pitch')
        self.ui.angleGraph.plot(range(len(angles[1])), angles[1], pen=pg.mkPen('r', width=2), name ='roll')
    def telemetryRefresh(self):
        self.ui.portSelectionBox.clear()
        for i,port in enumerate(portChecker()):
            self.ui.portSelectionBox.addItem("")
            self.ui.portSelectionBox.setItemText(i, port)
        self.ui.baudSelectionBox.clear()
        for i,baud in enumerate(self.baud_rates):
            self.ui.baudSelectionBox.addItem("")
            self.ui.baudSelectionBox.setItemText(i, str(baud))
        try: self.ui.portSelectionBox.setCurrentText(portChecker()[0])
        except : pass
        self.ui.baudSelectionBox.setCurrentText("115200")
    def total_esc_reporter(self):
        val = self.ui.total_esc.value()
        self.ui.total_esc_lcd.display(val)
        self.ui.esc_1.setValue(val)
        self.ui.esc_2.setValue(val)
        self.ui.esc_3.setValue(val)
        self.ui.esc_4.setValue(val)
    def esc_1_reporter(self):
        val = self.ui.esc_1.value()
        self.ui.esc_1_lcd.display(val)
        if self.fc_mode == 2: self.ser.txBuffer.append("SE1"+str(val))
    def esc_2_reporter(self):
        val = self.ui.esc_2.value()
        self.ui.esc_2_lcd.display(val)
        if self.fc_mode == 2: self.ser.txBuffer.append("SE2"+str(val))
    def esc_3_reporter(self):
        val = self.ui.esc_3.value()
        self.ui.esc_3_lcd.display(val)
        if self.fc_mode == 2: self.ser.txBuffer.append("SE3"+str(val))
    def esc_4_reporter(self):
        val = self.ui.esc_4.value()
        self.ui.esc_4_lcd.display(val)
        if self.fc_mode == 2: self.ser.txBuffer.append("SE4"+str(val))
    def esc_1_update(self, val): 
        self.ui.esc_1_lcd.display(val)
        self.ui.esc_1.setValue(val)
    def esc_2_update(self, val): 
        self.ui.esc_2_lcd.display(val)
        self.ui.esc_2.setValue(val)
    def esc_3_update(self, val): 
        self.ui.esc_3_lcd.display(val)
        self.ui.esc_3.setValue(val)
    def esc_4_update(self, val): 
        self.ui.esc_4_lcd.display(val)
        self.ui.esc_4.setValue(val)
    def pid_p_update(self):
        val = self.ui.pid_p_slider.value()
        val_text = str(val / 100 )
        self.ui.pitch_p_text.setText(val_text)
        self.ui.roll_p_text.setText(val_text)
        try: 
            self.ser.txBuffer.append(f"SPP{val}")
            self.ser.txBuffer.append(f"SRP{val}")
        except: pass
    def pid_i_update(self):
        val = self.ui.pid_i_slider.value()
        val_text = str(val / 100000 )
        self.ui.pitch_i_text.setText(val_text)
        self.ui.roll_i_text.setText(val_text)
        try:
            self.ser.txBuffer.append(f"SPI{val}")
            self.ser.txBuffer.append(f"SRI{val}")
        except: pass
    def pid_d_update(self):
        val = self.ui.pid_d_slider.value()
        val_text = str(val)
        self.ui.pitch_d_text.setText(val_text)
        self.ui.roll_d_text.setText(val_text)
        try:
            self.ser.txBuffer.append(f"SPD{val}") 
            self.ser.txBuffer.append(f"SRD{val}")
        except: pass
    def set_default_pid_reporter(self):
        self.ui.pid_p_slider.setValue(self.pid_p_default)
        self.ui.pid_i_slider.setValue(self.pid_i_default)
        self.ui.pid_d_slider.setValue(self.pid_d_default)
    def pid_get_values_button_reporter(self):
        self.ser.txBuffer.append("GPP")
        self.ser.txBuffer.append("GPI")
        self.ser.txBuffer.append("GPD")
        self.ser.txBuffer.append("GRP")
        self.ser.txBuffer.append("GRI")
        self.ser.txBuffer.append("GRD")
    def gpp_signal_update(self, val):  self.ui.pid_p_slider.setValue(val)
    def gpi_signal_update(self, val):  self.ui.pid_i_slider.setValue(val)
    def gpd_signal_update(self, val):  self.ui.pid_d_slider.setValue(val)
    def grp_signal_update(self, val):  self.ui.pid_p_slider.setValue(val)
    def gri_signal_update(self, val):  self.ui.pid_i_slider.setValue(val)
    def grd_signal_update(self, val):  self.ui.pid_d_slider.setValue(val)
    def txBufferTextUpdate(self, val): self.ui.tx_buffer.setText(str(val))
    def rxBufferTextUpdate(self, val): self.ui.rx_buffer.setText(str(val))

if __name__ == "__main__": 
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow() 
    ui = Arayuz()
    ui.showMaximized()
    sys.exit(app.exec())