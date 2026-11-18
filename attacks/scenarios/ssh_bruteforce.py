# Author: Lazaro Perez Jr.

# Scenario 1: Hydra SSH brute force on Cowrie
import subprocess
command=["hydra","-L","users.txt","-P","passwords.txt","-s","2222","-t","4","172.30.0.20","ssh"]
subprocess.run(command)
