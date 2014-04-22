#!/usr/bin/python
# -*- coding: utf-8 -*-


import pygame
from framework.event import AnswerEvent, PlayCardEvent, BuyCardEvent,\
    NewHandEvent
from framework.locals import WHITE
from itertools import chain
from game.cards.card import TREASURE
from game.gamestates import *
from client.pygameclient.settings import *

class PhaseHandler(object):
    
    def __init__(self, client):
        self.client = client

    def __getattr__(self, name):
        return getattr(self.client, name)

    def _draw_text(self, text, color, pos, shadow=True, font='font'):

        if not isinstance(text, str) and not isinstance(text, unicode):
            return
        if len(text) == 0:
            text = " "
        self.fontr.render((self.fonts)[font], text, color, self.screen, pos)

    def do_draw(self, draw_info_cards=False):
        """Draw everything from board to player info etc. (except GUI)"""

        self._drawpart_kingdom_piles()
        self._drawpart_common_piles()
        self._drawpart_board()
        if draw_info_cards:
            self._drawpart_info_cards()
        else:
            self._drawpart_hand()
        self._drawpart_player_info()
        self._drawpart_phase_indicator()
        self._drawpart_go()
        self._drawpart_mouse_hover()
    
    def _drawpart_kingdom_piles(self):
        """Draw the kingdom card piles"""

        if self.boardsetup:
            self._drawpart_piles(self.boardsetup, 15, SCREEN_HEIGHT / 5.6, 5)
    
    def _drawpart_common_piles(self):
        """Draw the common card piles"""

        if self.boardcommon:
            self._drawpart_piles(self.boardcommon, 15, 30, 4, True)
    
    def _drawpart_piles(self, piles, start_x, start_y, columns, small=False):
        """Draw card piles"""

        x = start_x
        y = start_y

        size = (PREV_WIDTH, PREV_WIDTH) if not small else (SMALL_WIDTH, SMALL_HEIGHT)

        for pile in piles:
            rect = pygame.Rect(x, y, size[0], size[1])
            (self.mouse_hover_area)[pile.id] = rect

            hover = rect.collidepoint(pygame.mouse.get_pos())
            dx = x - 1 if hover else x
            dy = y - 1 if hover else y

            self.screen.blit(self.res.get(pile.name.lower(), 'prev' if not small else 'small'),
                             (dx, dy))

            self._draw_text(str(len(pile)), WHITE, (dx + 3, dy + 3),
                            True)

            if pile.calc_cost != pile.cost:
                cost_y = (PREV_HEIGHT if not small else SMALL_HEIGHT) - \
                    21

                self._draw_text(str((pile.calc_cost)[0]), (255, 255, 0),
                                (dx + 3, dy + cost_y), True)

            x += size[0] + 5
            if x >= start_x + columns * (size[0] + 5):
                x = start_x
                y += size[1] + size[1] / 7.0

    def _drawpart_board(self):
        """Draw the cards that are played"""

        if not self.board:
            return
        
        for card in self.board:
            rect = card.get_rect().move(self.board_draw_offset, 0)
            self.screen.blit(self.res.get(card.name.lower(), 'prev'),
                             rect)

            if card.calc_cost != card.cost:
                cost_y = PREV_HEIGHT - 21
                (dx, dy) = (rect.left, rect.top)
                self._draw_text(str((card.calc_cost)[0]), (255, 255,
                                0), (dx + 3, dy + cost_y), True)

    def _drawpart_info_cards(self):
        x = HAND_DRAW_X
        y = HAND_DRAW_Y
            
        for card in self.info.cards:
            card.get_rect = lambda x=x, y=y: pygame.Rect(x, y, PREV_WIDTH, PREV_HEIGHT)
            rect = card.get_rect().move(self.info_draw_offset, 0)
            self.screen.blit(self.res.get(card.name.lower(), 'prev'), rect)
            if card.calc_cost != card.cost:
                cost_y = PREV_HEIGHT - 21
                (dx, dy) = (rect.left, rect.top)
                self._draw_text(str((card.calc_cost)[0]), (255, 255, 0),
                                (dx + 3, dy + cost_y), True)
                
            x += PREV_WIDTH + 5
                                    
    def _drawpart_hand(self):
        """Draw the cards we have in hand"""

        if not self.hand:
            return

        for card in self.hand:
            rect = card.get_rect().move(self.hand_draw_offset, 0)
            self.screen.blit(self.res.get(card.name.lower(), 'prev'),
                             rect)
            if card.calc_cost != card.cost:
                cost_y = PREV_HEIGHT - 21
                (dx, dy) = (rect.left, rect.top)
                self._draw_text(str((card.calc_cost)[0]), (255, 255, 0),
                                (dx + 3, dy + cost_y), True)
                
    def _drawpart_go(self):
        """Draws the skip button and some text"""

        y = 415
        x = 650
        self._draw_text(self.client.skip_button_text, WHITE, (x + 60, y + 15),
                        True)

        if self.client.skip_button_visible:
            self.client.skip_button_rect = pygame.Rect(x, y, ICON_WIDTH, ICON_HEIGHT)
            
            if pygame.mouse.get_pressed()[0] and self.client.skip_button_rect.collidepoint(pygame.mouse.get_pos()):
                x += 2
                y += 2
            self.screen.blit(self.res.get('button', 'ico'), (x, y))

    def _drawpart_phase_indicator(self):
        """Draws the little images that shows which phase we are in"""

        y = 415
        (action, buy, cleanup) = (15, 65, 115)

        self.screen.blit(self.res.get('phase'), (action - 5, y - 4))

        x = None
        if self.global_gamestate == P_ACTION:
            x = action
        if self.global_gamestate == P_BUY:
            x = buy
        if self.global_gamestate == P_CLEANUP or self.global_gamestate == \
            P_PRECLEANUP:
            x = cleanup
        if x:
            self.screen.blit(self.res.get('indicator', 'ico'), (x, y))

        self.screen.blit(self.res.get('anvil', 'ico'), (action, y))
        self.screen.blit(self.res.get('coins', 'ico'), (buy, y))
        self.screen.blit(self.res.get('broom', 'ico'), (cleanup, y))
        phase = " "
        text = " "

        cur = self.active_player

        if not cur:
            return

        if self.global_gamestate != P_CLEANUP:
            address = '%s has' % cur.player_name if not self.is_active_player else 'You have'
            money = cur.money
            potion = ', %i potion%s' % (cur.potion, '' if cur.potion ==
                    1 else 's') if cur.potion else ''
            count = cur.actions if self.global_gamestate == P_ACTION else cur.buys
            action = 'action' if cur.actions == 1 else 'actions'
            buy = 'buy' if cur.buys == 1 else 'buys'
            t = action if self.global_gamestate == P_ACTION else buy
            text = '%s %i money%s and %i %s left' % (address, money,
                    potion, count, t)

        if self.global_gamestate == P_ACTION:
            phase = 'Action-Phase'
        elif self.global_gamestate == P_BUY:
            phase = 'Buy-Phase'
        elif self.global_gamestate == P_CLEANUP or self.global_gamestate == \
            P_PRECLEANUP:
            phase = 'Cleanup-Phase'

        self._draw_text(phase, WHITE, (178, 415), True)
        self._draw_text(text, WHITE, (178, 437), True)

    def _drawpart_player_info(self):
        """Draw the player information box"""

        x = 820
        y = 170
        for p in self.players:
            self.screen.blit(self.res.get('name'), (x - 5, y - 5))
            self._draw_text(p.player_name, WHITE, (x, y), True)
            if p.current:
                self._draw_text('*', WHITE, (x + 95, y), True)
            self._draw_text(str(p.hand_size), WHITE, (x + 120, y), True)
            self._draw_text(str(p.drawpile_size), WHITE, (x + 145, y),
                            True)
            self._draw_text(str(p.discardpile_size), WHITE, (x + 170, y),
                            True)
            y += 25
     
    def _drawpart_mouse_hover(self):
        """Draw the full card image when hovering over a card"""

        if self.mouse_hover_time >= HOVER_TIME:
            (x, y) = pygame.mouse.get_pos()
            if y + CARD_HEIGHT > SCREEN_HEIGHT:
                y -= (y + CARD_HEIGHT) - SCREEN_HEIGHT
            if x + CARD_WIDTH > SCREEN_WIDTH:
                x -= (x + CARD_WIDTH) - SCREEN_WIDTH
            allpiles = list(chain(*[self.boardsetup, self.boardcommon]))
            pile = next(pile for pile in allpiles if pile.id == self.last_hover)

            self.screen.blit(self.res.get(pile.name.lower()), (x, y)) 
                
    def enterphase(self):
        self.client.skip_button_text = (self.info.text or '') if self.info else ''
        self.client.skip_button_visible = False
        self.do_update()
    
    def do_update(self):
        pass
    
    def do_input(self, event):
        pass

    def notify(self, event):
        pass

