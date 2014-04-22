#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame

from client.aiclient.botthread import BotThread
from client import deckprovider
from phases import ActionHandler, BuyHandler, PhaseHandler, PickCardHandler, \
                         PickCardsFromHandHandler, AskPlayerHandler, OrderCardsHandler
from client.pygameclient.widgets import gui
from framework.event import PlayerInfoEvent, SetMasterEvent, RequestStartGame, MessageEvent, EndGameEvent, ResetEvent,\
    QuitEvent, TickEvent, RequestConnectEvent
from framework.pygame.scrollablesurface import ScrollableSurface
from game import cardprovider
from game.rules import commonpiles
from game.gamestates import P_ACTION, P_BUY, P_CLEANUP, P_PRECLEANUP, SP_WAIT,\
    SP_PICKCARD, SP_PICKCARDSFROMHAND, SP_ORDERCARDS, SP_ASKPLAYER,\
    SP_PLAYERINPUT
from client.pygameclient.settings import SCREEN_WIDTH, PREV_HEIGHT, PREV_WIDTH
import logging
from framework.networking import find_server
from server.serverthread import ServerThread, UDPServerThread
import time


class Scene(object):

    """Drawing GUI and handle scene specific events for a different game-states, like menu or lobby etc."""

    def enter(self):
        """Called when entering this phase"""

        pass

    def notify(self, event):
        """Called when an event occurs"""

        pass

    def leave(self):
        """Called when leaving this phase"""

        pass

    def draw(self, surface):
        """Draw something on the given surface"""

        pass

    def handle_event(self, event):
        """Handles the given event"""

        pass

    def update(self):
        """Called via the game loop"""

        pass
    
    def enterphase(self):
        pass

class CardInfo(object):

    def __init__(self, card_class, res):
        self.card_class = card_class
        self.name = card_class.name
        self.image = res.get(card_class.name.lower(), 'prev')
        self.loc = (0, 0)

class EditorScene(Scene):

    def enter(self):
        self.cards = [CardInfo(c, self.client.res) for c in cardprovider.get_all_card_classes()
                      if c not in commonpiles]
        self.cards.sort(key=lambda c: c.name)
        self.selected = []

        self.cards_draw_offset = 0
        self.selected_draw_offset = 0

        app = self.client.app
        x = 15

        gui.Label((x, 50), (180, 0), app, text="Decks")

        self.decklist = gui.ListBox((x, 75), (180, 400), app)
        self.decklist.onItemSelected = self.__handle_decklist_select

        gui.Label((x, 500), (0, 0), app, text="Deck Name:")
        self.txtName = gui.TextBox((x, 525), (180, 0), app)

        btnSave = gui.Button((x, 560), (180, 0), app, text="Save")
        btnSave.onClick = self.__handle_save_click

        btnBack = gui.Button((x, 585), (180, 0), app, text="Back")
        btnBack.onClick = self.__handle_back_click

        self.ss_selected = ScrollableSurface((SCREEN_WIDTH - 30,
                PREV_HEIGHT + 10), (15, 615))

        surface_width = 6 * (5 + PREV_WIDTH) + 5
        surface_height = 4 * (5 + PREV_HEIGHT) + 5
        self.ss_cards = ScrollableSurface((surface_width, surface_height),
                (260, 50), scroll_speed=10)

        self.__update_deck_list()

    def __update_deck_list(self):
        del (self.decklist.items)[0:len(self.decklist.items)]
        for d in [d[:-5] for d in deckprovider.get_all_deck_names()]:
            self.decklist.items.append(d)
        self.decklist.selectedIndex = -1
        self.decklist.refresh()

    def __handle_decklist_select(self, *args):
        if 0 <= self.decklist.selectedIndex < len(self.decklist.items):
            self.__reset()
            deck_name = (self.decklist.items)[self.decklist.selectedIndex]
            self.txtName.text = deck_name.decode('UTF-8')
            deck = deckprovider.load_deck(deck_name)

            for c in [c for c in self.cards if c.name in deck]:
                self.selected.append(c)
                self.cards.remove(c)
                self.cards.sort(key=lambda c: c.name)
                self.selected.sort(key=lambda c: c.name)

    def __handle_save_click(self, *args):
        #TODO feedback to UI
        if len(self.selected) < 10:
            logging.debug("need 10 cards for a deck")
            return

        if not self.txtName.text:
            logging.debug("need a name for the deck")
            return

        if self.txtName.text.lower() == 'random':
            logging.debug("can't name deck 'random'")
            return

        deckprovider.save_deck(self.txtName.text, [c.name for c in self.selected])
        self.__update_deck_list()
        self.__reset()
        logging.debug("deck saved")

    def notify(self, event):
        pass

    def draw(self, surface):
        num_cards = len(self.cards)
        num_in_row = (num_cards + 3) / 4
        cards_surface = pygame.Surface(((PREV_WIDTH + 5) * num_in_row +
                5, (PREV_HEIGHT + 5) * 4 + 5))

        x = 5
        y = 5
        i = 0
        for c in self.cards:
            i += 1
            cards_surface.blit(c.image, (x, y))
            c.loc = (x, y)
            x += 5 + PREV_WIDTH
            if i == num_in_row:
                x = 5
                y += 5 + PREV_HEIGHT
                i = 0

        self.ss_cards.draw(surface, cards_surface)

        selected_surface = pygame.Surface(((PREV_WIDTH + 5) * len(self.selected) +
                5, PREV_HEIGHT + 10))

        x = 5
        y = 5

        for c in self.selected:
            selected_surface.blit(c.image, (x, y))
            c.loc = (x, y)
            x += 5 + PREV_WIDTH

        self.ss_selected.draw(surface, selected_surface)

    def __get_card_under_mouse(self, ss, card_list):
        if not ss.get_rect().move(ss.pos).collidepoint(pygame.mouse.get_pos()):
            return
        for c in card_list:
            (x, y) = c.loc
            rect = pygame.Rect(x + ss.x_offset + (ss.pos)[0], y + ss.y_offset +
                               (ss.pos)[1], PREV_WIDTH, PREV_HEIGHT)
            if rect.collidepoint(pygame.mouse.get_pos()):
                return c

    def __reset(self):
        for c in self.selected:
            self.cards.append(c)
        self.selected = []
        self.txtName.text = ''
        self.cards.sort(key=lambda c: c.name)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if len(self.selected) < 10:
                card = self.__get_card_under_mouse(self.ss_cards, self.cards)
                if card:
                    self.cards.remove(card)
                    self.selected.append(card)

            card = self.__get_card_under_mouse(self.ss_selected, self.selected)
            if card:
                self.selected.remove(card)
                self.cards.append(card)

            self.cards.sort(key=lambda c: c.name)
            self.selected.sort(key=lambda c: c.name)

    def leave(self):
        app = self.client.app
        app.widgets = []

    def __handle_back_click(self, *args):
        self.client.go_back()

