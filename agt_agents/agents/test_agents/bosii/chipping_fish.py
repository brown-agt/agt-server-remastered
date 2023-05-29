import argparse
import math
import random
from agents.base_agents.bosii_agent import BOSIIAgent
from agents.local_games.bosii_arena import BOSIIArena


class ChippingFish(BOSIIAgent):
    # You can ignore this test, it is just the agent that I implemented for the class competition moved from the trading platform to here
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]

    def get_action(self):
        discount = 1
        discount_rate = 0.01
        goodMoodC = 0.0
        goodMoodS = 0.0
        goodTotal = 0.0
        badMoodC = 0.0
        badMoodS = 0.0
        badTotal = 0.0
        probC = 0.0
        probS = 0.0

        mood_history = self.get_mood_history()
        action_history = self.get_action_history()
        util_history = self.get_util_history()
        for mood, action, util in zip(mood_history, action_history, util_history):
            if mood == self.GOOD_MOOD:
                goodTotal += discount
                if action == self.COMPROMISE:
                    goodMoodC += discount * util
                elif action == self.STUBBORN:
                    goodMoodS += discount * util
            elif mood == self.BAD_MOOD:
                badTotal += discount
                if action == self.COMPROMISE:
                    badMoodC += discount * util
                elif action == self.STUBBORN:
                    badMoodS += discount * util
            discount *= 1 - discount_rate

        if self.is_row_player():
            moodProb = self.col_player_good_mood_prob()
            if goodTotal > 0 and badTotal > 0:
                expectedC = (moodProb * (goodMoodC / goodTotal)) + \
                    ((1 - moodProb) * (badMoodC / badTotal))
                expectedS = (moodProb * (goodMoodC / goodTotal)) + \
                    ((1 - moodProb) * (badMoodC / badTotal))
                probC = math.exp(expectedC)
                probS = math.exp(expectedS)
        else:
            if self.get_mood() == self.GOOD_MOOD:
                if goodTotal > 0:
                    probC = math.exp(goodMoodC / goodTotal)
                if badTotal > 0:
                    probS = math.exp(badMoodC / badTotal)
            elif self.get_mood() == self.BAD_MOOD:
                if goodTotal > 0:
                    probC = math.exp(goodMoodS / goodTotal)
                if badTotal > 0:
                    probS = math.exp(badMoodS / badTotal)

        if random.random() < probC:
            return self.COMPROMISE
        else:
            return self.STUBBORN

    def update(self):
        return None


if __name__ == "__main__":
    ##### EDIT THIS #####
    ip = '192.168.1.16'
    port = 1234

    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--run_server', action='store_true',
                        help='Connects the agent to the server')

    args = parser.parse_args()

    agent = ChippingFish(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = BOSIIArena(players=[
            agent,
            ChippingFish("Agent_1"),
            ChippingFish("Agent_2"),
            ChippingFish("Agent_3"),
            ChippingFish("Agent_4")])
        arena.run()