class PickCardsFromHandHandler(PhaseHandler):

    def __init__(self, client):
        PhaseHandler.__init__(self, client)
    
    def do_draw(self):
        super(PickCardsFromHandHandler, self).do_draw()
        offset = (25, 2)
        for i, card in enumerate(self.marked_hand_cards):
            rect = card.get_rect().move(self.hand_draw_offset, 0)
            pos = ((rect[0] + PREV_WIDTH) - ICON_WIDTH, rect[1] - ICON_HEIGHT / 2)
            self.screen.blit(self.res.get('uparrow', 'ico'), pos)
            self._draw_text(str(i + 1), (255, 255, 255), map(sum,zip(pos, offset)))
        self._drawpart_mouse_hover()
        
    def do_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for card in self.hand:
                if card.get_rect().move(self.hand_draw_offset, 0).collidepoint(pos):
                    if card in self.marked_hand_cards:
                        self.marked_hand_cards.remove(card)
                    else:
                        self.marked_hand_cards.append(card)
                        
    def enterphase(self):
        self.client.skip_button_visible = True
        self.marked_hand_cards = []
        self.client.skip_button_action = self.__send_cards
        self.client.skip_button_visible = True
        self.client.skip_button_text = self.info.text
    
    def __send_cards(self, *args):
        AnswerEvent([c.id for c in self.marked_hand_cards]).post(self.ev)
        self.marked_hand_cards = []
   
