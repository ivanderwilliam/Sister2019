import Pyro4


def setupClient():
    uri = "PYRONAME:greetserver@localhost:8909"
    Greeserver = Pyro4.Proxy(uri)

    while True:
        inputs = input().split(' ', 2)
        command = inputs[0]
        if command == 'create':
            Greeserver.create(inputs[1])
        elif command == 'read':
            Greeserver.read(inputs[1])
        elif command == 'update':
            Greeserver.update(inputs[1], inputs[2])
        elif command == 'delete':
            Greeserver.delete(inputs[1])
         elif command == 'list':
             Greeserver.list()


if __name__ == '__main__':
    print('Commands :')
    print('create [file]')
    print('read [filename]')
    print('update [file] [text]')
    print('delete [file/folder]')
    print('list')

    setupClient()
