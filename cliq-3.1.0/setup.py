import sys

from setuptools import setup

from consts import VERSION, DESC, APP_NAME


def forbid_publish():
    argv = sys.argv
    blacklist = ["register", "upload"]

    for command in blacklist:
        if command in argv:
            values = {"command": command}
            print('Command "%(command)s" has been blacklisted, exiting...' % values)
            sys.exit(2)


forbid_publish()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name=APP_NAME,
    version=VERSION,
    description=DESC,
    license="Apache License Version 2",
    url="http://www.burstiq.com",
    download_url="",
    entry_points={
        "console_scripts": ["cliq = cliq:main", "cliq_sudo = cliq_sudo:main"]
    },
    python_requires=">=3.13.0",
    install_requires=required,
    packages=[".", "actions", "actions_sudo", "graphchain_client", "jpath"],
    package_data={"data": ["data"]},
)
