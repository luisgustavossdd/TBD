import abc


class GameInterface(object):
    """The interface for the cards to interact with the game
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def take_card_from_pile(self, player, pile, safe=False, to_hand=False, to_deck=False, message=None):
        """Let the player pick a card from a pile

        :param player: the player that should take a card
        :type player: Player
        :param pile: the pile the player should take the card from
        :type pile: Pile
        :param safe: ignore empty piles if True
        :type safe: bool
        :param to_hand: the card should go to hand instead of discard pile
        :type to_hand: bool
        :param to_deck: the card should go on top of the deck instead of discard pile
        :type to_deck: bool
        :param message: message to display instead of '<playername> took <cardname>'
        :param message: str
        :returns: the top card from the pile
        :rtype: Card
        """

    @abc.abstractmethod
    def whisper(self, message, player=None):
        """Send a message a player

        :param message: the message the player should receive
        :type message: str
        :param player: the player that should receive the message instead of the active player
        :type player: Player
        """

    @abc.abstractmethod
    def yell(self, message):
        """Send a message to all players

        :param message: the message the players should receive
        :type message: str
        """

    @abc.abstractmethod
    def update_player(self, player=None):
        """Tell player(s) the game state was updated

        :param player: The player which should receive the update instead of all players
        :type player: Player
        """

    @abc.abstractmethod
    def trash_card(self, player, card, silent=False):
        """Let the player trash a card from his hand

        :param player: The player which should receive the update instead of all players
        :type player: Player
        :param card: The card that should be trashed
        :type card: Card
        :param silent: If True, the trashing is not announced
        :type silent: bool
        """

    @abc.abstractmethod
    def take_card(self, player, card, message=None, to_hand=False, to_deck=False):
        """Let the player take the card

        :param player: the player that should take a card
        :type player: Player
        :param card: The card that should be taken by the player
        :type card: Card
        :param message: the message the players should receive
        :type message: str
        :param to_hand: the card should go to hand instead of discard pile
        :type to_hand: bool
        :param to_deck: the card should go on top of the deck instead of discard pile
        :type to_deck: bool
        :returns: the card
        :rtype: Card
        """

    @abc.abstractmethod
    def reveal_top_card(self, player=None):
        """
        :param player: the player that should reveal his top card instead of the active player
        :type player: Player
        """

    @abc.abstractmethod
    def reveal_player_hand(self, player=None):
        """
        :param player: the player that should reveal his hand instead of the active player
        :type player: Player
        """

    @abc.abstractmethod
    def on_resolve(self, card, f):
        """Register a callback function that is called when a card tells it is resolved

        :param card: the card that triggers the callback function
        :type card: Card
        :param f: the callback function that should be called when the card resolves
        :type f: function
        """

    @abc.abstractmethod
    def resolved(self, card):
        """Called by cards to tell the game they are resolved

        :param card: the card that is resolved
        :type card: Card
        """

    @abc.abstractmethod
    def previous_player(self):
        """Return the previous player before the actual one

        :returns: the player before the active player
        :rtype: Player"""

    @abc.abstractmethod
    def next_player(self, current=None):
        """Return the next player after the actual or given one

        :param current: the player of which the next player is returned
        :type current: Player
        :returns: the player after 'current'
        :rtype: Player
        """

    @abc.abstractmethod
    def play_card(self, player, card_id, free=False, is_duration=False, update=True):
        """Let the player play a card

        :param player: the player that plays the card
        :type player: Player
        :param card_id: the card of the card played
        :type card_id: int
        :param free: if True, playing this card don't cost an action
        :type free: bool
        :param is_duration: has to be set to True if the card is played during resolving a duration-action at the begin
        of a turn
        :type is_duration: bool
        """

    @abc.abstractmethod
    def let_all_players_pick(self, card, text, handler=None, player_filter=None):
        """Let all players pick a card from their hand

        :param card: the card that triggers this action
        :type card: Card
        :param text: the message that all players get displayed
        :type text: str
        :param handler: the callback function that is invoked when each player chooses his card
        :type handler: function
        :param player_filter: a function that takes a player and decides if this player should pick a card
        :type player_filter: function
        """

    @abc.abstractmethod
    def let_order_cards(self, card, text, cards, callback):
        """
        Let the player order a bunch of cards

        :param card: the card that triggers this action
        :type card: Card
        :param text: the message that will be displayed to the player
        :type text: str
        :param cards: the cards the player should order
        :type cards: list
        :param callback: the callback function that is invoked after the player ordered the cards
        :type callback: function
        """

    @abc.abstractmethod
    def let_pick_from_hand(self, card, text, callback=None):
        """
        Let the player pick some cards from his hand

        Example: Haven lets the player pick a card from his hand to put this beneath itself

        :param card: the card that triggers this action
        :type card: Card
        :param text: the message that will be displayed to the player
        :type text: str
        :param callback: the callback function that is invoked after the player picked the cards
        :type callback: function
        """

    @abc.abstractmethod
    def let_pick_pile(self, card, text, callback=None):
        """
        Let the player pick a pile of cards from the board

        Example: Feast lets the player pick a pile of cards and checks if the cost of the cards is up to 5

        :param card: the card that triggers this action
        :type card: Card
        :param text: the message that will be displayed to the player
        :type text: str
        :param callback: the callback function that is invoked after the player picked a pile
        :type callback: function
        """

    @abc.abstractmethod
    def add_action_step_handler(self, card_class, callback):
        """Register a callback function that is invoked if a specific card is played in the action step.

        Example: The Coppersmith registers a function that adds 1 to the players coins whenever a Copper is played.

        All callbacks are cleared when the player finishes his turn.

        :param card_class: the class of the card that triggers the callback function
        :type card_class: Class
        :param callback: the callback function invoked when a card of the given class is player in the action step
        :type callback: function
        """
    
    @abc.abstractmethod
    def add_buy_step_handler(self, card_class, callback):
        """Register a callback function that is invoked if a specific card is played in the buy step

        Example: The Coppersmith registers a function that adds 1 to the players coins whenever a Copper is played.

        All callbacks are cleared when the player finishes his turn.

        :param card_class: the class of the card that triggers the callback function
        :type card_class: Class
        :param callback: the callback function invoked when a card of the given class is player in the buy step
        :type callback: function
        """

    @abc.abstractmethod
    def add_cost_mod(self, mod):
        """Register a function that is invoked when the cost of a card is calculated

        Example: The Brigde registers a function that subtracts 1 coin of the cost of each card.

        :param mod: a function taking the parameters 'coins' and 'potions' and returning a tuple of (coins, potions)
        :type mod: function
        """
    
    @abc.abstractmethod
    def allpiles(self):
        """Get all piles (kingdom cards and common cards)

        :returns: a list of all piles of kingdom and common cards
        :rtype: list
        """

    @abc.abstractmethod
    def ask(self, card, text, answers, callback=None, on_restore_callback=None):
        """Ask the active player to pick an answer to the given question

        Example: The Minion asks the player to either get money or to discard/draw cards

        :param card: the card that triggers this action
        :type card: Card
        :param text: the text displayed to/question asked the player
        :type text: str
        :param answers: the possible answers to the question
        :type answers: tuple
        :param callback: the callback function invoked when the player picked his answer
        :type callback: function
        :param on_restore_callback: the callback function invoked when the sub-phase is restored
        :type on_restore_callback: function
        """
    
    @abc.abstractmethod
    def ask_all_players(self, card, askplayerinfo, handler=None, player_filter=None):
        """

        """
    
    @abc.abstractmethod
    def ask_yes_no(self, card, text, callback=None, on_restore_callback=None, card_to_show=None):
        """

        """
    
    @abc.abstractmethod
    def attack(self, card, attack_handler=None, subphase=None, info=None,
               expect_answer=True, on_restore_callback=None, keep_WAIT=False):
        """

        """
    
    @abc.abstractmethod
    def attack_ask(self, card, info, attack_handler=None,
               expect_answer=True, on_restore_callback=None):
        """

        """
    
    @abc.abstractmethod
    def attack_let_pick_from_hand(self, card, text, attack_handler=None,
               expect_answer=True, on_restore_callback=None):
        """

        """
    
    @abc.abstractmethod
    def discard_card(self, player, card):
        """

        """
    
    @abc.abstractmethod
    def discard_cards(self, cards, player=None):
        """

        """
    
    @abc.abstractmethod
    def discard_hand(self, player):
        """

        """
    
    @abc.abstractmethod
    def draw_card(self, player=None, count=1):
        """

        """
    
    @abc.abstractmethod
    def enter_subphase(self, subphaseinfo):
        """
        
        """
    
    @abc.abstractmethod
    def get_cost(self, pile_or_card):
        """

        """
    
    @abc.abstractmethod
    def get_pile(self, cardtype):
        """

        """
    
    @abc.abstractmethod
    def get_player_by_id(self, player_id):
        """

        """

    @abc.abstractmethod
    def has_played(self, card_class):
        """

        """
