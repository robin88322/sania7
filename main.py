import sys
import numpy as np
import pandas as pd
from sys import argv
from copy import deepcopy
import gc
import time
from typing import Any, List, NoReturn, Optional, Union

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.Qt import (QApplication,
                      QMessageBox,
                      QFileDialog,
                      QInputDialog,
                      QTableWidgetItem)
from PyQt5.QtWidgets import QMainWindow
import PyQt5.QtGui
from PyQt5.uic import loadUi
from PyQt5.uic import loadUiType
from PyQt5 import uic
from cogitive_model import CognitiveModel



form_class, base_class = loadUiType('data/main.ui')
class AppWindow(QMainWindow, form_class):

    def closeEvent(self, event):
        event.accept()

    def input1(self):
        filename = QFileDialog.getOpenFileName(self, "Select File")
        self.file.setText(filename[0])

    @pyqtSlot()
    def upload1(self):
        try:
            df = pd.read_csv(self.file.displayText(), delimiter=',',header=None)

            self.main_table.clear()


            self.main_table.setCornerButtonEnabled(False)
            #self.impulse_table.setCornerButtonEnabled(False)
            self.main_table.setColumnCount(len(df))
            #self.impulse_table.setColumnCount(len(df))
            self.main_table.setRowCount(len(df))
            #self.impulse_table.setRowCount(1)

            self.main_table.setSortingEnabled(False)

            for i in range(len(df)):

                    #self.main_table.horizontalHeader.setDefaultSectionSize(60)
                    item = QTableWidgetItem()
                    self.main_table.setVerticalHeaderItem(i, item)
                    item = self.main_table.verticalHeaderItem(i)
                    item.setText(str(i+1))
                    self.main_table.setColumnWidth(i, 50)

                    item = QTableWidgetItem()
                    self.main_table.setHorizontalHeaderItem(i, item)
                    item = self.main_table.horizontalHeaderItem(i)
                    item.setText(str(i+1))

            for i in range(len(df)):
                for j in range(len(df)):
                        item = QTableWidgetItem()
                        mmm = round(df.iloc[i, j], 3)
                        item.setText( str(mmm))
                        self.main_table.setItem(i, j, item)
                self.main_table.setColumnWidth(i, 50)
                self.main_table.setRowHeight(i, 50)
                #item = QTableWidgetItem()
                #item.setText(str(0))
                #self.impulse_table.setItem(0, i, item)
            #self.main_table.resizeRowsToContents()
        except:
            QMessageBox.warning(w, 'Error', 'Не вибраний існуючий файл')




    @pyqtSlot()
    def add1(self) :
            name = str(self.main_table.rowCount() + 1)
            r = self.main_table.rowCount()
            self.main_table.setColumnCount(r + 1)
            self.main_table.setRowCount(r + 1)
            #self.impulse_table.setColumnCount(r + 1)
            self.main_table.setHorizontalHeaderItem(r, QTableWidgetItem(name))
            self.main_table.setVerticalHeaderItem(r, QTableWidgetItem(name))
            #self.impulse_table.setHorizontalHeaderItem(r, QTableWidgetItem(name))
            self.main_table.setColumnWidth(r, 50)
            self.main_table.setRowHeight(r, 50)
            #self.impulse_table.setColumnWidth(r, 50)

            for i in range(r + 1):
                item = '0'
                self.main_table.setItem(i, r, QTableWidgetItem(item))
                self.main_table.setItem(r, i, QTableWidgetItem(item))
            #item = '0'
            #self.impulse_table.setItem(0, r, QTableWidgetItem(item))

    @pyqtSlot()
    def remove1(self):
            selected_items = self.main_table.selectedItems()
            try:
                k = selected_items[0]
                c = k.column()

                self.main_table.removeColumn(c)
                self.main_table.removeRow(c)
            #self.impulse_table.removeColumn(c)
            except:
                QMessageBox.warning(w, 'Error', 'Нема виділених даних')



    def get_A(self):
        A = []
        for i in range(self.main_table.rowCount()):
            A_row = []
            for j in range(self.main_table.columnCount()):
                val = float(self.main_table.item(i, j).text())
                if val == None:
                    return None
                A_row.append(val)
            A.append(np.array(A_row))
        return np.array(A)

    def get_B(self):
        B = []
        for i in range(self.impulse_table.columnCount()):
            val = float(self.impulse_table.item(0, i).text())
            if val == None:
                    return None
            B.append(val)
        return np.array(B)

    @pyqtSlot()
    def analise1(self):
            A = self.get_A()
            if A.any() == None:
                QMessageBox.warning(w, 'Error', 'Error parsing matrix')

            # researching A
            cognitiveModel = CognitiveModel(A)

            results = 'Власні числа: \n'
            results += ' '.join(str(x)+'\n' for x in cognitiveModel.calculate_eigenvalues())
            results += ' \n '

            results += 'Стійкість збурення: '
            results += 'True' if cognitiveModel.check_perturbation_stability() else 'False'
            results += ' \n '

            results += 'Стійкість значення: '
            results += 'True' if cognitiveModel.check_numerical_stability() else 'False'
            results += ' \n '
            results += ' \n '

            results += 'Структурна стійкість: '
            cycles = cognitiveModel.check_structural_stability()
            if not cycles:
                results += 'True'
            else:
                cycle_str = lambda x: ' - '.join(self.main_table.verticalHeaderItem(y).text() for y in x)
                results += 'No \n(' + ', \n'.join(cycle_str(x) for x in cycles) + ')'

            self.result.setText(results)

    @pyqtSlot()
    def graph1(self):
            A = self.get_A()
            if A.any() == None:
                QMessageBox.warning(w,'Error','Помилка обробки матриці')
                return

            cognitiveModel = CognitiveModel(A)
            cognitiveModel.draw_graph()

    @pyqtSlot()
    def impulse1(self):
        A = self.get_A()
        if A.any() == None:
            QMessageBox.warning(w, 'Error', 'Error parsing matrix')
        cognitiveModel = CognitiveModel(A)
        B = self.get_B()
        t = 7
        cognitiveModel.impulse_model(t=t, q=B)

    @pyqtSlot()
    def impulse_calculate1(self):
        self.impulse_table.clear()
        l = self.main_table.columnCount()
        self.impulse_table.setColumnCount(l)
        for i in range(l):
            self.impulse_table.setItem(0, i, QTableWidgetItem('0'))
            self.impulse_table.setColumnWidth(i, 50)

        for c in range(self.main_table.columnCount()):
            it = self.main_table.horizontalHeaderItem(c)
            item = QTableWidgetItem()
            self.impulse_table.setHorizontalHeaderItem(c, item)
            item = self.impulse_table.horizontalHeaderItem(c)
            item.setText(str(it.text()))


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.widgetList = []
        self.show()
        self.tool.clicked.connect(self.input1)
        self.upload.clicked.connect(self.upload1)
        self.add.clicked.connect(self.add1)
        self.analise.clicked.connect(self.analise1)
        self.graph.clicked.connect(self.graph1)
        self.remove.clicked.connect(self.remove1)
        self.impulse.clicked.connect(self.impulse1)
        self.impulse_calculate.clicked.connect(self.impulse_calculate1)




app = 0
app = QApplication(argv)
app.setApplicationName('Work 7')
w = AppWindow()
w.show()

app.exec_()