class PickCardHandler(PhaseHandler):

    def __init__(self, client):
        PhaseHandler.__init__(self, client)
        
    def do_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.last_hover and self.mouse_hover_time > 0:
                allpiles = list(chain(*[self.boardsetup, self.boardcommon]))
                pile = next(pile for pile in allpiles if pile.id == self.last_hover)
                AnswerEvent(pile.id).post(self.ev)
        
    def do_update(self):
        self.client.skip_button_visible = True
        self.client.skip_button_text = self.info.text
    
    
    def pickcard_enterphase(self):
        self.client.skip_button_visible = True
        self.client.skip_button_action = self.__send_none
    
    def __send_none(self, *args):
        AnswerEvent(None).post(self.ev)
        
class OrderCardsHandler(PhaseHandler):

    def __init__(self, client):
        PhaseHandler.__init__(self, client)
        
    def do_draw(self):
        super(OrderCardsHandler, self).do_draw(draw_info_cards=True)
        offset = (25, 2)
        for i, card in enumerate(self.marked_hand_cards):
            rect = card.get_rect().move(self.info_draw_offset, 0)
            pos = ((rect[0] + PREV_WIDTH) - ICON_WIDTH, rect[1] - ICON_HEIGHT / 2)
            self.screen.blit(self.res.get('uparrow', 'ico'), pos)
            self._draw_text(str(i + 1), (255, 255, 255), map(sum,zip(pos, offset)))
        self._drawpart_mouse_hover()
        
    def do_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for card in self.info.cards:
                if card.get_rect().move(self.info_draw_offset, 0).collidepoint(pos):
                    if card in self.marked_hand_cards:
                        self.marked_hand_cards.remove(card)
                    else:
                        self.marked_hand_cards.append(card)
    
    def enterphase(self):
        self.client.skip_button_visible = True
        self.marked_hand_cards = []
        self.client.skip_button_action = self.__send_cards
        self.client.skip_button_visible = True
        self.client.skip_button_text = self.info.text
        
    def __send_cards(self, *args):
        AnswerEvent([c.id for c in self.marked_hand_cards]).post(self.ev)
        self.marked_hand_cards = []
                
