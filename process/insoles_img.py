from pipeline.core import Worker, Frame
import cv2
from pipeline.log import Log
import utils
import copy

logger = Log.get_log()

class InsolesImg(Worker):
    def __init__(self, name: str = 'insoles_img', keys: list = None):
        super().__init__(name)
        if keys is None:
            keys = []
        self.background = None
        self.keys = keys
        self.centroids = []

        # 尝试读取鞋垫背景
        try:
            self.background = cv2.imread('./data/insoles.jpg')
            # 获得灰度化图片
            gray_img = cv2.cvtColor(self.background, cv2.COLOR_BGR2GRAY)
            # 获得二值化图片
            ret, t_img = cv2.threshold(gray_img, 250, 255, cv2.THRESH_BINARY)
            # 获得中心
            ret, labels, stats, centroids = cv2.connectedComponentsWithStats(t_img)

            # 过滤掉不正确的中心点，并将中心点设置为整形
            for c in centroids:
                c = [int(i) for i in c]
                if t_img[c[1]][c[0]] == 255:
                    self.centroids.append(c)
        except Exception as e:
            logger.warning(e)
            self.switch = False

    def process(self, frame: Frame):
        for k in self.keys:
            if k in frame.data.keys():
                try:
                    t_data = utils.insoles_after_process(frame.data[k])
                    bg = copy.deepcopy(self.background)
                    for i, p in enumerate(t_data['press']):
                        if p > 5:
                            cv2.circle(bg, (self.centroids[i][0], self.centroids[i][1]), p // 5, (0, 0, 255), -1)
                    bg = cv2.resize(bg, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
                    frame.data['insoles_data'.format(k)] = t_data
                    frame.data['insoles_img'] = bg
                    cv2.imshow('insoles', bg)
                    cv2.waitKey(1)
                except Exception as e:
                    pass
        return frame

    def decode(self):
        pass



