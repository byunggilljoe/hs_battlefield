class Scene:
    def update(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

    def handle_event(self, event):
        raise NotImplementedError
