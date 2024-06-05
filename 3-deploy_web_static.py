#!/usr/bin/python3
# Fabfile to create and distribute an archive to a web server.
import os.path
from datetime import datetime
from fabric.api import env
from fabric.api import local
from fabric.api import put
from fabric.api import run

env.hosts = ["107.22.144.189", "52.3.241.179"]

def do_pack():
    """Create a tar gzipped archive of the directory web_static."""
    try:
        dt = datetime.utcnow()
        file = "versions/web_static_{}{}{}{}{}{}.tgz".format(dt.year,
                                                             dt.month,
                                                             dt.day,
                                                             dt.hour,
                                                             dt.minute,
                                                             dt.second)
        if not os.path.isdir("versions"):
            local("mkdir -p versions")
        local("tar -cvzf {} web_static".format(file))
        return file
    except Exception as e:
        print(f"Error creating archive: {e}")
        return None

def do_deploy(archive_path):
    """Deploy web files to server
    """
    try:
        if os.path.isfile(archive_path) is False:
            return False
        file = archive_path.split("/")[-1]
        name = file.split(".")[0]

        # upload archive
        put(archive_path, '/tmp/{}'.format(file))

        # create target dir
        run('sudo mkdir -p /data/web_static/releases/{}'.format(name))

        # uncompress archive and delete .tgz
        run('sudo tar -xzf /tmp/{} -C /data/web_static/releases/{}/'.format(file, name))

        # remove archive
        run('sudo rm /tmp/{}'.format(file))

        # move contents into host web_static
        run('sudo mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/'.format(name, name))

        # remove extraneous web_static dir
        run('sudo rm -rf /data/web_static/releases/{}/web_static'.format(name))

        # delete pre-existing sym link
        run('sudo rm -rf /data/web_static/current')

        # re-establish symbolic link
        run('sudo ln -s /data/web_static/releases/{}/ /data/web_static/current'.format(file))
    except Exception as e:
        return False

    # return True on success
    return True

def deploy():
    """Create and distribute an archive to a web server."""
    file = do_pack()
    result = do_deploy(file)
    return result