class BuyHandler(PhaseHandler):

    def __init__(self, client):
        PhaseHandler.__init__(self, client)
        self.play_lock = False
        self.played = []

    def enterphase(self):
        self.play_lock = False
        self.client.skip_button_text = 'finish buy phase' if self.is_active_player else ''
        self.client.skip_button_visible = self.is_active_player
        
    def do_update(self):
        if self.play_lock: 
            return
        
        treasures = [c for c in self.hand if c.cardtype & TREASURE]
        
        if treasures and \
           all(t.name in ("Copper", "Silver", "Gold", "Platinum") for t in treasures):
            card = treasures[0]
            if not card.id in self.played and card in self.hand:
                PlayCardEvent(card.id).post(self.ev)
                self.play_lock = True
                self.played.append(card.id)

    def notify(self, event):
        if isinstance(event, NewHandEvent):
            self.play_lock = False
            self.played = []
                    
    def do_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.last_hover and self.mouse_hover_time > 0:
                allpiles = list(chain(*[self.boardsetup, self.boardcommon]))
                try:
                    pile = next(pile for pile in allpiles if pile.id == self.last_hover)
                    BuyCardEvent(pile.id).post(self.ev)
                except StopIteration:
                    pass
            pos = pygame.mouse.get_pos()
            
            for card in self.hand:
                if card.get_rect().move(self.hand_draw_offset, 0).collidepoint(pos):
                    PlayCardEvent(card.id).post(self.ev)
                    self.played_cards.add(card)
                    self.last_card_played = card
       
class ActionHandler(PhaseHandler):

    def __init__(self, client):
        PhaseHandler.__init__(self, client)
       
    def do_update(self):
        self.client.skip_button_text = 'finish action phase' if self.is_active_player else ''
        self.client.skip_button_visible = self.is_active_player
        
    def do_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for card in self.hand:
                if card.get_rect().move(self.hand_draw_offset, 0).collidepoint(pos):
                    PlayCardEvent(card.id).post(self.ev)
                    self.played_cards.add(card)
                    self.last_card_played = card

class AskPlayerHandler(PhaseHandler):

    def __init__(self, client):
        PhaseHandler.__init__(self, client)

    def do_draw(self):
        super(AskPlayerHandler, self).do_draw()
        self.question.draw()
        
    def do_input(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            for answer in self.question.answers:
                if answer[1].collidepoint(pos):
                    AnswerEvent(answer[0]).post(self.ev)
        
    def enterphase(self):
        self.question = Question(self.client)

class Question(object):

    def __init__(self, client):
        self.x = 162
        self.y = 184
        self.left_border = 245
        self.title = client.info.title
        self.text = client.info.text
        self.s = pygame.Surface((700, 400), pygame.SRCALPHA, 32)
        self.s.convert_alpha()
        self.client = client
        self.s.blit(client.res.get('dialog'), (0, 0))
        try:
            card_face = client.res.get(client.info.card_to_show.lower())
            self.s.blit(card_face, (30, 40))
        except:
            pass
        tmp = self.left_border
        client.fontr.render((client.fonts)['font'], str(client.info.title),
                            WHITE, self.s, (tmp, 30))
        client.fontr.render((client.fonts)['font'], str(client.info.text),
                            WHITE, self.s, (tmp, 55))
        y = 85
        self.answers = []
        for answer in client.info.answers:
            client.fontr.render((client.fonts)['font'], str(answer),
                                WHITE, self.s, (self.left_border +
                                ICON_WIDTH, y + 12))
            self.answers.append((answer, pygame.Rect(self.x + self.left_border,
                                self.y + y, ICON_WIDTH, ICON_HEIGHT)))
            y += 55

    def draw(self):
        y = 85
        s = self.s.copy()
        for answer in self.answers:
            if pygame.mouse.get_pressed()[0] and answer[1].collidepoint(pygame.mouse.get_pos()):
                s.blit(self.client.res.get('button', 'ico'), (self.left_border +
                       2, y + 2))
            else:
                s.blit(self.client.res.get('button', 'ico'), (self.left_border,
                       y))
            y += 55
        self.client.screen.blit(s, (self.x, self.y))