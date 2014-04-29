'''
Created on Apr 22, 2014

@author: LuisGustavo
'''

from client.aiclient.Policy import DominionPolicy
from collections import Counter, defaultdict
import random

STATE = 0
ACTION = 1


class QLearning:
    def __init__(self, gamma=0.7, iterations = 1500, explorationRate=0.7):
        self.gamma = gamma
        self.iterations = iterations
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
        self.initialState = initialState.Clone()
        state = self.initialState
        for i in range(self.iterations):
            state.visits += 1
            action = self.expFn(state,state.GetMoves())
            nextState = state.generateSuccessor(action)
            maxQ = max([self.Q[(nextState,nextAction)] for nextAction in nextState.GetMoves()]) if nextState else 0
            self.Q[(state,action)] = (1-state.getAlpha())*self.Q[(state,action)] + (state.getAlpha())*((state.GetResult(state.playerJustMoved) or 0)+ self.gamma * maxQ)
            state = nextState if nextState else self.initialState
            
        print "Q estimatives computed"
            
    def getAction(self,state):
        return max([(action, self.Q[(state,action)]) for action in state.GetMoves()],key=lambda x: x[1])[0]
    
    def getActions(self):
        return [element[ACTION] for element in self.Q.keys()]
    
    def compute_policy(self):
        state = self.initialState
        self.policy = []
        while True:
            QActionsList = [(self.Q[key],key[ACTION]) for key in self.Q.keys() if key[STATE].isEqual(state)]
            bestAction = max(QActionsList,key=lambda x: x[0])[1]
            if not bestAction: break
            self.policy += [bestAction]
            nextState = state.generateSuccessor(bestAction)
            state = nextState 
            state.GetResult(state.playerJustMoved)
            if state.gameEnded: break;
        
        self.policy = DominionPolicy(Counter([action for action in self.policy if action]))
    
    def getPolicy(self):
        if not self.policy: self.compute_policy()
        return self.policy
#         print self.policy
#         print state.GetResult(state.playerJustMoved)
#         return DominionPolicy(Counter([action for action in self.policy if action]))
        
        
#         state = self.initialState
#         policy = []
#         while state.GetResult(state.playerJustMoved) == None:
#             action = self.getAction(state)
#             policy += [action]
# #             print (Counter([action.name for action in policy if action]).keys())
#             state = state.generateSuccessor(action)
#         return Counter([action.name for action in policy if action])

#         actionsIn = defaultdict(list)
#         any(actionsIn[state].append((q,action)) for ((state, action),q) in self.Q.items())
#         self.policy = [max(actionsIn[state], key=lambda element: element[0])[ACTION] for state in actionsIn.keys()]
#         return Counter([action for action in self.policy if action])