import asyncio
import base64
import json


class Client:
    rx: asyncio.StreamReader
    tx: asyncio.StreamWriter
    name: str

    def __init__(self, rx: asyncio.StreamReader, tx: asyncio.StreamWriter, server):
        self.rx = rx
        self.tx = tx
        self.server = server

    async def start(self):
        self.name = await self.read_message()

        print(self.name + " connected!")

    async def run(self):
        msg = await self.read_message()

        while msg is not None:
            await self.server.broadcast(msg, {
                "type": "message",
                "data": {
                    "author_name": self.name,
                    "text": msg
                }
            })

            msg = await self.read_message()

    async def read_message(self):
        try:
            line = await self.rx.readline()

            # EOF, client disconnected
            if len(line) == 0:
                return None

            return json.loads(base64.b64decode(line))
        except:
            return None

    async def send_message(self, msg):
        self.tx.write(base64.b64encode(json.dumps(msg).encode("ascii")))
        self.tx.write(b'\n')
        await self.tx.drain()
