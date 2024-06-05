#!/usr/bin/python3
# Fabfile to create and distribute an archive to a web server.
import os.path
from datetime import datetime
from fabric.api import env, local, put, run, abort

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
    """Distributes an archive to a web server.

    Args:
        archive_path (str): The path of the archive to distribute.
    Returns:
        If the file doesn't exist at archive_path or an error occurs - False.
        Otherwise - True.
    """
    if not os.path.isfile(archive_path):
        print(f"Archive path {archive_path} does not exist.")
        return False

    try:
        file = archive_path.split("/")[-1]
        name = file.split(".")[0]

        put(archive_path, "/tmp/{}".format(file))
        run("rm -rf /data/web_static/releases/{}/".format(name))
        run("mkdir -p /data/web_static/releases/{}/".format(name))
        run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(file, name))
        run("rm /tmp/{}".format(file))
        run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/".format(name, name))
        run("rm -rf /data/web_static/releases/{}/web_static".format(name))
        run("rm -rf /data/web_static/current")
        run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(name))
        print("New version deployed!")
        return True
    except Exception as e:
        print(f"Error deploying archive: {e}")
        return False


def deploy():
    """Create and distribute an archive to a web server."""
    file = do_pack()
    if file is None:
        print("Failed to create archive.")
        return False
    result = do_deploy(file)
    if not result:
        print("Failed to deploy archive.")
    return result
