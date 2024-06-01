#!/usr/bin/python3
"""
used in deployment with aid of fabrics
"""
from os import path
from fabric.api import *


env.hosts = ["107.22.144.189", "52.3.241.179"]
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'


def do_deploy(archive_path):
    """
    deploy a static file to server
    """
    try:
        if not (path.exists(archive_path)):
                return False

        # upload archive
        put(archive_path, '/tmp/')

        # getting time_stamp
        timestamp = archive_path[-18:-4]
        run('sudo mkdir -p /data/web_static/releases/web_static_{}/'
            .format(timestamp))

        # Decompress archive
        run('sudo tar-xzf /tmp/web_static_{}.tgz -C \
                /data/web_static/releases/web_static_{}/'.format(timestamp, timestamp))

        # delete archive
        run('sudo rm /tmp/web_static_{}.tgz'.format(timestamp))

         # move contents into host web_static
         run('sudo mv /data/web_static/releases/web_static_{}/web_static/* \
                 /data/web_static/releases/web_static_{}/'.format(timestamp, timestamp))

          # remove extraneous web_static dir
          run('sudo rm -rf /data/web_static/releases/web_static_{}/web_static'
              .format(timestamp))

        # delete exisiting symbolic link
        run('sudo rm -rf /data/web_static/current/')
        
        # create new symbolic link
        run('sudo ln -s /data/web_static/releases/web_static_{}/ \
                /data/web_static/current'.format(timestamp))

    except:
        return False

    # where Sucess
    return True
