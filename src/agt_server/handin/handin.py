import os
import pkg_resources
import importlib.util
import sys
import json
from datetime import datetime
import argparse

def import_agent_submission_from_path(path):
    directory = os.path.dirname(path)
    
    original_sys_path = sys.path.copy()
    if directory not in sys.path:
        sys.path.insert(0, directory)
    
    try:
        spec = importlib.util.spec_from_file_location("my_agent_module", path)
        my_agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(my_agent)
        return my_agent.agent_submission
    finally:
        sys.path = original_sys_path

def get_agent_submissions(directory):
    print(directory)
    agent_submissions = []
    folder_mod_times = {}
    for root, _, files in os.walk(directory):
        print(files)
        root_mod_time = os.path.getmtime(root)
        if root not in folder_mod_times or root_mod_time > folder_mod_times[root]:
            folder_mod_times[root] = root_mod_time
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_mod_time = os.path.getmtime(file_path)
                if file_mod_time > folder_mod_times[root]:
                    folder_mod_times[root] = file_mod_time
            except Exception as e:
                print(f"Failed to get modification time for {file_path}: {e}", file=sys.stderr)
        
        for file in files:
            if file == 'my_agent.py':
                full_path = os.path.join(root, file)
                try:
                    agent_submission = import_agent_submission_from_path(full_path)
                    agent_submission.timestamp = folder_mod_times[root]
                    agent_submissions.append(agent_submission)
                except Exception as e:
                    print(f"Failed to import {full_path}: {e}", file=sys.stderr)
    print(f"{len(agent_submissions)} sucessfully imported")
    return agent_submissions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Handin Script')
    parser.add_argument('handin_config', type=str, help='The name of the handin_config file that you want to use')
    parser.add_argument('agent_submissions', type=str, help='The path to the directory that you want to run the handin-script on (Relative to agt_server)')
    args = parser.parse_args()
    full_config = f"configs/handin_configs/{args.handin_config}"
    
    config_path = pkg_resources.resource_filename('agt_server', full_config)
    with open(config_path) as cfile:
        server_config = json.load(cfile)
    
    agent_submissions = get_agent_submissions(pkg_resources.resource_filename('agt_server', args.agent_submissions))
    print(agent_submissions)
    
    directory = os.path.dirname(pkg_resources.resource_filename('agt_server', server_config['arena_path']))
    spec = importlib.util.spec_from_file_location("module.name", pkg_resources.resource_filename('agt_server', server_config['arena_path']))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    start = datetime.now()
    print([agent.name for agent in agent_submissions if agent is not None])
    arena_type = getattr(module, server_config['arena_classname'])
    arena = arena_type(
            num_rounds = server_config['num_rounds'],
            timeout = server_config['response_time'],
            players = [agent for agent in agent_submissions if agent is not None],
            handin = True, 
            logging_path = server_config['logging_path'], 
            summary_path = server_config['save_path']
    )
    arena.run()
    end = datetime.now()
    print(f"Time Elapsed (s): {(end - start).total_seconds()}")
    
    