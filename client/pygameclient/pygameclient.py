#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from settings import *

from framework.animations import move_linear
from framework.resourcemanager import ResourceManager
from framework.pygame.resourcehandling import Fontrenderer
from client.pygameclient.scenes.scenemanager import SceneManager
from client.pygameclient.widgets import regnancyStyle
from imagemodding import full_to_prev, full_to_small
from framework.event import RequestChangeName, EndPhaseEvent
from client.pygameclient.scenes.scene import *
from client.pygameclient.imagedownload import download_async

class PygameClient(object):

    def __init__(self, name=None, start=False, join=False, quickmatch=False):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.download_cancel_token = None
        self.download_thread = None
        self._init_resources()
        pygame.display.set_icon(self.res.get('logo'))
        pygame.display.set_caption("Regnancy - the deckbuilding game")
        
        regnancyStyle.init(gui)
        self.app = gui.Desktop()
        self.labelStyleCopy = gui.defaultLabelStyle.copy() #@UndefinedVariable
        (self.labelStyleCopy)['border-width'] = 0
        (self.labelStyleCopy)['wordwrap'] = True
        (self.labelStyleCopy)['autosize'] = False

        self.id = None
        self.phase = None

        self.quickmatch = quickmatch
        self.registered = False  # name registered at server?
        self.mouse_hover_area = {}  # position of cards piles
        self.last_hover = None  # last pile under mouse cursor
        self.mouse_hover_time = 0  # time taken since card under mouse cursor
        self.skip_button_rect = None  # position of skip button
        self.marked_hand_cards = []  # cards in hand marked for action

        self.__skip_button_action = self.end_phase  # action invoked by clicking on the skip-button
        self.skip_button_text = ''
        self.__skip_button_visible = True
        self.threads = []
        self.played_cards = set()
        self.known_cards = set()
        self.global_gamestate = None
        self.subphase = None
        self.master = False

        self.game_started = False
        self.connected = False

        self.hand = None
        self.board = None
        self.master = False
        self.oldhand = None
        self.board = None
        self.oldboard = None

        self.info = " "

        self.boardcommon = None
        self.boardsetup = None

        self.hand_draw_offset = 0
        self.board_draw_offset = 0
        self.info_draw_offset = 0
        self.exit = False
        self.ticks = 0
        
        sc = StartScene()
        sc.name = name or 'Player1'
        self.player_name = name or 'Player1'
        sc.start = start or quickmatch
        sc.join = join
        
        self.scenemanager = SceneManager(self, scenes=(sc, LobbyScene(),
                EditorScene(), PlayingScene(self), ResultScene()))
        
    @property
    def skip_button_action(self):
        return self.__skip_button_action

    @skip_button_action.setter
    def skip_button_action(self, value):
        self.__skip_button_action = value

    @property
    def skip_button_visible(self):
        return self.__skip_button_visible
    
    @skip_button_visible.setter
    def skip_button_visible(self, value):
        self.__skip_button_visible = value
        
    @property
    def active_player(self):
        return next((p for p in self.players if p.current), None)

    @property
    def is_active_player(self):
        return self.active_player and int(self.active_player.id) == int(self.id)

    def open_deck_editor(self):
        self.scenemanager.next(target=EditorScene)

    def __end_threads(self):
        for t in self.threads:
            t.join()
        self.download_cancel_token.cancel = True
        self.threads = []

    def go_back(self):
        self.__end_threads()
        self.scenemanager.back()

    def handle_tickevent(self, event):
        if self.exit:
            return

        self.ticks += 1
        if self.ticks % 200 == 0:
            self.ticks = 0
            for t in self.threads:
                t.keep_alive()

        self.paint(self.screen)
        for e in gui.setEvents():  #called instead of pygame.event.get() for simple-gui
            self._handle_event(e)

        self.app.update()  # update the GUI

        self.scenemanager.update()

        self._handle_mouse_hover_pile()
        self._handle_hand_board_scrolling()

    def handle_endgameevent(self, event):
        self.phase = None
        self.subphase = None
        self.global_gamestate = None
        self.scenemanager.next()

    def handle_setmasterevent(self, event):
        self.master = event.master

    def handle_newhandevent(self, event):
        self.oldhand = self.hand
        self.hand = event.hand
        self.hand.sort(key=lambda e: e.name)
        self.hand.sort(key=lambda e: e.cost)
        self.hand.sort(key=lambda e: e.cardtype)

        x = HAND_DRAW_X
        y = HAND_DRAW_Y

        for (idx, card) in enumerate(self.hand):
            self.known_cards.add(card)
            try:
                old_card = (c for c in self.oldhand if c.id == card.id).next()
                card_rect = old_card.get_rect()
            except (StopIteration, TypeError):
                card_rect = None

            if card_rect:
                x_gen = move_linear(card_rect[0], x)
                y_gen = move_linear(card_rect[1], y)
            else:
                x_gen = move_linear(x, x)
                y_gen = move_linear(1100 + idx * 20, y)

            card.get_rect = lambda x_gen=x_gen, y_gen=y_gen: pygame.Rect(x_gen.next(),
                    y_gen.next(), PREV_WIDTH, PREV_HEIGHT)
            self.played_cards.add(card)
            x += PREV_WIDTH + 5

    def handle_newboardevent(self, event):
        newboard = event.board
        self.oldboard = self.board
        self.board = newboard
        x = BOARD_DRAW_X
        y = BOARD_DRAW_Y
        for card in self.board:
            try:
                nc = (c for c in self.known_cards if c.id == card.id).next()
                (ox, oy, _, _) = nc.get_rect()
                x_gen = move_linear(ox, x, speed=35)
                y_gen = move_linear(oy, y, speed=35)
            except StopIteration:
                x_gen = move_linear(-500, x, speed=35)
                y_gen = move_linear(y, y, speed=35)

            card.get_rect = lambda x_gen=x_gen, y_gen=y_gen: pygame.Rect(x_gen.next(),
                    y_gen.next(), PREV_WIDTH, PREV_HEIGHT)
            self.known_cards.add(card)

            if self.oldboard:
                try:

                    old_card = (c for c in self.oldboard if c.id == card.id).next()
                    old_rect = old_card.get_rect()
                    x_gen = move_linear(old_rect[0], x, speed=35)
                    y_gen = move_linear(old_rect[1], y, speed=35)
                    card.get_rect = lambda x_gen=x_gen, y_gen=y_gen: \
                        pygame.Rect(x_gen.next(), y_gen.next(),
                                    PREV_WIDTH, PREV_HEIGHT)
                except StopIteration:
                    pass

            x += PREV_WIDTH + 5

    def handle_newboardsetupevent(self, event):
        self.boardsetup = event.boardsetup

    def handle_newboardcommonevent(self, event):
        self.boardcommon = event.boardcommon

    def handle_connectionfailed(self, event):
        logging.debug("connection failed")

    def handle_connectionsuccess(self, event):
        RequestChangeName(self.name).post(self.ev)
        self.scenemanager.next(target=LobbyScene)
        self.id = event.id
        self.connected = True

    def handle_globalphasechangedevent(self, event):
        self.global_gamestate = event.phase

    def handle_subphasechangedevent(self, event):
        self.subphase = event.subphase
        self.info = event.info
        if self.subphase == SP_PLAYERINPUT:
            self.skip_button_action = self.end_phase
            
        self.scenemanager.enterphase()
        
    def handle_phasechangedevent(self, event):
        self.hand_draw_offset = 0
        self.info_draw_offset = 0
        self.board_draw_offset = 0
        self.phase = event.phase
        if self.phase == P_CLEANUP:
            self.played_cards.clear()
            self.known_cards.clear()

    def handle_playerinfoevent(self, event):
        self.players = event.playerinfos

    def handle_resetevent(self, event):
        self.restart()

    def handle_gamestartedevent(self, event):
        self.game_started = True
        self.scenemanager.next(target=PlayingScene)

    def notify(self, event):
        """Callend when an event occurs"""

        self.scenemanager.notify(event)

    def end_phase(self, *args):
        EndPhaseEvent().post(self.ev)

    def restart(self, *args):
        self.__end_threads()
        self.__init__(self.player_name)
        self.registered = False

    def _init_resources(self):
        self.res = ResourceManager()
        mod = {'': lambda x:x,
               'small': full_to_small,
               'prev': full_to_prev}
        self.res.load_images(os.path.join('res', 'cards_full'),
                             (CARD_WIDTH, CARD_HEIGHT),
                             mod)
        
        def download_finished(path):
            self.res.load(path, (CARD_WIDTH, CARD_HEIGHT), mod)
        
        self.download_cancel_token, self.download_thread = download_async(download_finished)
        logging.info("download images...")
        
        self.res.load_images(os.path.join('res', 'ico'), (ICON_WIDTH, ICON_HEIGHT))
        
        self.res.load_images(os.path.join('res', 'dialog'), (700, 400))
        self.res.load_images(os.path.join('res', 'background'), SCREEN_SIZE)
        
        self.res.load_images(os.path.join('res', 'icon'), (30, 30))
        
        self.res.load_images(os.path.join('res', 'phase'), (ICON_WIDTH * 3.2, ICON_HEIGHT * 1.2))
        
        self.res.load_images(os.path.join('res', 'name'), (200, 30))

        self.fontr = Fontrenderer()

        self.fonts = {'ffont': pygame.font.Font(os.path.join('res/fonts', 'ffont.ttf'), 160), 
                      'font': pygame.font.Font(os.path.join('res/fonts', 'font.ttf'), 19),
                      'small_font': pygame.font.Font(os.path.join('res/fonts', 'font.ttf'), 9)}

    def _handle_event(self, event):

        if event.type == pygame.QUIT:
            self.exit = True
            self.__end_threads()
            exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
            logging.debug("Client is in %s %s", self.phase, self.subphase)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            EndPhaseEvent().post(self.ev)

        if self.skip_button_rect:
            if event.type == pygame.MOUSEBUTTONUP and self.skip_button_visible and \
                self.skip_button_rect.collidepoint(pygame.mouse.get_pos()):
                self.skip_button_action(self)

        self.scenemanager.handle_event(event)

    def paint(self, screen):
        """Draw the screen"""

        self.screen.blit(self.res.get('regnancy'), (0, 0))

        self.app.draw()

        self.scenemanager.draw(self.screen)
        
        if self.download_thread and self.download_thread.is_alive():
            self.fontr.render((self.fonts)['small_font'], 
                              'checking and downloading card images...', 
                              (255, 255, 255), self.screen,
                              (10, 10))
        
        pygame.display.flip()

    def _handle_hand_board_scrolling(self):
        if self.hand and self.board:
            pos = pygame.mouse.get_pos()

            mouse_hand = HAND_DRAW_Y + PREV_HEIGHT > pos[1] > HAND_DRAW_Y
            mouse_board = BOARD_DRAW_Y + PREV_HEIGHT > pos[1] > BOARD_DRAW_Y

            mouse_right_border = SCREEN_WIDTH - PREV_WIDTH < pos[0] < SCREEN_WIDTH
            mouse_left_border = 0 < pos[0] < PREV_WIDTH

            cards_out_of_screen = HAND_DRAW_X + (PREV_WIDTH + 5) * len(self.hand) + \
                self.hand_draw_offset + 5 > SCREEN_WIDTH
                
            board_out_of_screen = BOARD_DRAW_X + (PREV_WIDTH + 5) * len(self.board) + \
                self.board_draw_offset + 5 > SCREEN_WIDTH

            if hasattr(self.info, 'cards'):
                info_out_of_screen = BOARD_DRAW_X + (PREV_WIDTH + 5) * len(self.info.cards) + \
                    self.info_draw_offset + 5 > SCREEN_WIDTH

                if mouse_hand and mouse_right_border and info_out_of_screen:
                    self.info_draw_offset -= SCROLL_SPEED
                elif mouse_hand and mouse_left_border and self.info_draw_offset < 0:
                    self.info_draw_offset += SCROLL_SPEED

            if mouse_hand and mouse_right_border and cards_out_of_screen:
                self.hand_draw_offset -= SCROLL_SPEED
            elif mouse_hand and mouse_left_border and self.hand_draw_offset < 0:
                self.hand_draw_offset += SCROLL_SPEED

            if mouse_board and mouse_right_border and board_out_of_screen:
                self.board_draw_offset -= SCROLL_SPEED
            elif mouse_board and mouse_left_border and self.board_draw_offset < 0:
                self.board_draw_offset += SCROLL_SPEED

    def _handle_mouse_hover_pile(self):
        if self.subphase == SP_ASKPLAYER:
            return

        pos = pygame.mouse.get_pos()

        current_hover = None
        try:
            current_hover = next(i for i in self.mouse_hover_area.keys()
                if (self.mouse_hover_area)[i].collidepoint(pos))
        except StopIteration:
            pass

        if current_hover:
            if current_hover != self.last_hover:
                self.mouse_hover_time = 0
            self.last_hover = current_hover
            self.mouse_hover_time += 1
        else:
            self.mouse_hover_time = 0



