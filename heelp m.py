import asyncio
from asyncio import transports


class ClientProtocol(asyncio.Protocol):
    login: str
    password: str
    server: 'Server'
    transport: transports.Transport
    clients_list: list
    clients_pass: list
    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None
        self.password = None
        self.clients_list=[]
        self.clients_pass=[]
    def data_received(self, data: bytes):
        decoded = data.decode()
        prinim_dannie=decoded.split()
        potv=False
        pris_login=False
        if self.login is None:
            # login:User
            self.list_client()
            self.list_pass()
            if prinim_dannie[0].startswith("login:") and prinim_dannie[1].startswith("password:"):
                self.login = prinim_dannie[0].replace("login:", "").replace("\r\n", "")
                self.password = prinim_dannie[1].replace("password:", "").replace("\r\n", "")
                for ik in self.server.clients:
                    if ik.login==self.login:
                        self.transport.write(f"Пользователь <{self.login}> уже зашел!\n".encode())
                        self.transport.close()
                if self.clients_list!=[]:
                    for prov in range(len(self.clients_list)):
                        if self.clients_list[prov]==self.login:
                            if self.clients_pass[prov]==self.password:
                                self.transport.write(
                                    f"Привет, <{self.login}>!\n".encode()
                                )
                                self.server.clients.append(self)
                                self.send_history()
                                pris_login=True
                                break
                            else:
                                self.transport.write(
                                    f"Клиент с ником <{self.login}> уже зарегестрирован, а пароль не верный!\n".encode()
                                )
                                pris_login=True
                                self.transport.close()
                if pris_login==False:
                    self.new_client()
                    self.server.clients.append(self)
                    text=f"Добро пожаловать, <{self.login}>\n"
                    self.transport.write(text.encode())
                    self.send_history()
                    for pols in self.server.clients:
                        if pols.login!=self.login:
                            pols.transport.write(f"Поприветствуем пользователя <{self.login}>!\n".encode())
        hist=True
        if decoded.startswith("login:"):
            hist=False
        if self.login!=None and hist:
            print(decoded)
            self.send_message(decoded)
            self.server.messeges.append(f"<{self.login}> "+decoded+"\n")
            if len(self.server.messeges)>10:
                self.server.messeges.remove(self.server.messeges[0])
    def send_message(self, message):
        format_string = f"<{self.login}> {message}"
        encoded = format_string.encode()

        for client in self.server.clients:
            if client.login != self.login:
                client.transport.write(encoded)
    def send_history(self):
        msg=[]
        for i in self.server.messeges:
            msg.append("> "+i)
        for k in msg:
            self.transport.write(k.encode())
    def new_client(self):
        dob=open("test.txt", "a")
        dob.write(f"{self.login}\n")
        dob.close
        dob=open("pass.txt", "a")
        dob.write(f"{self.password}\n")
        dob.close()
    def list_client(self):
        dob=open("test.txt")
        dob=dob.readlines()
        for i in dob:
            self.clients_list.append(i.replace("\r\n", "").replace("\n", ""))
    def list_pass(self):
        dob=open("pass.txt")
        dob=dob.readlines()
        for k in dob:
            self.clients_pass.append(k.replace("\r\n", "").replace("\n", ""))
    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        print("Соединение установлено")
        msg="Введите логин\n>>>Пример ввода: login:логин password:пароль".encode()
        self.transport.write(msg)

    def connection_lost(self, exception):
        if self in self.server.clients:
            self.server.clients.remove(self)
        print("Соединение разорвано")


class Server:
    clients: list
    messeges: list
    def __init__(self):
        self.clients = []
        self.messeges = []
    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()

process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("\nСервер остановлен вручную")