#!/usr/bin/env python3

import argparse
from aws_ec2_manager import AWSEC2Manager

import sys
import os

def connectToEC2(aws_key=None, aws_secret=None):
    global _ec2
    _ec2 = AWSEC2Manager(aws_key, aws_secret)

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

def sshIntoInstance(args):
    keys = getAWSKeys(args)
    connectToEC2(keys['aws_key'], keys['aws_secret'])

    ssh_dest = None if args.ssh is None else args.ssh[0]
    ssh_user = None if args.ssh_user is None else args.ssh_user[0]
    aws_pem = None if args.pem is None else args.pem[0]

    _ec2.sshIntoInstance(ssh_dest, ssh_user, aws_pem)

class DisplayAllActiveInstances(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        keys = getAWSKeys(namespace)
        connectToEC2(keys['aws_key'], keys['aws_secret'])

        print("%-40s %-50s %-20s %-15s %-20s" % ("Tags", "Public DNS Name", "IP Address", "Type", "Launch Time"))
        print("-" * 155)

        for instance in _ec2.instances:
            print("%-40s %-50s %-20s %-15s %-30s" % (", ".join(instance.tags), instance.public_dns_name, instance.ip_address, instance.type, instance.launch_time))

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
