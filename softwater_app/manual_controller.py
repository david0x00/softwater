from controller import Controller

class ManualController(Controller):
    def __init__(self):
        super().__init__()
    
    def implement_controls(self, u):
        return False

controller = ManualController()