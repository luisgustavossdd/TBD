'''
Created on Apr 22, 2014

@author: LuisGustavo
'''

from collections import Counter, defaultdict
import random

STATE = 0
ACTION = 1


class QLearning:
    def __init__(self, gamma=0.7, iterations = 5000, explorationRate=0.7):
        self.gamma = 0.7
        self.iterations = 5000
        self.explorationRate = explorationRate
        self.Q = Counter()
        self.cards = Counter()
        self.policy = None
    
    def expFn(self,state,actions):
        result = None
        if random.random() < self.explorationRate: result = random.sample(actions,1)[0]
        else: 
            Qs = []
            any(Qs.append((action,self.Q[(state,action)])) for action in actions)
            result = max(Qs, key=lambda element: element[1])[0]
            
        if result: self.cards[result.name] += 1
        else:      self.cards["None"] += 1
        return result
            
    def learn(self, initialState):
        self.initialState = initialState
        state = initialState.Clone()
        for i in range(self.iterations):
            state.visits += 1
            action = self.expFn(state,state.GetMoves())
            nextState = state.generateSuccessor(action)
            maxQ = max([self.Q[(nextState,nextAction)] for nextAction in nextState.GetMoves()])
            self.Q[(state,action)] = (1-state.getAlpha())*self.Q[(state,action)] + (state.getAlpha())*((state.GetResult(state.playerJustMoved) or 0)+ self.gamma * maxQ)
            state = nextState
            
    def getAction(self,state):
        return max([(action, self.Q[(state,action)]) for action in state.GetMoves()],key=lambda x: x[1])[0]
    
    def getActions(self):
        return [element[ACTION] for element in self.Q.keys()]
    
    def getPolicy(self):
        
#         state = self.initialState
#         policy = []
#         while state.GetResult(state.playerJustMoved) == None:
#             action = self.getAction(state)
#             policy += [action]
# #             print (Counter([action.name for action in policy if action]).keys())
#             state = state.generateSuccessor(action)
#         return Counter([action.name for action in policy if action])
        
        actionsIn = defaultdict(list)
        any(actionsIn[state].append((q,action)) for ((state, action),q) in self.Q.items())
        self.policy = [max(actionsIn[state], key=lambda element: element[0])[ACTION] for state in actionsIn.keys()]
        return Counter([action for action in self.policy if action])
        