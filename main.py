from pipeline.core import *
from connect.connect_manager import ConnectManager
from process.super_show import SuperShow
from process.insoles_img import InsolesImg
from pipeline.mul import MulIgnition
import utils


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    MulIgnition([
        Node('head', subsequents=['node1']),
        Node('node1', subsequents=['node2'], worker=ConnectManager()),
        Node('node2', worker=InsolesImg(keys=['Sensor_b1'])),
        # Node('node3', worker=SuperShow())
    ]).run()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
