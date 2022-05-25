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
        
        self.fc_mode = "SM0"
        self.baud_rates = [9600, 19200, 28800, 38400, 57600, 76800, 115200]
        self.telemetryConnectionStatus = False
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
        self.telemetryRefresh()
        self.connections()
        self.initGraphs()

        self.ui.webView = QWebEngineView(self.ui.groupBox)
        self.ui.webView.setGeometry(QtCore.QRect(610, 30, 581, 581))
        self.ui.webView.setObjectName("webView")

        m = folium.Map( location=[41.08905409111161, 29.090750238423432], zoom_start=16 )

        data = io.BytesIO()
        m.save(data, close_file=False)
        self.ui.webView.setHtml(data.getvalue().decode())

    def connections(self):
        self.ui.initializeModule.clicked.connect(self.initModule)
        self.ui.arm_button.clicked.connect(self.arm_mode)
        self.ui.disarm_button.clicked.connect(self.disarm_mode)
        self.ui.debug_button.clicked.connect(self.debug_mode)
    
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
            self.ui.pid_configurate_button.setEnabled(True)
            self.ui.pid_get_values_button.setEnabled(True)
            self.ui.pid_lock_unlock_button.setEnabled(True)
            self.ui.debug_button.setEnabled(True)
        else:
            self.ui.initializeModule.setText("Initialize The Module")
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
            self.ui.debug_button.setText('DEBUG MODE')
    def initGraphs(self):
        self.ui.angleGraph.setMouseEnabled(x=False, y=False)
        self.ui.angleGraph.setBackground(background=None)
        self.ui.angleGraph.setRange(yRange=[-90,90])
        self.ui.angleGraph.getPlotItem().hideAxis('bottom')
   
    def debug_mode(self): self.ser.txBuffer.append("SM2")
    def arm_mode(self): self.ser.txBuffer.append("SM1")
    def disarm_mode(self): self.ser.txBuffer.append("SM0")
    def tx_signal_update(self, state): 
        self.ui.TXCheckBox.setChecked(state)
        QtCore.QCoreApplication.processEvents()
    def rx_signal_update(self, state): 
        self.ui.RXCheckBox.setChecked(state)
        QtCore.QCoreApplication.processEvents()

    def txBufferTextUpdate(self, val): self.ui.tx_buffer.setText(str(val))
    def rxBufferTextUpdate(self, val): self.ui.rx_buffer.setText(str(val))
    def latency_signal_update(self, val): self.ui.latencyArayuz.setText(str(val))
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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow() 
    ui = Arayuz()
    ui.showMaximized()
    sys.exit(app.exec())