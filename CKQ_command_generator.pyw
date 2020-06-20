# -*- coding: utf-8 -*-
"""
开发者：周梦雄
最后更新日期：2020/6/12
"""
import sys
import pyperclip
import re
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QTableWidget,
    QMessageBox,
)
from Ui_chip_id_assignment import *
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp


class MyMainWindow(QMainWindow, Ui_chip_id_assignment):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # MAC地址取值范围 ：0-9，A-F
        reg = QRegExp("[0-9A-Fa-f]+")
        MacValidator = QRegExpValidator(reg)
        self.le_mac.setValidator(MacValidator)

        self.statusbar.setStyleSheet(
            "* { color: #00CD00;font-size:30px;font-weight:bold;}")        
        self.le_mac.editingFinished.connect(self.GenerateMessage)
        self.show()

    def GenerateMessage(self):
        print(len(self.le_mac.text()))
        if len(self.le_mac.text()) != 12:
            QMessageBox.warning(
                self, '错误：', '您输入的MAC地址不是12位，请重新输入！', QMessageBox.Ok)
            self.le_mac.setFocus()
        else:
            try:
                mac_list = re.findall(r'.{2}', self.le_mac.text())
                mac_last3_byte = mac_list[-3:]
                mac_last3_byte_decimal = [int(e, 16) for e in mac_last3_byte]
                # 加0x33
                mac_last3_byte_add33_hex = ['{:X}'.format(e) for e in [(e1 + 51) for e1 in mac_last3_byte_decimal]]
                # mac_last_byte_dec_add33 = [hex(e+51) for e in mac_last3_byte_decimal]
                command_prefix = ['68', 'DC', 'EE', 'EB', 'DC', 'BB', 'CE', '68', '1E', '0C', '35', '45', '32', '31', 'FF', 'FF',
                                'FF']
                # 固定前缀连接mac地址后3字节+"00"+"00"
                command_com = command_prefix + mac_last3_byte_add33_hex + ['00'] * 2
                # print(command_com)
                command_com_decimal = [int(e, 16) for e in command_com]
                check_byte = '{:02X}'.format(sum(command_com_decimal) % 256)
                command_with_check_byte = command_com + [check_byte, '16']
                print("串口指令为：%s" % ' '.join(command_with_check_byte))
                self.textBrowser.setText("MAC地址："+self.le_mac.text()+'\n'+"报文："+' '.join(command_with_check_byte))
                pyperclip.copy(' '.join(command_with_check_byte))
                self.statusbar.showMessage("报文已复制到剪贴板", 5000)
                mac_ccc = "CCCCCC" + self.le_mac.text()[-6:]
                self.le_mac.clear()
                with open("mac数据.txt", 'a') as f:
                    f.writelines(mac_ccc+'\n')

            except Exception:
                return



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyMainWindow()
    sys.exit(app.exec_())
