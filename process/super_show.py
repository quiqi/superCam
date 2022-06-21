from pipeline.core import Worker, Node, Frame
import tkinter
from tkinter import messagebox
from pipeline.mul import MulIgnition
import threading


class SuperShow(Worker, tkinter.Frame):
    def __init__(self, name: str = 'super_show', img_keys: list = None, plt_keys: list = None):
        super(SuperShow, self).__init__(name)
        self.windows = None
        self.img_keys = img_keys
        self.plt_keys = plt_keys
        self.i = 0
        self.data_dict = {
            'img': {},
            'curve': {}
        }

    def process(self, frame: Frame):
        self.i += 1
        if self.windows is None:
            self.windows = _Windows(self)
            self.windows.start()
        for k in list(frame.data.keys()):
            if k in self.img_keys:
                self.data_dict['img'][k] = frame.data[k]
            elif k in self.plt_keys:
                self.data_dict['curve'][k] = frame.data[k]
        # print(self.data_dict)
        return frame


class _Windows(tkinter.Frame, threading.Thread):
    def __init__(self, worker: SuperShow):
        threading.Thread.__init__(self)
        self.root = None
        self.worker = worker
        self.module = {}

    def run(self) -> None:
        self.root = tkinter.Tk()
        self.root.geometry('600x600')
        tkinter.Frame.__init__(self, self.root)
        self.module['btn'] = tkinter.Button(self)
        self.pack()
        # self.refresh_data()
        self.after(50, self.refresh_data)
        self.root.mainloop()

    def refresh_data(self):
        data = self.worker.data_dict
        for k in data['img']:
            if k not in self.module.keys():
                self.module[k] = tkinter.Canvas(self, width=600, height=300)

        self.root.after(50, self.refresh_data)

    def sh(self):
        messagebox.showinfo('a', str(self.worker.i))