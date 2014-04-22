class TriggerInfo(object):
    
    def __init__(self, card, causer_player, causer_card, callback):
        self.causer_player = causer_player
        self.causer_card = causer_card
        self.callback = callback
        self.card = card
        
    def __call__(self, game, player):
        return self.callback(game, player, self.causer_player, self.causer_card)