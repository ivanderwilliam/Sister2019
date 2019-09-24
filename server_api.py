import glob
import os

class GServers:

    def create(self, filename):
        fd = open(filename, 'w+')

    def read(self, filename):
        fd = open(filename, 'r')
        for isi in fd:
            print(isi)
        fd.close()

    def update(self, filename, text):
        fd = open(filename, 'w')
        fd.write(text)

    def delete(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif len(os.listdir(path)) == 0:
                os.rmdir(path)

    def list(self):
        dir_list = glob.glob('/*')
        dir_list = map(
            lambda path: {'name': path.split('/')[-1], 'is': os.path.isfile(path)},
            dir_list
        )
        for dir in dir_list:
            dir_type = ''
            if dir['is']:
                dir_type = 'file'
            else:
                dir_type = 'folder'
            print('-> ' + dir['name'] + '     [{}]'.format(dir_type))