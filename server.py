import asyncio

from client import Client


class Server:
    port: int
    clients: list = []

    def __init__(self, port: int = 6969):
        self.port = port

    def run(self):
        loop = asyncio.get_event_loop()
        future = asyncio.start_server(self.handle_conn, "0.0.0.0", self.port, loop=loop)

        server = loop.run_until_complete(future)

        sock_name = server.sockets[0].getsockname()

        print("PyChat listening on:", sock_name[0] + ':' + str(sock_name[1]))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

    async def handle_conn(self, rx: asyncio.StreamReader, tx: asyncio.StreamWriter):
        client = Client(rx, tx, self)

        await client.start()

        await self.broadcast(client.name + " connected!")

        self.clients.append(client)

        await client.run()

        await self.broadcast(client.name + " disconnected!")


    async def broadcast(self, msg, exclude=None):
        if exclude is None:
            exclude = []

        tasks = []

        for client in self.clients:
            if client not in exclude:
                tasks.append(client.send_message(msg))

        if len(tasks) > 0:
            await asyncio.wait(tasks)
