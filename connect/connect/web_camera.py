from connect.connect.base import Connect, LostException, LackArgException
import cv2


class WebCamera(Connect):
    def __init__(self, name, args: dict):
        default_args = {
            'url': 'rtsp://admin:a1234567@192.168.111.6:554/stream1'
        }
        super().__init__(name, args, default_args, insist=True)

    def get_handle(self) -> object:
        try:
            if self.args['url'] == 'local':
                self.args['url'] = 0
            camera = cv2.VideoCapture(self.args['url'])
            if camera.isOpened() is None:
                return False
        except KeyError as e:
            raise LackArgException(self.name, str(e))
        except Exception as e:
            return False

    def get_data(self) -> dict:
        try:
            # 读取数据
            ret, img = self.handle.read()
            if ret:
                img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
                return img
            else:
                raise LostException(self.name)
        except Exception as e:
            raise LostException(self.name)
