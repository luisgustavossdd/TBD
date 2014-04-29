'''
Created on Apr 28, 2014

@author: LuisGustavo
'''
        
class DominionPolicy:
    def __init__(self, cardsToBuy):
        self.cardsToBuy = cardsToBuy

    def cards(self):
        return sorted([card for (card,amount) in self.cardsToBuy.items() if amount],key=lambda card: card.cost, reverse=True)

    def pop(self, card):
        if not self.cardsToBuy.has_key(card): return None
        return self.cardsToBuy.pop(card)
