from server_api import *
import Pyro4


def start_without_ns():
    daemon = Pyro4.Daemon()
    GreetServers = Pyro4.expose(GServers)
    uri = daemon.register(GreetServers)
    print("URI : ", uri)
    daemon.requestLoop()

    # NS harus start  -> pyro4-ns -n localhost -p 8909
    # cek service NS -> pyro4-nsc -n localhost -p 8909 list

def start_with_ns():
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 7777)
    Class = Pyro4.expose(GServers)
    uri_greetserver = daemon.register(Class)
    print("URI greetserver : ", uri_greetserver)
    ns.register("greetserver", uri_greetserver)
    daemon.requestLoop()


if __name__ == '__main__':
    start_with_ns()
