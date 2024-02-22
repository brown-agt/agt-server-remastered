# **CS1440 AGT Server**
## **Introduction**
The **AGT Server** is a python platform designed to run and implement game environments that autonomous agents can connect to and compete in. Presently the server only supports 
- Complete Information and Incomplete Information Matrix Games (e.g. Rock-Paper-Scissors, BotS, etc...)

However, at its core the server is also designed to be flexible so that new game environments can be easily created, modified, and adjusted.

## **Getting Started**
### **Installation** 
Ensure that you have the latest version of pip installed <br> <br>
First clone the respositiory 
```
git clone https://github.com/JohnUUU/agt-server-remastered.git
```
Please create a virtual environment first 
```
python3 -m venv .venv
source .venv/bin/activate
```
#### **For Users**
```bash 
pip install --upgrade pip
pip install agt_server
```
#### **For Developers**
In the root directory, install the project in an editable state
```bash
pip install --upgrade pip
pip install -e .
pip install -r requirements.txt 

```
### **Usage**
From here you can start a server in `src/server` by running 
```
python server.py [server_config_file] [--ip [ip_address]] [--port [port]]
```
Then you can run any of the example agents in `src/agt_agents/test_agents` by running 
```
Usage: 
python [agent_file].py [name] [--join_server] [--ip [ip_address]] [--port [port]]
```
Or you can write a agent file that implements any of the `src/agt_agents/base_agents` and then use 
```
agent.connect(ip, port)
```


## **Frequently Asked Questions**
- What do each of the options in the server configurations do? 
Here is a quick description of each of the server configuration options.
    - `game_name`: The name of the game being played 
    - `game_path`: The Python import path for the game module 
    - `num_rounds`: The number of rounds to be played in the game 
    - `signup_time`: The duration (in seconds) allowed for players to sign up before a game starts (60 seconds tends to work best for Lab) 
    - `response_time`: The maximum time (in seconds) allowed for each player to respond with their move
    - `num_players_per_game`: The number of players required in each game
    - `player_types`: The list of available player types in the game. This can be used to specify different permissions for each player and also can be used flexibly to change the rules for different players inside the game_path file. 
    - `permissions`: This is a dictionary of permissions for each player type restricting the amount of information that each player will recieve at the end of each round. `all` means that the player will recieve all information. All other key words correspond to specific information sent each round like `my_action`, `opp_action`,  `my_utils`, `opp_utils`, etc... <br>
    If you wish to change or add more permissions please edit the corresponding game under `server/games` and the corresponding agent under `agents/base_agents`
    - `type_configurations`: The configuration for player type combinations, if it's `all`, then every combination of player types will be played for each game. Otherwise, it can be specified to be a list like [[`type1`, `type2`], [`type1`, `type1`]] for example so that player 1 will always be type 1 and play against player 2 as both type 1 and type 2. 
    - `invalid_move_penalty`: The penalty for submitting an invalid move
    - `display_results`: Flag indicating whether to display/print the game results
    - `save_results`: Flag indicating whether to save the game results
    - `save_path`: If `save_results` is set to true, then this is the path where the game results should be saved
    - `send_results`:  Flag indicating whether to send the game results to the agents
    - `check_dev_id`:  Flag indicating whether to check the device ID so that each device can only connect once. This is to stop collusion bots. 

- What purpose do the local arenas serve? 
    - The local arenas allow you to run the games locally and allow the user to be able to catch exceptions and invalid moves ahead of time, as well as test out their agent. 
    <!---
    [TODO]: If you do add handin mode make sure to add a blurb about it here
    - Add a note about how in handin mode if you timeout 10 times in a row then you will be disqualified due to the increased number of rounds played and how a single delay agent could cause it to take upwards of 3+ hours
    --->

<!---
    [TODO]: If you do add handin mode make sure to add the handin config information here
--->
- I cant run rps_test.sh or any of the other .sh test files
    - Unfortunately this is currently only supports Mac's `terminal.app`. If you are using the Mac terminal then make sure to `chmod +x` the shell command before running it. 
    - You may also need to change the IP address of each agent to be the ip address of your computers hostname as well. 

- I am recieving an error concerning my hostname
    - Please find your ip address using `ifconfig` (Mac) or `ipconfig` (Windows) under `en0` or `eth0`. Find your hostname using `echo $HOST` and then set the host in `\etc\hosts`. That usually fixes the problem. 
    - Alternatively if that doesn't work you can just supply the ip address that you found to server.py when you run it using the optional `--ip` arguement. 
    - This is mostly a bandaid solution by overriding the hostname locally and you'll have to do it everytime the ISP switches, if anyone has more experience with DNS resolution and wants to help please reach out!

- What if the server hangs for some unexpected reason? 
    - These things can be hard to debug but the backup solution is that the server code will catch any interrupts (^C) commands 
    that you give it and return the currently compiled results to the best of its ability so that the agents will know who was winning at that point. 
