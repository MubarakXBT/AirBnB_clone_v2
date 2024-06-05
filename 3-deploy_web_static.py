#!/usr/bin/python3
# Fabfile to create and distribute an archive to a web server.
import os.path
from datetime import datetime
from fabric.api import env, local, put, run

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
        print(f"Archive created successfully: {file}")
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

        print(f"Uploading {archive_path} to /tmp/{file} on remote servers...")
        if put(archive_path, "/tmp/{}".format(file)).failed:
            print(f"Failed to upload {archive_path}")
            return False

        print(f"Creating release directory /data/web_static/releases/{name}/ on remote servers...")
        if run("mkdir -p /data/web_static/releases/{}/".format(name)).failed:
            print(f"Failed to create release directory /data/web_static/releases/{name}/")
            return False

        print(f"Extracting /tmp/{file} to /data/web_static/releases/{name}/ on remote servers...")
        if run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(file, name)).failed:
            print(f"Failed to extract /tmp/{file}")
            return False

        print(f"Removing /tmp/{file} from remote servers...")
        if run("rm /tmp/{}".format(file)).failed:
            print(f"Failed to remove /tmp/{file}")
            return False

        print(f"Moving files from /data/web_static/releases/{name}/web_static to /data/web_static/releases/{name}/ on remote servers...")
        if run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/".format(name, name)).failed:
            print(f"Failed to move files to /data/web_static/releases/{name}/")
            return False

        print(f"Removing /data/web_static/releases/{name}/web_static from remote servers...")
        if run("rm -rf /data/web_static/releases/{}/web_static".format(name)).failed:
            print(f"Failed to remove /data/web_static/releases/{name}/web_static")
            return False

        print(f"Removing current symbolic link /data/web_static/current on remote servers...")
        if run("rm -rf /data/web_static/current").failed:
            print(f"Failed to remove current symbolic link")
            return False

        print(f"Creating new symbolic link /data/web_static/releases/{name}/ to /data/web_static/current on remote servers...")
        if run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(name)).failed:
            print(f"Failed to create new symbolic link")
            return False

        print("New version deployed successfully!")
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

