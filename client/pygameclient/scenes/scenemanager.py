#!/usr/bin/python
# -*- coding: utf-8 -*-


class SceneManager(object):

    """Manages different scenes, like the starting or lobby scene"""

    def __init__(self, client, scenes=[]):
        assert scenes

        self.client = client
        self.scenes = []
        self.current = None
        [self.add(scene) for scene in scenes]

    def add(self, scene):
        """Add a new scene to the manager. The first scene added will automatically be the starting screen"""

        scene.client = self.client
        scene.manaer = self
        self.scenes.append(scene)
        if not self.current:
            self.__enter(scene)

    def next(self, target=None):
        """Move to the next scene"""

        self.prev = self.current

        if target:
            s = next(s for s in self.scenes if isinstance(s, target))
            self.__enter(s)
        else:
            idx = self.scenes.index(self.current)
            self.__enter((self.scenes)[idx + 1])

    def back(self):
        self.__enter(self.prev)

    def notify(self, event):
        """Handles events (by passing them to the current scene)"""

        self.current.notify(event)

    def __enter(self, scene):
        """Leave the current scene and enter the given scene"""

        if self.current:
            self.current.leave()
        self.current = scene
        self.current.enter()

    def draw(self, surface):
        if self.current:
            self.current.draw(surface)

    def handle_event(self, event):
        if self.current:
            self.current.handle_event(event)

    def update(self):
        if self.current:
            self.current.update()

    def enterphase(self):
        if self.current:
            self.current.enterphase()