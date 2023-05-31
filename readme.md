# **CS1440 AGT Server**

## **Getting Started**
### **Installation** 
Ensure that you have the latest version of pip installed <br> <br>
First clone the respositiory 
```
git clone https://github.com/JohnUUU/agt-server-remastered.git
```
In the root directory, install the project in an editable state
```
pip install -e .
```
Make sure to run the agents from the root directory


## **Frequently Asked Questions (General)**
- What do each of the options in the configuration do? 
    - The RPS configuration only supports <br>
    [`all`, `my_action`, `opp_action`,  `my_utils`, `opp_utils`] <br> 
    <br>
    If you wish to change or add more permissions please edit the corresponding game under `server/games` and the corresponding agent under `agents\base_agents`

- I cant run rps_test.sh or any of the other .sh test files
    - Unfortunately this is currently only supports Mac's `terminal.app`. If you are using the Mac terminal then make sure to `chmod +x` the shell command before running it. 
    - You may also need to change the IP address of each agent to be the ip address of your computers hostname as well. 


## **Frequently Asked Questions (Mac)**
- I am recieving an error concerning my hostname
    - Please find your ip address using `ifconfig` under `en0` or `eth0`. Find your hostname using `echo $HOST` and then set the host in `\etc\hosts`. That usually fixes the problem 

