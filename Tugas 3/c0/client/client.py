import Pyro4
import Pyro4.errors
import time
import threading
import os
import sys
import uuid
from c0.client.heartbeat import Heartbeat

id = None
interval = 0
server = None
connected = True
connected_device = []

def get_server(id):
    try:
        uri = "PYRONAME:{}@localhost:7777".format(id)
        gserver = Pyro4.Proxy(uri)
        return gserver
    except:
        gracefully_exits()

def job_heartbeat() -> threading.Thread:
    global id
    heartbeat = Heartbeat(id)
    t1 = threading.Thread(target=job_heartbeat_failure, args=(heartbeat,))
    t1.start()

    t = threading.Thread(target=expose_function_heartbeat, args=(heartbeat, id,))
    t.start()
    return heartbeat, t, t1

def job_heartbeat_failure(heartbeat):
    while True:
        if time.time() - heartbeat.last_received > 2*interval:
            print("\nserver is down [DETECT BY heartbeat]")
            break
        time.sleep(interval)
    gracefully_exits()

def job_heartbeat_failure_all_to_all(id):
    server_heartbeat = get_server('heartbeat-{}'.format(id))
    while True:
        try:
            summary = server_heartbeat.get_summary_heartbeat(id)
            summary = summary.split(',')
            if summary[1] == 'none':
                pass
            else:
                if time.time() - float(summary[2]) > 2*interval:
                    print("\n{} is down [DETECT BY all heartbeat]\n> ".format(id))
                    # break
            time.sleep(interval)
        except:
            # print("\n{} is down [DETECT BY all heartbeat]\n> ".format(id))
            break

def expose_function_heartbeat(heartbeat, id):
    __host = "localhost"
    __port = 7777
    daemon = Pyro4.Daemon(host = __host)
    ns = Pyro4.locateNS(__host, __port)
    uri_server = daemon.register(heartbeat)
    ns.register("heartbeat-{}".format(id), uri_server)
    daemon.requestLoop()

def communicate() -> bool:
    try:
        res = server.ok()
        if res.value == 'ok':
            pass
    except:
        return False
    return True

def ping_server():
    global connected
    while True and connected:
        alive = communicate()
        if not alive:
            alive = communicate()
            if not alive:
                print("\nserver is down [DETECT BY ping ack]")
                break
        time.sleep(interval)
    gracefully_exits()

def get_connected_device_from_server() -> list:
    try:
        conn_device = server.connected_device_ls()
        conn_device.ready
        conn_device.wait(1)
        conn_device = clear_connected_device(conn_device.value.split(','), id)
    except:
        return None
    return conn_device

def job_ping_server_ping_ack() -> threading.Thread:
    t = threading.Thread(target=ping_server)
    t.start()
    return t

def register_new_clients(heartbeat):
    while True:
        conn_device = get_connected_device_from_server()
        all_to_al_heartbeat_job(heartbeat, conn_device)
        time.sleep(interval)

def job_check_updated_device_from_server(heartbeat) -> threading.Thread:
    t = threading.Thread(target=register_new_clients, args=(heartbeat,))
    t.start()
    return t

def gracefully_exits():
    # unregister device on server
    server.connected_device_delete(id)
    print("disconnecting..")
    time.sleep(0.5)
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

def clear_connected_device(devices, id) -> list:
    if id in devices:
        devices.remove(id)
    return devices

def all_to_al_heartbeat_job(heartbeat, devices):
    for device in devices:
        if device not in connected_device:
            connected_device.append(device)
            heartbeat.new_thread_job(device)

            t1 = threading.Thread(target=job_heartbeat_failure_all_to_all, args=(device,))
            t1.start()

def call_create(proxy,filenames):
    response = proxy.create(filenames)
    print(response)

def call_read(proxy,filename):
    response = proxy.read(filename)
    print(response)

def call_update(proxy,filename,data):
    response = proxy.update(filename,data)
    print(response)

def call_delete(proxy,filenames):
    response = proxy.delete(filenames)
    print(response)

def call_list(proxy):
    response = proxy.list()
    print(response)

def makeProxy():
    uri = "PYRONAME:filemanager@localhost:7777"
    proxy = Pyro4.Proxy(uri)
    return proxy

def manageCommand(cmd):
    listCommand = ['list','create','read','update','delete','help']
    cmdArr = cmd.split(' ')

    if cmdArr[0] == 'exit':
        return ['exit','Program closed']

    if cmdArr[0] in listCommand:
        return cmdArr
    elif cmdArr[0] not in listCommand:
        return ['error','Command unknown']
    else:
        return None

def start_program():
    while True:
        command = input("Type here : ")
        command = manageCommand(command)
        if command[0] == 'create':
            call_create(server,command[1:])
        elif command[0] == 'read':
            call_read(server,command[1])
        elif command[0] == 'update':
            params = " ".join(command[2:]);
            call_update(server,command[1],params)
        elif command[0] == 'delete':
            call_delete(server,command[1:])
        elif command[0] == 'list':
            call_list(server)
        elif command[0] == 'error':
            print(command[1])
        elif command[0] == 'exit':
            print(command[1])
            exit()
        elif command[0] == 'help':
            print("List of commands : ")
            print("1. create [filename1] [filename2] ...")
            print("2. read [filename]")
            print("3. update [filename] [parameter]")
            print("4. delete [filename1] [filename2] ...")
            print("5. list")
            print("6. exit")

if __name__=='__main__':
    # core
    server = get_server('server')
    try:
        interval = server.ping_interval()
    except:
        print('server not running')
        sys.exit(0)
    server._pyroTimeout = interval
    server._pyroAsync()

    # device id
    id = str(uuid.uuid4())
    print('-->-->--> registered id : {}'.format(id))

    # register device on server (heartbeat)
    server.connected_device_add(id)

    heartbeat, thread_heartbeat, thread_heartbeat_detector = job_heartbeat()
    thread_ping_ack = job_ping_server_ping_ack()

    # register failure detector on server
    server.new_thread_job(id)

    conn_device = get_connected_device_from_server()
    all_to_al_heartbeat_job(heartbeat, conn_device)
    thread_get_connected_device_list = job_check_updated_device_from_server(heartbeat)

    start_program()

    connected = False
    # thread_get_connected_device_list.join()
    thread_ping_ack.join()
    # thread_heartbeat.join()
    # thread_heartbeat_detector.join()
    gracefully_exits()