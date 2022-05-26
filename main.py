from regex import D
from files.graphical_interface import *
from modules.serialModule import serialHandler, serialCOM, portChecker
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pyqtgraph as pg
import io, folium, sys

class Arayuz(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_FC()
        self.ui.setupUi(self)

        self.warning_color = "#ff0f0f"
        self.success_color = "#FF4CAF50"
        self.info_color = "#F6F6F6"
        self.fc_mode = 0
        self.baud_rates = [9600, 19200, 28800, 38400, 57600, 76800, 115200]
        self.telemetryConnectionStatus = False
        self.pid_configurate_status = False

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
        self.ui.total_esc.valueChanged.connect(self.total_esc_reporter)
        self.ui.esc_1.valueChanged.connect(self.esc_1_reporter)
        self.ui.esc_2.valueChanged.connect(self.esc_2_reporter)
        self.ui.esc_3.valueChanged.connect(self.esc_3_reporter)
        self.ui.esc_4.valueChanged.connect(self.esc_4_reporter)
        
    
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
            self.GeneralSerialHandler.start()
            self.ui.initializeModule.setText("Terminate The Module")
            self.ui.INITCheckBox.setChecked(False)
            QtCore.QCoreApplication.processEvents()
            self.ui.portSelectionBox.setEnabled(False)
            self.ui.baudSelectionBox.setEnabled(False)
            self.ui.arm_button.setEnabled(True)
            self.ui.disarm_button.setEnabled(True) 
            self.ui.pid_get_values_button.setEnabled(True)
            self.ui.pid_lock_unlock_button.setEnabled(True)
            self.ui.debug_button.setEnabled(True)
            self.terminal('SUCCESS', 'Module initialized successfully.')
        else:
            self.ui.initializeModule.setText("Initialize The Module")
            self.ser.txBuffer.append("SM0")
            self.ser.telemetryConnectionStatus = False
            self.telemetryConnectionStatus = False  
            self.ui.portSelectionBox.setEnabled(True)
            self.ui.baudSelectionBox.setEnabled(True)
            self.ui.arm_button.setEnabled(False)
            self.ui.disarm_button.setEnabled(False)
            self.ui.pid_configurate_button.setEnabled(False)
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
        self.ui.pid_configurate_button.setEnabled(False)
        self.ui.pid_get_values_button.setEnabled(False)
        self.ui.pid_lock_unlock_button.setEnabled(False)
        self.ui.debug_button.setEnabled(False)
        self.ui.total_esc.setEnabled(False)
        self.ui.esc_1.setEnabled(False)
        self.ui.esc_2.setEnabled(False)
        self.ui.esc_3.setEnabled(False)
        self.ui.esc_4.setEnabled(False)
        self.ui.calibrate_esc_button.setEnabled(False)
        self.ui.pid_p_slider.setEnabled(False)
        self.ui.pid_i_slider.setEnabled(False)
        self.ui.pid_d_slider.setEnabled(False)
    def terminal(self, status, msg):

        if status ==      "INFO": self.ui.terminalBox.insertHtml(f'<font color={self.info_color     }><strong>INFO :: </strong></font><font color="white">{msg}</font><br>')
        elif status == "WARNING": self.ui.terminalBox.insertHtml(f'<font color={self.warning_color  }><strong>WARNING :: </strong></font><font color="white">{msg}</font><br>')
        elif status == "SUCCESS": self.ui.terminalBox.insertHtml(f'<font color={self.success_color  }><strong>SUCCESS :: </strong></font><font color="white">{msg}</font><br>')
        self.ui.terminalBox.verticalScrollBar().setValue(self.ui.terminalBox.verticalScrollBar().maximum())

    def debug_mode(self):
        
        self.ser.txBuffer.append("SM2")
        self.ui.calibrate_esc_button.setEnabled(True)
        self.ui.total_esc.setEnabled(True)
        self.ui.esc_1.setEnabled(True)
        self.ui.esc_2.setEnabled(True)
        self.ui.esc_3.setEnabled(True)
        self.ui.esc_4.setEnabled(True)
    def arm_mode(self): 
        self.ser.txBuffer.append("SM1")
        self.ui.total_esc.setEnabled(False)
        self.ui.esc_1.setEnabled(False)
        self.ui.esc_2.setEnabled(False)
        self.ui.esc_3.setEnabled(False)
        self.ui.esc_4.setEnabled(False)
    def disarm_mode(self): 
        self.ser.txBuffer.append("SM0")
        self.ui.total_esc.setEnabled(False)
        self.ui.esc_1.setEnabled(False)
        self.ui.esc_2.setEnabled(False)
        self.ui.esc_3.setEnabled(False)
        self.ui.esc_4.setEnabled(False)

    def pid_lock_unlock(self):
        if self.pid_configurate_status == True:
            self.ui.pid_configurate_button.setEnabled(False)
            self.pid_configurate_status = False
            self.ui.pid_lock_unlock_button.setText('Unlock')
            self.ui.pid_p_slider.setEnabled(False)
            self.ui.pid_i_slider.setEnabled(False)
            self.ui.pid_d_slider.setEnabled(False)
        else:
            self.ui.pid_configurate_button.setEnabled(True)
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
    def txBufferTextUpdate(self, val): self.ui.tx_buffer.setText(str(val))
    def rxBufferTextUpdate(self, val): self.ui.rx_buffer.setText(str(val))
    def latency_signal_update(self, val): 
        if val < 0: val = 0
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
        self.ser.txBuffer.append("E1"+str(val))
    def esc_2_reporter(self):
        val = self.ui.esc_2.value()
        self.ui.esc_2_lcd.display(val)
        self.ser.txBuffer.append("E2"+str(val))
    def esc_3_reporter(self):
        val = self.ui.esc_3.value()
        self.ui.esc_3_lcd.display(val)
        self.ser.txBuffer.append("E3"+str(val))
    def esc_4_reporter(self):
        val = self.ui.esc_4.value()
        self.ui.esc_4_lcd.display(val)
        self.ser.txBuffer.append("E4"+str(val))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow() 
    ui = Arayuz()
    ui.showMaximized()
    sys.exit(app.exec())