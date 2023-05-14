from controller import Controller

class ManualController(Controller):
    def __init__(self):
        super().__init__()
    
    def on_start(self):
        print("Controller Start")

    def on_end(self):
        print("Controller End")
    
    def implement_controls(self, u):
        pass

    def evaluate(self, *args):
        return [False for _ in range(len(self.u_headers))]

controller = ManualController()
