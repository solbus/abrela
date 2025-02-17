from PyQt6.QtWidgets import QPushButton

class StartOverButton(QPushButton):
    def __init__(self, setup_flow_controller, parent=None):
        super().__init__("Start Over", parent)
        self.setup_flow_controller = setup_flow_controller
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        # Delegate the actual "start over" logic to the flow controller
        self.setup_flow_controller.handle_start_over()
