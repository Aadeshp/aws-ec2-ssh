# aws-ec2-ssh

### Handling AWS Keys Options
- Send in keys using --aws-key and --aws-secret
- Create ~/.aws/credentials file with the following contents:
```
[Credentials]
aws_access_key_id = [AWS ACCESS KEY ID HERE]
aws_secret_access_key = [AWS SECRET ACCESS KEY HERE]
```
- Add environmental variables called AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY


### Retrieving All Active Instances
```bash
$ aws-ec2-ssh --active
```

Output:
```
Tags    Public DNS Name                             IP Address        Type          Launch Time
-------------------------------------------------------------------------------------------------------------
ec1     ec2-XX-X-XXX-XXX.compute-1.amazonaws.com    XX-X-XXX-XXX      m3.medium     2015-05-27T15:31:50.000Z 
```

### SSH Into An Instance
- The following will only work if your .pem AWS authentication file is in the same directory as the script
```bash
$ aws-ec2-ssh --ssh ec1
```
- If your .pem AWS authentication file is in another directory
```bash
$ aws-ec2-ssh --ssh ec1 --pem /Path/To/Pem/File
```
- If you don't have your AWS keys saved on your machine:
```bash
$ aws-ec2-ssh --ssh ec1 --aws-key [AWS ACCESS KEY ID HERE] --aws-secret [AWS SECRET ACCESS KEY HERE]
```
- If you don't want to SSH as ubuntu
```bash
$ aws-ec2-ssh --ssh ec1 --ssh-user ubuntu
```

