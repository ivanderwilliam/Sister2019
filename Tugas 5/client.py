import Pyro4
import base64
import json
import sys

instanceName = sys.argv[1]

def get_fileserver_object():
    uri = "PYRONAME:{}@localhost:7777" . format(instanceName)
    fserver = Pyro4.Proxy(uri)
    fserver.setName(instanceName)
    fserver.setPyroObject()
    return fserver

def manageCommand(cmd):
    listCommand = ['list', 'create', 'read', 'update', 'delete', 'instruction']
    cmdArr = cmd.split(' ')

    if cmdArr[0] == 'exit':
        return ['exit', 'Bye']
    if cmdArr[0] in listCommand:
        return cmdArr
    elif cmdArr[0] not in listCommand:
        return ['error', 'Format Error']
    else:
        return None

if __name__=='__main__':
    proxy = get_fileserver_object()
    while True:
        command = input("Type here : ")
        command = manageCommand(command)
        if command[0] == 'create':
            print(proxy.create(command[1],instanceName))
        elif command[0] == 'read':
            print(proxy.read(command[1]))
        elif command[0] == 'update':
            print(proxy.update(command[1],command[2],instanceName))
        elif command[0] == 'delete':
            print(proxy.delete(command[1],instanceName))
        elif command[0] == 'list':
            print(proxy.list())
        elif command[0] == 'instruction':
            print("Commands Instructions ")
            print("1. create [name]")
            print("2. read [name]")
            print("3. update [name]")
            print("4. delete [name]")
            print("5. list")
            print("6. instruction")
            print("7. exit")
        elif command[0] == 'error':
            print(command[1])
        elif command[0] == 'exit':
            print(command[1])
            exit()