class LobbyScene(Scene):

    def enter(self):
        app = self.client.app

        self.deck_name = 'random'

        x = 250
        y = 255

        self.lstPlayers = gui.ListBox((x, y), (300, 100), app)

        self.master_options = False

    def __add_master_options(self):
        if not self.master_options:
            app = self.client.app
            gui.Label((15, 50), (180, 0), app, text="Decks")
            self.decklist = gui.ListBox((15, 75), (180, 400), app)
            self.decklist.onItemSelected = self.__handle_decklist_select

            self.decklist.items.append('random')
            for d in [d[:-5] for d in deckprovider.get_all_deck_names()]:
                self.decklist.items.append(d)

            self.decklist.selectedIndex = 0
            self.decklist.refresh()

            x = 700
            y = 350
            btnStart = gui.Button((x, y), (150, 0), app, text=
                                  "Start Game")
            btnStart.onClick = lambda *args: RequestStartGame(self.deck_name).post(self.client.ev)
            y += 25

            btnAddBot = gui.Button((x, y), (150, 0), app, text=
                                   "Add AI-Player")
            btnAddBot.onClick = lambda *args: self.__add_bot()

            y += 25

            btnBack = gui.Button((x, 400), (150, 0), app, text="Back")

            btnBack.onClick = self.back

            self.master_options = True

    def __handle_decklist_select(self, *args):
        if 0 <= self.decklist.selectedIndex < len(self.decklist.items):
            self.deck_name = (self.decklist.items)[self.decklist.selectedIndex]

    def __add_bot(self):
        bt = BotThread(self.client.port)
        bt.start()
        self.client.threads.append(bt)
        
    def notify(self, event):
        if isinstance(event, SetMasterEvent):
            if event.master:
                self.__add_master_options()

        if isinstance(event, PlayerInfoEvent):
            self.lstPlayers.items = []
            for p in event.playerinfos:
                self.lstPlayers.items.append(p.player_name)
            self.lstPlayers.refresh()

        if isinstance(event, TickEvent):
            if self.client.quickmatch:
                time.sleep(0.1) # give the server some time. otherwise podsixnet may spam Errno 10035
                self.__add_bot()
                time.sleep(0.1)
                RequestStartGame(self.deck_name).post(self.client.ev)
                self.client.quickmatch = False
                

    def leave(self):
        app = self.client.app
        app.widgets = []

    def back(self, *args):
        self.client.go_back()

