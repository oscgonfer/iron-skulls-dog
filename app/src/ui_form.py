# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QLayout,
    QMainWindow, QMenu, QMenuBar, QPlainTextEdit,
    QPushButton, QSizePolicy, QSlider, QStatusBar,
    QTextEdit, QToolBox, QToolButton, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(993, 759)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Connect button
        self.pushButton_connect = QPushButton(self.centralwidget)
        self.pushButton_connect.setObjectName(u"pushButton")
        self.pushButton_connect.setGeometry(QRect(10, 64, 141, 31))
        # Space for log output
        self.logger = QPlainTextEdit(self.centralwidget)
        self.logger.setObjectName(u"plainTextEdit")
        self.logger.setGeometry(QRect(10, 100, 341, 171))
        self.logger.setReadOnly(True)

        self.pushButton_stop = QPushButton(self.centralwidget)
        self.pushButton_stop.setObjectName(u"pushButton_stop")
        self.pushButton_stop.setGeometry(QRect(10, 280, 341, 31))
        self.checkBox = QCheckBox(self.centralwidget)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(270, 70, 82, 23))
        self.checkBox.setChecked(False)
        self.checkBox_2 = QCheckBox(self.centralwidget)
        self.checkBox_2.setObjectName(u"checkBox_2")
        self.checkBox_2.setGeometry(QRect(190, 70, 82, 23))
        self.checkBox_2.setChecked(False)
        self.toolBox = QToolBox(self.centralwidget)
        self.toolBox.setObjectName(u"toolBox")
        self.toolBox.setGeometry(QRect(10, 370, 431, 331))
        font = QFont()
        font.setBold(True)
        self.toolBox.setFont(font)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 431, 269))
        self.pushButton_3 = QPushButton(self.page)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(240, 230, 101, 31))
        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(350, 50, 54, 17))
        font1 = QFont()
        font1.setBold(False)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pushButton_5 = QPushButton(self.page)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(120, 230, 101, 31))
        self.verticalSlider = QSlider(self.page)
        self.verticalSlider.setObjectName(u"verticalSlider")
        self.verticalSlider.setGeometry(QRect(370, 80, 20, 151))
        self.verticalSlider.setOrientation(Qt.Orientation.Vertical)
        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(0, 230, 101, 31))
        self.plainTextEdit_2 = QPlainTextEdit(self.page)
        self.plainTextEdit_2.setObjectName(u"plainTextEdit_2")
        self.plainTextEdit_2.setGeometry(QRect(0, 50, 341, 171))
        self.toolButton = QToolButton(self.page)
        self.toolButton.setObjectName(u"toolButton")
        self.toolButton.setGeometry(QRect(3, 10, 31, 31))
        self.plainTextEdit_3 = QPlainTextEdit(self.page)
        self.plainTextEdit_3.setObjectName(u"plainTextEdit_3")
        self.plainTextEdit_3.setGeometry(QRect(40, 10, 301, 31))
        self.toolBox.addItem(self.page, u"Play capture")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 431, 269))
        self.pushButton_6 = QPushButton(self.page_2)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(290, 0, 101, 31))
        self.pushButton_8 = QPushButton(self.page_2)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(10, 0, 101, 31))
        self.textEdit = QTextEdit(self.page_2)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(120, 0, 161, 31))
        self.toolBox.addItem(self.page_2, u"Record capture")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 30, 341, 21))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        self.label_2.setFont(font2)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignJustify|Qt.AlignmentFlag.AlignVCenter)
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 340, 341, 21))
        self.label_3.setFont(font2)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignJustify|Qt.AlignmentFlag.AlignVCenter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 993, 22))
        self.menuDog_controller = QMenu(self.menubar)
        self.menuDog_controller.setObjectName(u"menuDog_controller")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuDog_controller.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(MainWindow)

        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.pushButton_stop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"Dry run", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"Debug", None))
#if QT_CONFIG(tooltip)
        self.toolBox.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Hola</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Speed", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.toolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("MainWindow", u"Play capture", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"Store", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"Record", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QCoreApplication.translate("MainWindow", u"Record capture", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Connect to dog", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Capture Player / Recorder", None))
        self.menuDog_controller.setTitle(QCoreApplication.translate("MainWindow", u"Dog controller", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

