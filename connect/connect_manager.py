import json
import time

from pipeline.core import Worker, Frame
from pipeline.log import Log
from connect.connect.base import Connect
from connect.factory import *
from typing import Dict
import utils


logger = Log.get_log()


class ConnectManager(Worker):
    connects: Dict[str, Connect]

    def __init__(self, name: str = 'connect_manager', cfg: str = 'sensors.json'):
        super().__init__(name)
        self.switch = True
        self.connects = {}
        self.connects_dict = {}
        self.datas = {}
        self.factory = factory
        self.cfg = cfg
        self.load_cfg()

    def process(self, frame: Frame):
        for c in self.connects:
            if self.connects[c].update:
                frame.data['Sensor_{}'.format(c)] = self.connects[c].data
                self.connects[c].update = False
        return frame

    def my_act(self, order_head, order_args):
        hit = True
        # 显示命令
        if order_head == 'sensor':
            self.show(order_args)
        # 刷新命令，重新读取配置文件
        elif order_head == 're':
            self.load_cfg()
            self.refresh()
        # 连接命令
        elif order_head == 'cn':
            if len(order_args) == 1 and order_args[0] in self.connects_dict.keys():
                args = self.connects_dict[order_args[0]]
                self.add_connect(order_args[0], args['type'], args['args'])
            elif len(order_args) >= 2:
                args = utils.args2dict(order_args[2:])
                self.add_connect(order_args[0], order_args[1], args)

        elif order_head == 'cfg':
            for k in self.connects_dict:
                print('{}:{}'.format(k, self.connects_dict[k]))

        else:
            hit = False
        return hit

    def show(self, order_args: list):
        if order_args is None:
            order_args = []
        if len(order_args) == 0:
            for k in self.connects:
                print(self.connects[k])
        else:
            for order_arg in order_args:
                if order_arg in self.connects.keys():
                    print(self.connects[order_arg])
                else:
                    print('can not find the connect named {}'.format(order_arg))

    # 读取 cfg 文件
    def load_cfg(self):
        with open(self.cfg, 'r') as f:
            try:
                t_dict = json.load(f)
            except Exception as e:
                logger.warning(e)
                logger.warn('an error occurred while reading {}'.format(self.cfg))
            for name in t_dict:
                self.add_dict(name, t_dict[name])

    # 添加新的 dict
    def add_dict(self, name: str, t_dict: dict):
        # 只有当数据会发生改变时，才更新数据
        t_dict['_MOD'] = False
        if not (name in self.connects_dict.keys() and t_dict == self.connects_dict[name]):
            t_dict['_MOD'] = True
            self.connects_dict[name] = t_dict

    # 添加新的 connect
    def add_connect(self, name, key, cfg_dict):
        # 如果这个线程还在，且配置已经被修改，则关闭这个线程，如果还在，但没有被修改，则保持原样
        if name in self.connects.keys() and self.connects[name].is_alive():
            # 如果配置已经被修改
            if self.connects_dict[name]['_MOD']:
                self.connects[name].close()             # 关闭连接
                while self.connects[name].is_alive():   # 阻塞直到线程关闭
                    time.sleep(0.01)
            # 如果配置没有被修改，直接返回
            else:
                return
        # 尝试连接
        try:
            connect = self.factory(key, name, cfg_dict)
            if connect is not None:
                self.connects[name] = connect
                self.connects[name].start()
                self.connects_dict[name]['_MOD'] = False
                logger.info('Create the sensors {}: {}'.format(name, self.connects[name]))
            else:
                logger.info('Such sensors {} cannot be found in factory'.format(key))
        except Exception as e:
            logger.warn('sensor {} initialization failed!')
            logger.warning(e)

    # 刷新
    def refresh(self):
        for name in list(self.connects_dict):
            print(self.connects_dict)
            self.add_connect(name, self.connects_dict[name]['type'], self.connects_dict[name]['args'])







