import os
import time
import Pyro4
import Pyro4.errors
import threading

class Server(object):
    def __init__(self):
        self.connected_device = []
        self.connected_device_thread_job = []

    @Pyro4.expose
    def connected_device_list(self) -> str:
        return 'Connected device => ' + ', '.join(self.connected_device)

    @Pyro4.expose
    def connected_device_add(self, id):
        print('Register '+ id)
        self.connected_device.append(id)

    @Pyro4.expose
    def connected_device_delete(self, id):
        print('Unregister '+ id)
        self.connected_device.remove(id)

    @Pyro4.expose
    def command_not_found(self) -> str:
        return "Not Found"

    @Pyro4.expose
    def command_success(self) -> str :
        return "Success"

    @Pyro4.expose
    def bye(self) -> str:
        return "bye"

    @Pyro4.expose
    def ok(self) -> str:
        return "Ok"

    @Pyro4.expose
    def fail(self) -> str:
        return "Failed"

    @Pyro4.expose
    def max_retries(self) -> int:
        return 2

    @Pyro4.expose
    def ping_interval(self) -> int:
        return 3

    @Pyro4.expose
    def new_thread_job(self, id) -> str:
        threads = threading.Thread(target=self.__new_thread_job, args=(id,))
        threads.start()
        self.connected_device_thread_job.append(threads)
        return self.ok()

    def __connect_heartbeat_server(self, id):
        time.sleep(self.ping_interval())
        try:
            uri = "PYRONAME:heartbeat-{}@localhost:7777".format(id)
            server = Pyro4.Proxy(uri)
        except:
            return None
        return server

    def __new_thread_job(self, id):
        server = self.__connect_heartbeat_server(id)
        while True:
            try:
                res = server.signal_heartbeat()
                print(res)
            except (Pyro4.errors.ConnectionClosedError, Pyro4.errors.CommunicationError) as e:
                print(str(e))
                break
            time.sleep(self.ping_interval())

    @Pyro4.expose
    def down_my_server(self) -> str:
        time.sleep(self.ping_interval() + 1)
        return self.ok()

    @Pyro4.expose
    def list(self):
        listFiles = os.listdir("files")
        return listFiles

    @Pyro4.expose
    def create(self,filename):
        for f_name in filename:
            exist = os.path.isfile("files/" + f_name)
            if not exist:
                f = open("files/"+f_name,"w")
                f.close()
        return "Successfully created"

    @Pyro4.expose
    def read(self,filename):
        exist = os.path.isfile("files/" + filename)
        if exist:
            f = open("files/"+filename,"r")
            data = f.read()
            f.close()
            return data
        else:
            return "Not found"

    @Pyro4.expose
    def update(self,filename,data):
        exist = os.path.isfile("files/" + filename)
        if exist:
            f = open("files/"+filename,"w")
            f.write(data)
            f.close()
            return "Successfully updated"
        else:
            return "Not found"

    @Pyro4.expose
    def delete(self,filename):
        for f_name in filename:
            exist = os.path.isfile("files/" + f_name)
            if exist:
                os.remove("files/"+f_name)
        return "Successfully deleted"