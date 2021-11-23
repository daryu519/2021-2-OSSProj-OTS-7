import threading
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel
from .online_data_temp import GuiEmit
import os
import signal


class OnlineLobby(QWidget):
    def __init__(self, gui_emit: GuiEmit):
        super().__init__()
        self.player_id = ""

        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.v1layout = QVBoxLayout()
        self.v2layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setLayout(self.hlayout)
        self.setLayout(self.v1layout)
        self.setLayout(self.v2layout)

        self.setGeometry(0, 0, 700, 700)
        self.setWindowTitle('OTS Lobby')
        self.name_label = QLabel("login success")
        self.layout.addWidget(self.name_label)

        self.layout.addLayout(self.hlayout)
        self.hlayout.addLayout(self.v1layout)
        self.hlayout.addLayout(self.v2layout)
        self.invite_label = QLabel("Approacher List")
        self.v1layout.addWidget(self.invite_label)

        self.list_box_approacher = QtWidgets.QListWidget()
        self.list_box_approacher.setGeometry(QtCore.QRect(250, 70, 201, 301))
        self.list_box_approacher.setDisabled(True)
        self.list_box_approacher.setObjectName("approacher_list")
        self.v1layout.addWidget(self.list_box_approacher)
        self.list_box_approacher.itemClicked.connect(self.approacher_list_item_clicked)

        self.wait_label = QLabel("Waiting List")
        self.v2layout.addWidget(self.wait_label)

        self.list_box_waiter = QtWidgets.QListWidget()
        self.list_box_waiter.setGeometry(QtCore.QRect(20, 70, 201, 301))
        self.list_box_waiter.setObjectName("waiting_list")
        self.v2layout.addWidget(self.list_box_waiter)
        self.list_box_waiter.itemClicked.connect(self.waiter_list_item_clicked)

        self.game_start_btn = QtWidgets.QPushButton("Wait for approachers")
        self.game_start_btn.setGeometry(QtCore.QRect(120, 280, 80, 26))
        self.game_start_btn.setObjectName("game_start_btn")
        self.game_start_btn.clicked.connect(self.game_start_btn_clicked)
        self.layout.addWidget(self.game_start_btn)

        self.list_item_msg_box = QtWidgets.QMessageBox()
        self.list_item_msg_box.setObjectName("list_item_msg_box")
        self.list_item_msg_box.resize(100, 80)
        self.list_item_msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        self.approaching_msg_box = QtWidgets.QMessageBox()  # 대결 제안시
        self.approaching_msg_box.setObjectName('approaching_msg_box')
        self.approaching_msg_box.resize(100, 80)
        self.approaching_msg_box.setStandardButtons(QMessageBox.Cancel)

        self.waiter_list = []
        self.approacher_list = []
        self.waiter_update()
        self.approacher_update()

        self.dialog = False

        self.gui_emit = gui_emit

        self.waiting = False

        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

    def set_view_waiting(self):
        self.list_box_waiter.setDisabled(True)
        self.list_box_approacher.setDisabled(False)
        self.game_start_btn.setText('Waiting...')

    def set_view_hello(self):
        self.list_box_waiter.setDisabled(False)
        self.list_box_approacher.setDisabled(True)
        self.game_start_btn.setText('Wait for approachers')

    def set_status_waiting(self):
        self.set_view_waiting()
        self.waiting = True
        self.emit_to_handler(t='wa')

    def set_status_hello(self):
        self.set_view_hello()
        self.waiting = False
        self.emit_to_handler(t='wr')

    def game_start_btn_clicked(self):
        if not self.waiting:
            self.waiting = True
            self.list_box_waiter.setDisabled(True)
            self.list_box_approacher.setDisabled(False)
            self.game_start_btn.setText('Waiting...')
            self.emit_to_handler(t='wa')
        elif self.waiting:
            self.waiting = False
            self.list_box_waiter.setDisabled(False)
            self.list_box_approacher.setDisabled(True)
            self.game_start_btn.setText("Wait for approachers")
            self.emit_to_handler(t='wr')

    def approacher_list_item_clicked(self, item):
        self.list_item_msg_box_dialog(item, at='ha', rt='hr', msg='의 대결 제안 수락')

    def waiter_list_item_clicked(self, item):
        self.list_item_msg_box_dialog(item, at='a', msg='에게 대결 제안')
        # self.waiter_approaching_dialog()
    #
    # def waiter_approaching_dialog(self):
    #     self.approaching_msg_box.show()
    #     self.approaching_msg_box.setText('대결 제안중...')
    #     msg_box_return = self.approaching_msg_box.exec()
    #     if msg_box_return == QMessageBox.Cancel:
    #         self.emit_to_handler(t='ac')
    #         self.approaching_msg_box.close()

    def list_item_msg_box_dialog(self, item, at: str, msg: str, rt: str = None):
        self.list_item_msg_box.show()
        user_id = item.text()
        self.list_item_msg_box.setText(user_id + msg)
        self.dialog = True
        msg_box_return = self.list_item_msg_box.exec()
        if msg_box_return == QMessageBox.Ok:
            print(user_id + msg)
            self.emit_to_handler(t=at, d=user_id)
        else:
            if rt is not None:
                self.emit_to_handler(t=rt, d=user_id)
            self.list_item_msg_box.close()
        
    def list_box_add(self, listbox: QtWidgets.QListWidget, ref: list):
        for itm in ref:
            if itm != self.player_id:
                listbox.addItem(itm)

    @staticmethod
    def list_box_clear(listbox: QtWidgets.QListWidget):
        lc = listbox.count()
        for i in range(lc):
            listbox.takeItem(0)

    def list_box_update(self, listbox: QtWidgets.QListWidget, ref: list):
        self.list_box_clear(listbox=listbox)
        self.list_box_add(listbox=listbox, ref=ref)

    def waiter_update(self):
        self.list_box_update(self.list_box_waiter, self.waiter_list)

    def approacher_update(self):
        self.list_box_update(self.list_box_approacher, self.approacher_list)

    def emit_to_handler(self, t: str, d: object = None):
        to_emit = {
            't': t,
            'd': d
        }
        self.gui_emit.to_handler.put(to_emit)

    @staticmethod
    def on_server_connection_lost():
        msg_box = QtWidgets.QMessageBox()
        msg_box.show()
        msg_box.resize(100, 80)

        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setText('서버와의 연결이 끊어졌습니다.')
        res = msg_box.exec()
        if res == QMessageBox.Ok:
            os.kill(os.getpid(), signal.SIGTERM)  # POSIX 신호인데 윈도우에서 일단 동작을 함.

