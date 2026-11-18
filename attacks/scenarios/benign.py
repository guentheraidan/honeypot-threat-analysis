# Author: Lazaro Perez Jr.

# Scenario 4: Normal activity, should not be flagged
import subprocess
import paramiko
output_file = 'paramiko.org'
def paramiko_B(command):
	hostname='172.30.0.20'
	print('running')
	try:
		port='22'
		client=paramiko.SSHClient()
		client.load_system_host_keys()
		client.connect(hostname,port=22, username='root',password='admin123')
		(stdin,stdout,stderr)=client.exec_command(command)
		cmd_output=stdout.read()
		print('log printing: ', command, cmd_output)
		with open(output_file,"w+") as file:
			file.write(str(cmd_output))
		return output_file
	finally:
		client.close()


command=["curl","http://172.30.0.30"]
subprocess.run(command)
command=["hydra","-1","username","-p","incorrect","2222","-t","1","172.30.0.20","ssh"]
paramiko_B(ls)
paramiko_B(pwd)

