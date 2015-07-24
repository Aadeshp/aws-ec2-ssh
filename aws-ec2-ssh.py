#!/usr/bin/env python3

import argparse
from aws_ec2_manager import AWSEC2Manager

import sys
import os
import itertools
import threading
import time

from functools import wraps

def progress_bar(message, event):
    chars = itertools.cycle(r'-\|/')

    while not event.is_set():
        sys.stdout.write('\r%s ' % str(message)  + next(chars))
        sys.stdout.flush()
        event.wait(0.2)

    if event.is_set():
        sys.stdout.write('\r')
        sys.stdout.flush()

"""
Decorator that runs a method with a progress bar thread
"""
def run_with_progress_bar(message):
    def run_with_progress_bar_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            event = threading.Event()
            progress_bar_thread = threading.Thread(target = progress_bar, args = (str(message), event,))

            progress_bar_thread.start()
            func(*args, **kwargs)
            event.set()
            progress_bar_thread.join()

        return func_wrapper

    return run_with_progress_bar_decorator

"""
Establishes global EC2 connection
"""
def connectToEC2(aws_key=None, aws_secret=None):
    global _ec2
    _ec2 = AWSEC2Manager(aws_key, aws_secret)


"""
Retrieves AWS Access and Secret Key from either input params or environmental variables
"""
def getAWSKeys(namespace):
    aws_key = None
    aws_secret = None

    if namespace.aws_key:
        aws_key = namespace.aws_key[0]

    if namespace.aws_secret:    
        aws_secret = namespace.aws_secret[0]

    if aws_key is None:
        aws_key = os.environ.get('AWS_ACCESS_KEY_ID')

    if aws_secret is None:
        aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

    return { 'aws_key': aws_key, 'aws_secret': aws_secret }

"""
SSH Into Specified Instance Specifications
"""
def sshIntoInstance(args):
    keys = getAWSKeys(args)
    connectToEC2(keys['aws_key'], keys['aws_secret'])

    ssh_dest = None if args.ssh is None else args.ssh[0]
    ssh_user = None if args.ssh_user is None else args.ssh_user[0]
    aws_pem = None if args.pem is None else args.pem[0]

    _ec2.sshIntoInstance(ssh_dest, ssh_user, aws_pem)

"""
ArgParse
"""
class DisplayAllActiveInstances(argparse.Action):
    @run_with_progress_bar("Retrieving")
    def __call__(self, parser, namespace, values, option_string = None):
        instances = self.getActiveInstances(namespace)
        self.displayActiveInstances(instances)
    
    def getActiveInstances(self, namespace):
        keys = getAWSKeys(namespace)
        connectToEC2(keys['aws_key'], keys['aws_secret'])
        instances = _ec2.instances

        return instances

    def displayActiveInstances(self, instances):
        sys.stdout.write("\r%-40s %-50s %-20s %-15s %-20s\n" % ("Tags", "Public DNS Name", "IP Address", "Type", "Launch Time"))
        sys.stdout.write("-" * 155)
        sys.stdout.write('\n')

        for instance in instances:
            sys.stdout.write("%-40s %-50s %-20s %-15s %-30s\n" % (", ".join(instance.tags), instance.public_dns_name, instance.ip_address, instance.type, instance.launch_time))

        sys.stdout.flush()

def initArgParse():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--aws-key",
        nargs = 1,
        action = "store",
        dest = "aws_key",
        help = "Set AWS Access Key"
    )

    parser.add_argument(
        "--aws-secret",
        nargs = 1,
        action = "store",
        dest = "aws_secret",
        help = "Set AWS Secret Key"
    )

    parser.add_argument(
        "--active",
        nargs = 0,
        action = DisplayAllActiveInstances,
        help = "Get Active Instances"
    )

    parser.add_argument(
        "--ssh",
        nargs = 1,
        action = "store",
        dest = "ssh",
        help = "SSH Into One of the Active Instances"
    )

    parser.add_argument(
        "--ssh-user",
        nargs = 1,
        action = "store",
        dest = "ssh_user",
        help = "User to SSH into Instance With"
    )

    parser.add_argument(
        "--pem",
        nargs = 1,
        action = "store",
        dest = "pem",
        help = "Path To Your AWS Pem Auth File"
    )

    return parser.parse_args()

def main():
    args = initArgParse()
    
    if args.ssh is not None:
        sshIntoInstance(args)

if __name__ == "__main__":
    main()