class PlayingScene(Scene):

    def __init__(self, client):
        self.client = client
        self.phasehandler = {P_ACTION: ActionHandler(client),
                             P_BUY: BuyHandler(client),
                             P_CLEANUP: PhaseHandler(client),
                             P_PRECLEANUP: PhaseHandler(client),
                             SP_WAIT: PhaseHandler(client),
                             SP_PICKCARD: PickCardHandler(client),
                             SP_PICKCARDSFROMHAND: PickCardsFromHandHandler(client),
                             SP_ORDERCARDS: OrderCardsHandler(client), 
                             SP_ASKPLAYER: AskPlayerHandler(client)}
    
    def __get_key(self):
        return self.client.phase if self.client.subphase in (None, SP_PLAYERINPUT) else self.client.subphase
    
    def enterphase(self):
        key = self.__get_key()
        if key in self.phasehandler:
            self.phasehandler[key].enterphase()
        
    def draw(self, screen):
        key = self.__get_key()
        if key in self.phasehandler:
            self.phasehandler[key].do_draw()
        
    def handle_event(self, event):
        key = self.__get_key()
        if key in self.phasehandler:
            self.phasehandler[key].do_input(event)
        
    def enter(self):
        app = self.client.app
        x = 650
        y = 255
        self.lstMessages = gui.ListBox(position=(x, y), parent=app, size=
                (300, 100))

    def update(self):
        key = self.__get_key()
        if key in self.phasehandler:
            self.phasehandler[key].do_update()

    def notify(self, event):
        if isinstance(event, MessageEvent):
            self.lstMessages.items.append(event.message)
            self.lstMessages.moveDown()
            self.lstMessages.refresh()
            
        key = self.__get_key()
        if key in self.phasehandler:
            self.phasehandler[key].notify(event)
            
    def leave(self):
        app = self.client.app
        app.widgets = []

class ResultScene(Scene):

    def enter(self):
        app = self.client.app
        x = 400
        y = 255
        self.lstResult = gui.ListBox(position=(x, y), parent=app, size=(300,
                100))

        x = 700
        y = 350
        self.btnFinish = gui.Button(position=(x, y), parent=app, text=
                                    "Finish")
        self.btnFinish.onClick = lambda *args: ResetEvent().post(self.client.ev)

    def notify(self, event):
        if isinstance(event, EndGameEvent):
            self.lstResult.items = []
            for res in event.result:
                self.lstResult.items.append((": ").join(map(str, res)))
            self.lstResult.moveDown()
            self.lstResult.refresh()

    def leave(self):
        app = self.client.app
        app.widgets = []
        

class StartScene(Scene):

    def __init__(self):
        self.name = None
        self.start = None
        self.join = None

    def enter(self):
        app = self.client.app
        
        
        name = self.name
        
        x = 700
        y = 275

        self.txtName = gui.TextBox(position=(x, y), parent=app, text=name)
        y += 25

        self.txtServer = gui.TextBox(position=(x, y), parent=app, text='xxx.x.x.x:xxx')
        y += 25

        self.btnQuick = gui.Button(position=(x, y), size=(150, 0),
                                   parent=app, text="Quick Match")
        self.btnQuick.onClick = self.quick_match
        y += 25

        self.btnStart = gui.Button(position=(x, y), size=(150, 0),
                                   parent=app, text="Start Game")
        self.btnStart.onClick = self.start_server
        y += 25

        self.btnEditor = gui.Button(position=(x, y), size=(150, 0),
                                    parent=app, text="Deck editor")
        self.btnEditor.onClick = self.deck_editor
        y += 25

        self.btnJoin = gui.Button(position=(x, y), size=(150, 0), parent=app, text="Join Game")
        self.btnJoin.onClick = lambda *args: self.req_con()
        y += 25

        self.btnExit = gui.Button(position=(x, y), size=(150, 0), parent=
                                  app, text="Exit")
        self.btnExit.onClick = lambda *args: QuitEvent().post(self.client.ev)

        self.con_requested = False
        self.timer = 0
        self.client.connected = False
            
    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.start:
                self.start = False
                self.start_server()
            if self.join:
                self.join = False
                self.req_con()
            # this is totally hackish
            if not self.client.connected and self.client.threads:
                self.timer += 1
                if self.timer % 50 == 0 and not self.con_requested:
                    self.req_con()
                    self.con_requested = True
        
    def req_con(self):
        self.client.name = self.txtName.text
        if self.txtServer.text != 'xxx.x.x.x:xxx' and self.txtServer.text:
            addr = self.txtServer.text.split(':')
        else:
            addr = find_server()
        self.client.port = int(addr[1])
        self.client.server = addr[0]
        RequestConnectEvent(self.client.server, self.client.port).post(self.client.ev)

    def leave(self):
        app = self.client.app
        app.widgets = []

    def quick_match(self, *args):
        self.client.quickmatch = True
        self.start_server()

    def start_server(self, *args):
        st = ServerThread()
        st.start()

        addr = st.poll()
        logging.info("Server runs on %s" % str(addr))
        udp = UDPServerThread(addr)
        udp.start()
        self.client.threads.append(st)
        self.client.threads.append(udp)

    def deck_editor(self, *args):
        self.client.open_deck_editor()




