import threading
import time
import traceback
from pipeline.log import Log

logger = Log.get_log()


class LostException(Exception):
    def __init__(self, connect_name: str):
        self.msg = '{} disconnect'.format(connect_name)
        super().__init__(self, self.msg)


class LackArgException(Exception):
    def __init__(self, connect_name: str, lack_arg):
        self.msg = 'for {}, {} is a necessary parameter'.format(connect_name, lack_arg)
        super().__init__(self, self.msg)


class Connect(threading.Thread):
    def __init__(self, name, args: dict, default_args: dict, after_process=None,
                 lost_max: int = 5, insist: bool = False, interval: float = 0.2):
        """
        初始化函数
        :param name: 名字
        :param lost_max: 最大失连次数，超过最大失联次数将重新连接或关闭
        :param insist: 当连接失败时是放弃连接还是进入监听状态
        :param kwargs:
        """
        super(Connect, self).__init__()
        self.name = name  # 名字
        self.args = default_args  # 使用默认参数

        # 传入参数，若传入参数不为空，则覆盖默认参数
        if args is not None:
            for k in args:
                self.change_arg(k, args[k])

        # 当前连接器的状态，'connecting' 表示正在连接状态，'connected' 表示已连接状态, 'listening' 表示监听中, 'close' 表示关闭
        self.status = 'connecting'

        self.data = None  # 当下数据，实际是一个通信变量
        self.update = False  # 指示 data 是否更新

        self.handle = None  # 连接句柄

        self.lost_max = lost_max  # 最多断联 lost_max 后重新连接
        self.lost = 0  # 失连次数

        self.insist = insist  # 是否坚持连接， 如果坚持连接，在连接失败后会进入监听状态
        self.interval = interval  # 监听间隔
        self.last_time = time.time()
        self.switch = True

        self.after_process = after_process

    def connect(self):
        try:
            self.handle = self.get_handle()
            if self.handle is not None:
                self.status = 'connected'  # 连接成功则进入已连接状态
                logger.info('connection successful:{}'.format(self))
            elif self.insist:
                self.status = 'listening'  # 如果坚持连接，则进入监听状态
                logger.info('connection unsuccess, we will try again in {}s, {}'.format(self.interval, self))
            else:
                self.status = 'close'  # 如果不坚持连接，则进入关闭状态，线程将退出
                logger.info('connection unsuccess, the thread will close, {}'.format(self))
        except LackArgException as e:
            logger.info(e)
            self.status = 'close'
            logger.info('connection unsuccess, the thread will close, {}'.format(self))

    def get_handle(self) -> object:
        """
        待重写方法
        :return: 连接成功返回连接之后的句柄，否则返回 None
        """
        return None

    def read(self):
        try:
            self.data = self.get_data()  # 获得数据
            # 后处理
            if self.after_process is not None:
                self.data = self.after_process(self.data)
            self.update = True  # 设置更新
            self.lost = 0  # lost 置为 0
        except LostException as e:
            self.lost += 1
            logger.info('Lost connection {}/{}...'.format(self.lost, self.lost_max))
            if self.lost >= self.lost_max:
                if self.insist:
                    self.status = 'listening'
                    logger.info('The connection is lost for several times, '
                                'and the listening state is displayed... {}'.format(self))
                else:
                    self.status = 'close'
                    logger.info('The connection is lost for several times, '
                                'and the connect will be closed. {}'.format(self))

    def get_data(self) -> dict:
        pass

    def run(self):
        while self.status != 'close' and self.switch:
            if self.status == 'connected':
                self.read()  # 已连接模式下，从read中读取数据
            elif self.status == 'connecting':
                self.connect()  # 正在连接模式下，重新连接
            elif self.status == 'listening':
                # 在监听模式下,每隔 self.interval 的时间，将 status 设置为 connecting
                if time.time() - self.last_time > self.interval:
                    self.last_time = time.time()
                    self.status = 'connecting'

    def close(self):
        self.status = 'close'
        self.switch = False

    def update_args(self, args: dict):
        for k in args:
            self.args[k] = args[k]

    def __str__(self):
        return 'name:{}\targs:{}\tstatu:{}'.format(self.name, self.args, self.status)

    def input_args(self):
        for arg_name in self.args:
            t_args = input('{}(default {}):'.format(arg_name, self.args[arg_name]))
            while not self.change_arg(arg_name, t_args):
                print('argument {} must be of type {}'.format(arg_name, type(self.args[arg_name])))
                t_args = input('{}(default {}):'.format(arg_name, self.args[arg_name]))

    def change_arg(self, key: str, value):
        if key not in self.args.keys() or self.args[key] is None:
            self.args[key] = value  # 如果原本没有这个参数，或这个参数为空，则直接赋值
            return True
        else:
            # 如果这个值和原来的值是同一个类型
            if isinstance(value, type(self.args[key])):
                self.args[key] = value  # 如果原本这个参数为字符串，也直接赋值
                return True

            # 如果这个值是字符串类型，尝试用 value转换
            elif isinstance(value, str):
                try:
                    value = eval(value)
                    # 转换成功后如果为同一个类型则赋值
                    if isinstance(value, type(self.args[key])):
                        self.args[key] = value
                        return True
                    # 否则不赋值
                    else:
                        return False
                # 转换失败不赋值
                except Exception as e:
                    return False
            else:
                return False


