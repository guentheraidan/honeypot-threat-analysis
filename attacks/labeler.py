# Author: Lazaro Perez Jr.

# Records start/end time of each attack to labels.jsonl
import json
import os
import threading
import uuid
from datetime import datetime, timezone
LOG_PATH=os.environ.get("Labeler_log", "/labels/labels.jsonl")

class ContextManager:
	def __init__(self,filename,mode):
		self.filename=filename
		self.mode=mode
		self.file=None
	def __enter__(self):
		self.file=open(self.filename,self.mode)
		return self.file
	def __exit__(self,exc_type,exc_value,exc_traceback):
		self.file.close()
with ContextManager('labels.jsonl','w') as f:
	f.write(line+"\n")

#Need to figure out how I'm going to get a scenario number, run_id, etc, just stuff I can't calculate here.
