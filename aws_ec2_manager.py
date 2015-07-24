import boto
from boto.ec2.connection import EC2Connection

import os
import subprocess

class Dict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    __setattr__ = dict.__setitem__

class AWSEC2Manager:
    def __init__(self, aws_key=None, aws_secret=None):
        self.ec2 = EC2Connection(aws_key, aws_secret)

    @property
    def tags(self):
        return self.ec2.get_all_tags()

    @property
    def reservations(self):
        return self.ec2.get_all_instances()

    @property
    def instances(self):
        active_instances = []
        
        for reservation in self.reservations:
            for instance in reservation.instances:
                i = Dict({
                    'tags'                  : [v for _, v in instance.tags.items()],
                    'public_dns_name'       : instance.public_dns_name,
                    'ip_address'            : instance.ip_address,
                    'type'                  : instance.instance_type,
                    'launch_time'           : instance.launch_time,
                    'private_ip_address'    : instance.private_ip_address,
                })

                active_instances.append(i)

        return active_instances

    def findPemInCurrentDir(self):
        for file in os.listdir(os.path.dirname(os.path.realpath(__file__))):
            if file.endswith(".pem"):
                return file

        return None

    def sshIntoInstance(self, instance_name, ssh_user = None, pem = None):
        for instance in self.instances:
            if instance_name in instance.tags:
                pem = pem or self.findPemInCurrentDir()

                if pem is None:
                    print("Error: Unable to find .pem AWS auth file in current directory")
                    exit(0)

                subprocess.call(['ssh', '-i', str(pem), '%s@%s' % (ssh_user or "ubuntu", str(instance.public_dns_name))])
