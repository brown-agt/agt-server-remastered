import os
import importlib
import time
import pandas as pd
import json
import argparse
import sys
if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser(description='My Handin')
    parser.add_argument('handin_config', type=str,
                        help='Relative Path of the handin config file starting from config/handin_configs')
    args = parser.parse_args()

    config_file = f"../../configs/handin_configs/{args.handin_config}"
    cfile = open(config_file)
    server_config = json.load(cfile)

    directory = server_config['agents_dir']
    arena_path = server_config['arena_path']
    arena_classname = server_config['arena_classname']
    result_path = server_config['save_path']
    num_rounds = server_config['num_rounds']
    timeout = server_config['response_time']

    timestamp = time.strftime("%Y-%m-%d_%H%M")
    agents = []
    for submission_name in os.listdir(directory):
        submission_path = os.path.join(directory, submission_name)
        if os.path.isdir(submission_path) and not submission_name.startswith(".") \
           and not (len(submission_name) >= 4 and submission_name[:2] == "__" and submission_name[-2:] == "__"):
            submission = os.path.join(submission_path, "my_agent.py")
            sys.path.insert(0, submission_path)
            spec = importlib.util.spec_from_file_location(
                "my_agent", submission)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.path.remove(submission_path)

            if hasattr(module, "agent_submission") and module.agent_submission != None:
                agents.append(module.agent_submission)

    spec = importlib.util.spec_from_file_location(
        "arena", arena_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, arena_classname) and getattr(module, arena_classname) != None:
        HandinArena = getattr(module, arena_classname)
        arena = HandinArena(
            num_rounds=num_rounds,
            timeout=timeout,
            players=agents,
            handin=True
        )
        results = arena.run()
        print(results)
        if result_path:
            agent_list = [str(x) for x in results['Final Score'].reset_index(
            ).values.flatten().tolist() if pd.notnull(x)]
            agent_res = " ".join(agent_list)
            result_str = f"{timestamp} {agent_res}\n"
            with open(result_path, "a") as file:
                file.write(result_str)
    end = time.time()
    print(f"{end - start} Seconds Taken")
