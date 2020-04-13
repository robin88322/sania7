import sys
import numpy as np
import pandas as pd
from sys import argv

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
    def __init__(w):
        super().__init__()
        w.setupUi(w)
        w.widgetList = []
        w.show()
    def closeEvent(w, event):
        event.accept()



app = 0
app = QApplication(argv)
app.setApplicationName('Work 7')
w = AppWindow()
w.show()

def input():
    filename = QFileDialog.getOpenFileName(w, "Select File")
    w.file.setText(filename[0])

def upload():
    df = pd.read_csv(w.file.displayText(), delimiter=',',header=None)
    w.tableWidget.clear()

    w.tableWidget.setCornerButtonEnabled(False)
    w.tableWidget.setColumnCount(len(df))
    w.tableWidget.setRowCount(len(df))

    w.tableWidget.setSortingEnabled(False)

    for i in range(len(df)):

            #w.tableWidget.horizontalHeader.setDefaultSectionSize(60)
            item = QTableWidgetItem()
            w.tableWidget.setVerticalHeaderItem(i, item)
            item = w.tableWidget.verticalHeaderItem(i)
            item.setText(str(i+1))
            w.tableWidget.setColumnWidth(i, 50)

            item = QTableWidgetItem()
            w.tableWidget.setHorizontalHeaderItem(i, item)
            item = w.tableWidget.horizontalHeaderItem(i)
            item.setText(str(i+1))

    for i in range(len(df)):
        for j in range(len(df)):
                item = QTableWidgetItem()
                item.setText( str(round(df.iloc[i, j], 3)))
                w.tableWidget.setItem(i, j, item)
        w.tableWidget.setColumnWidth(i, 50)
        w.tableWidget.setRowHeight(i, 50)
    #w.tableWidget.resizeRowsToContents()

def remove():
        selected_items = w.tableWidget.selectedItems()
        try:
            k = selected_items[0]
            r = k.row()
            c = k.column()
            w.tableWidget.removeColumn(c)
            w.tableWidget.removeRow(c)
        except:
            QMessageBox.warning(w,'Error','Нема виділених даних')


def add():
        name = str(w.tableWidget.rowCount() + 1)
        r = w.tableWidget.rowCount()
        w.tableWidget.setColumnCount(r + 1)
        w.tableWidget.setRowCount(r + 1)
        w.tableWidget.setHorizontalHeaderItem(r, QTableWidgetItem(name))
        w.tableWidget.setVerticalHeaderItem(r, QTableWidgetItem(name))
        w.tableWidget.setColumnWidth(r, 50)
        w.tableWidget.setRowHeight(r, 50)

        for i in range(r + 1):
            item = '0'
            w.tableWidget.setItem(i, r, QTableWidgetItem(item))
            w.tableWidget.setItem(r, i, QTableWidgetItem(item))

def get_A():
        A = []
        for i in range(w.tableWidget.rowCount()):
            A_row = []
            for j in range(w.tableWidget.columnCount()):
                val = float(w.tableWidget.item(i, j).text())
                if val == None:
                    return None
                A_row.append(val)
            A.append(np.array(A_row))
        return np.array(A)

def analise():
        A = get_A()
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

        results += ' Стійкість значення: '
        results += 'True' if cognitiveModel.check_numerical_stability() else 'False'
        results += ' \n '
        results += ' \n '

        results += 'Структурна стійкість: '
        cycles = cognitiveModel.check_structural_stability()
        if not cycles:
            results += 'True'
        else:
            cycle_str = lambda x: ' - '.join(w.tableWidget.verticalHeaderItem(y).text() for y in x)
            results += 'No \n(' + ', \n'.join(cycle_str(x) for x in cycles) + ')'
        t = 5
        q = [0, 0, 0]
        for i in range(3,w.tableWidget.rowCount(), 1):
            q.append(0)
        q[0] = 1
        cognitiveModel.impulse_model(t=t, q=q)

        q = [0, 0, 0]
        for i in range(3,w.tableWidget.rowCount(), 1):
            q.append(0)
        q[2] = 1
        cognitiveModel.impulse_model(t=t, q=q)

        q = [0, 0, 0]
        for i in range(3,w.tableWidget.rowCount(), 1):
            q.append(0)
        q[0] = 1
        q[1] = 1
        cognitiveModel.impulse_model(t=t, q=q)

        q = [0, 0, 0]
        for i in range(3,w.tableWidget.rowCount(), 1):
            q.append(0)
        q[1] = 1
        try:
            q[5] = 1
        except:
            print('kek')
        cognitiveModel.impulse_model(t=t, q=q)

        w.result.setText(results)


def graph():
        A = get_A()
        if A.any() == None:
            QMessageBox.warning(w,'Error','Помилка обробки матриці')
            return

        cognitiveModel = CognitiveModel(A)
        cognitiveModel.draw_graph()

w.tool.clicked.connect(input)
w.upload.clicked.connect(upload)
w.remove.clicked.connect(remove)
w.add.clicked.connect(add)
w.analise.clicked.connect(analise)
w.graph.clicked.connect(graph)
app.exec_()
