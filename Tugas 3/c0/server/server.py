from c0.server.service import Server
import Pyro4

def start_server(host="localhost",port=7777):
    daemon = Pyro4.Daemon(host=host)
    ns = Pyro4.locateNS(host, port)
    server = Server()
    uri = daemon.register(server)
    print("Uri : ", uri)
    ns.register("server", uri)
    daemon.requestLoop()

if __name__ == '__main__':
    start_server();