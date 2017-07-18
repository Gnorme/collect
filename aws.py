import boto3
import paramiko
from datetime import datetime, timedelta

def GetBalance():
	cloudwatch = boto3.client('cloudwatch',aws_access_key_id='AKIAIU22OCRGXFDS2ONA',aws_secret_access_key='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', region_name='us-east-2')
	Namespace = 'AWS/EC2'
	MetricName = 'CPUCreditBalance'
	Statistics=['Average']
	StartTime = datetime.utcnow() - timedelta(seconds=300)
	EndTime = datetime.utcnow()
	Period = 300
	Unit = 'Count'
	Dimensions = [{'Name':'InstanceId','Value':'i-06f5e220cb05c65ef'}]
	metrics = cloudwatch.get_metric_statistics(Namespace=Namespace, MetricName=MetricName,Dimensions=Dimensions, StartTime=StartTime,EndTime=EndTime,Statistics=Statistics,Period=Period,Unit=Unit)
	print(metrics['Datapoints'][0]['Average'])

def CreateInstance():
	ec2 = boto3.resource('ec2')
	instance = ec2.create_instances(
		ImageId='ami-828aabe7',
		KeyName='first',
		MinCount=1,
		MaxCount=1,
		InstanceType='t2.micro')
	return instance[0]

def SSHConnect():
	k = paramiko.RSAKey.from_private_key_file("first.pem")
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print("Connecting")
	ssh.connect(hostname = "ec2-13-58-176-246.us-east-2.compute.amazonaws.com", username = "ubuntu", pkey = k )
	return ssh

def DownloadTextFiles():
	ssh = SSHConnect()
	sftp = ssh.open_sftp()
	file_list = sftp.listdir(path='/home/ubuntu/data')
	for item in file_list:
		localpath = 'files/' + item
		remotepath = '/home/ubuntu/data/' + item
		sftp.get(remotepath,localpath)
	sftp.close()
	ssh.close()

def DownloadPdfFiles():
	ssh = SSHConnect()
	sftp = ssh.open_sftp()
	file_list = sftp.listdir(path='/home/ubuntu/Downloads')
	for item in file_list:
		localpath = 'data/' + item
		remotepath = '/home/ubuntu/Downloads/' + item
		sftp.get(remotepath,localpath)
	sftp.close()
	ssh.close()

DownloadTextFiles()
#cloudwatch.get_dashboard(DashboardName='string')
#ec2 = boto3.resource('ec2')
#ec2.create_instances(ImageId='ami-828aabe7')

#check credits
#if < 1, transfer files
#stop instance
#start new instance
