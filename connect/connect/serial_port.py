from connect.connect.base import Connect, LostException, LackArgException
import serial
import utils
import re


class SerialPort(Connect):
    def __init__(self, name, args: dict = None, after_process=None, insist: bool = True):
        # 只传入 name 和 args，默认非坚持
        default_args = {
            'port': 'com11',
            'timeout': 1,
            'baud_rate': 115200,
            'read_size': 33
        }
        super().__init__(name, args, default_args, after_process=after_process, insist=insist)

    def get_handle(self) -> object:
        try:
            handle = serial.Serial(self.args['port'], self.args['baud_rate'], timeout=self.args['timeout'])
            return handle   # 连接成功返回句柄
        except serial.SerialException as e:
            return None     # 连接失败返回空

    def get_data(self) -> dict:
        try:
            # 读取数据
            data = self.handle.read(self.args['read_size'])
            # 读取数据长度不够，则被认为失去连接
            if len(data) < self.args['read_size']:
                raise LostException(self.name)
            return data
        except Exception as e:
            raise LostException(self.name)


if __name__ == '__main__':
    s = SerialPort('test', {'port': 'com11'}, insist=True)
    s.start()
