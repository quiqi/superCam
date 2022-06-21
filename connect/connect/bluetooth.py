import asyncio
from bleak import BleakClient
from connect.connect.base import Connect, LostException, LackArgException
import _thread


class Bluetooth(Connect):
    original_data = None

    def __init__(self, name: str = 'bt', args: dict = None):
        default_args = {
            'addr': 'EC:62:60:92:EB:92',
            'UUID': '0000abf2-0000-1000-8000-00805f9b34fb'
        }
        super().__init__(name, args, default_args, insist=True)

    def get_handle(self) -> object:
        try:
            asyncio.run(self._get_handle())
        except Exception as e:
            return print(e)
        return self.handle

    async def _get_handle(self):
        client = BleakClient(self.args['addr'])
        b = await client.connect()
        print('is connect:{}'.format(b))
        self.handle = client
        _thread.start_new_thread(self.read_thead, ())

    def get_data(self) -> dict:
        try:
            data = Bluetooth.original_data
            # print(data)
            return data
        except Exception as e:
            raise LostException(self.name)

    @staticmethod
    def notification_handler(sender, data):
        Bluetooth.original_data = data

    async def _get_data(self):
        await self.handle.start_notify(self.args['UUID'], Bluetooth.notification_handler)
        # await self.handle.stop_notify(self.args['UUID'])
        while self.status != 'close':
            await asyncio.sleep(0.1)
        await self.handle.stop_notify(self.args["UUID"])

    def read_thead(self):
        asyncio.run(self._get_data())


if __name__ == "__main__":
    b = Bluetooth()
    b.handle = b.get_handle()
    while True:
        d = b.get_data()
        print(d)
