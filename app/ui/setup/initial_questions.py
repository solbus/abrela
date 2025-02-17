from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QHBoxLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout, QWidget
)

class InitialQuestionsStep(QWidget):
    continue_clicked = pyqtSignal(str, str, bool)  # all_or_some, shared_or_separate, remember

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Question 1
        q1_label = QLabel("Do you have all of the bootlegger albums downloaded, or just some of them?")
        q1_label.setWordWrap(True)
        q1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q1_label.setFixedWidth(275)
        layout.addWidget(q1_label)

        # Layout for Q1 radio buttons
        q1_hlayout = QHBoxLayout()
        q1_hlayout.setSpacing(40)
        q1_hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.all_button = QRadioButton("All")
        self.some_button = QRadioButton("Some")

        # Group for Q1
        q1_group = QButtonGroup(self)
        q1_group.addButton(self.all_button)
        q1_group.addButton(self.some_button)

        q1_hlayout.addWidget(self.all_button)
        q1_hlayout.addWidget(self.some_button)
        layout.addLayout(q1_hlayout)

        # Add some spacing before Q2
        layout.addSpacing(20)

        # Question 2
        q2_label = QLabel("Do you have the album folders stored in one<br>shared folder, or in separate folders?")
        q2_label.setWordWrap(True)
        q2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q2_label.setFixedWidth(275)
        layout.addWidget(q2_label)

        # Layout for Q2 radio buttons
        q2_hlayout = QHBoxLayout()
        q2_hlayout.setSpacing(40)
        q2_hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.shared_button = QRadioButton("Shared")
        self.separate_button = QRadioButton("Separate")

        # Group for Q2
        q2_group = QButtonGroup(self)
        q2_group.addButton(self.shared_button)
        q2_group.addButton(self.separate_button)

        q2_hlayout.addWidget(self.shared_button)
        q2_hlayout.addWidget(self.separate_button)
        layout.addLayout(q2_hlayout)

        # Remember answers checkbox
        layout.addSpacing(10)
        remember_checkbox_layout = QHBoxLayout()
        remember_checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remember_checkbox = QCheckBox("Remember answers")
        remember_checkbox_layout.addWidget(self.remember_checkbox)
        layout.addLayout(remember_checkbox_layout)

        # Spacing before continue button
        layout.addSpacing(10)

        # Continue button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        continue_button = QPushButton("Continue")
        continue_button.setEnabled(False)
        button_layout.addWidget(continue_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        def check_enable():
            if q1_group.checkedButton() and q2_group.checkedButton():
                continue_button.setEnabled(True)
            else:
                continue_button.setEnabled(False)

        q1_group.buttonClicked.connect(check_enable)
        q2_group.buttonClicked.connect(check_enable)

        continue_button.clicked.connect(self.on_continue_clicked)

        self.adjustSize()

    def on_continue_clicked(self):
        all_some = "all" if self.all_button.isChecked() else "some"
        shared_sep = "shared" if self.shared_button.isChecked() else "separate"
        remember = self.remember_checkbox.isChecked()
        self.continue_clicked.emit(all_some, shared_sep, remember)
