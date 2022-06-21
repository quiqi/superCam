def args2dict(kvs: list):
    args = {}
    for kv in kvs:
        kv = kv.split(':')
        try:
            args[kv[0]] = eval(kv[1])
        except Exception as e:
            raise e
    return args


def is_num(s: str):
    # 如果是整数，直接返回
    if s.isdigit():
        return True
    # 如果是小数，先以小数点分割成两个部分，然后分别判断
    if '.' in s:
        ss = s.split('.')
        if len(ss) == 2:
            if ss[0].isdigit() and ss[1].isdigit():
                return True
    return False


def insoles_after_process(data):
    t_data = data[:-1]
    # 转为字符串
    t_data = t_data.decode('us-ascii').split(' ')
    # 压力传感器数据
    press = [int(i) for i in t_data[0].split('-')]

    # 三轴陀螺仪数据
    ax1 = int(t_data[1])
    ax2 = int(t_data[2])
    ax3 = int(t_data[3])
    return {
        'press': press,
        'axs': [ax1, ax2, ax3]
    }


if __name__ == '__main__':
    ns = ['asdf', 'sd.dd', '123a.d', '123.4', '654.2', '123.0', '123.0654']
    for n in ns:
        print(n, is_num(n))