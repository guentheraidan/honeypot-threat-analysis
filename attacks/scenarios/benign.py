# Author: Lazaro Perez Jr.

# Scenario 4: Normal activity, should not be flagged
import subprocess
import paramiko
import time
output_file = 'paramiko.org'
def paramiko_B(command):
	hostname='172.30.0.20'
	print('running')
	try:
		port='2222'
		client=paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(hostname,port=2222, username='root',password='admin123',look_for_keys=False,allow_agent=False)
		channel=client.invoke_shell()
		channel.send(command+'\n')
		#(stdin,stdout,stderr)=client.exec_command(command)
		time.sleep(1)
		#cmd_output=stdout.read()
		cmd_output=channel.recv(4090).decode()
		print('log printing: ', command, cmd_output)
		with open(output_file,"w+") as file:
			file.write(str(cmd_output))
		return output_file
	finally:
		client.close()
def run():
	command=["curl","http://172.30.0.30"]
	subprocess.run(command)
	command=["hydra","-l","username","-p","incorrect","-s","2222","-t","1","172.30.0.20","ssh"]
	subprocess.run(command)
	time.sleep(1)
	paramiko_B("ls")
	time.sleep(1)
	paramiko_B("pwd")
	time.sleep(1)
	paramiko_B("exit")
run()
