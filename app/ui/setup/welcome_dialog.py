from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget 
)

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Welcome")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.dont_show_again = False

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 5, 8, 5)

        # Scroll area for the explanatory text
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Text widget with padding on the left side
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(10, 5, 10, 2)

        info_label = QLabel()
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        info_label.setText(
            "<b>Version 1.0.1</b><br><br>"
            "Abrela works with the King Gizzard & The Lizard Wizard bootlegger albums from<br>"
            "<a href=\"https://bootleggizzard.bandcamp.com\">https://bootleggizzard.bandcamp.com</a>.<br>"
            "It is an unofficial & fan-made choose-your-own-adventure MP3 editor & mixer.<br><br>"
            "---<br><br>"
            "<b>Important:</b> Currently, only unmodified MP3-format albums from Bandcamp are supported.<br>"
            "<b>MP3 320</b> is recommended over MP3 V0 because Abrela is configured to maintain MP3 320 quality.<br><br>"
            "<b>To get started:</b><br>"
            "<b>1.</b> Download albums from the Bandcamp link above (free, but consider throwing some $ at the band!).<br>"
            "<b>2.</b> Extract each album's ZIP - this will create one folder for each album (you can delete the ZIPs after).<br>"
            "<b>3.</b> After extracting, move all of the album folders to one shared folder (optional, but recommended).<br>"
            "<b>4.</b> Close this welcome message and continue in the main window.<br><br>"
            "Tutorial video: <a href=\"https://youtu.be/AEIggCPhB8k\">https://youtu.be/AEIggCPhB8k</a><br><br>"
            "---<br><br>"
            "Abrela works with transition logic, specifically <b>default</b> and <b>custom</b> transitions:<br>"
            "- <b>Default transitions</b> are all available - they're just the next track on any given album.<br>"
            "- <b>Custom transitions</b> are all defined manually, so future versions of Abrela will include more of them.<br>"
            "- Custom transitions will only be available if you have downloaded the albums with those transitions.<br><br>"
            "List of all custom transitions currently available:<br>"
            "<a href=\"https://github.com/solbus/abrela/blob/main/TRANSITIONS.md\">https://github.com/solbus/abrela/blob/main/TRANSITIONS.md</a><br><br>"
            "If you set up Abrela with just some of the albums and then want to add more,<br>"
            "click the <b>Start Over</b> button under the list of all the albums.<br><br>"
            "---<br><br>"
            "Send me bug reports & suggestions & let me know if any transitions sound bad!<br>"
            "- Discord server King Gizzcord: <b>@Solbus</b><br>"
            "- Reddit: <b>u/automation_kglw</b><br>"
            "- Email: <b>kglwautomation@gmail.com</b><br><br>"
            "I'm super open to the idea of collaborators:<br>"
            "- <b>Transition Makers:</b> Only basic audio editing experience needed to contribute!<br>"
            "- <b>Programmers:</b> Because I have no idea what I'm doing!<br>"
            "- <b>Graphic Artists:</b> Some visual assets for this could be nice!<br>"
            "I am not currently able to hire help, but anyone volunteering to contribute will be credited.<br><br>"
            "---<br><br>"
            "<b>A friendly reminder:</b><br>"
            "The spirit of the KGLW bootleggers is in <b>physical media</b>, so Abrela is intended for personal use only,<br>"
            "or for those experimenting with intentions to create physical media.<br><br>"
            "Relevant info from <a href=\"https://kinggizzardandthelizardwizard.com/bootlegger\">https://kinggizzardandthelizardwizard.com/bootlegger</a>:<br>"
            "<b>Q:</b> \"Can I upload to Spotify or other DSPs like Apple Music?\"<br>"
            "<b>A:</b> \"No thanks! Let's keep this shit underground baby.\"<br>"
            "<b>Also:</b> \"The licence only extends to physical copies of the music.\"<br><br>"
            "---<br><br>"
            "<b>GPL v3 Notice</b> - link to full license: <a href=\"https://github.com/solbus/abrela/blob/main/LICENSE\">https://github.com/solbus/abrela/blob/main/LICENSE</a><br>"
            "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.<br><br>"
            "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.<br><br>"
            "You should have received a copy of the GNU General Public License along with this program. If not, see <a href=\"https://www.gnu.org/licenses/\">https://www.gnu.org/licenses/</a>."
        )

        text_layout.addWidget(info_label)
        scroll_area.setWidget(text_widget)
        main_layout.addWidget(scroll_area)

        # "Don't show again" checkbox, centered
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.make_centered_checkbox(), alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(checkbox_layout)

        # Close button at bottom
        bottom_button_layout = QHBoxLayout()
        close_bottom_button = QPushButton("Close")
        close_bottom_button.clicked.connect(self.handle_close_button)
        bottom_button_layout.addWidget(close_bottom_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(bottom_button_layout)

        self.setLayout(main_layout)

    def make_centered_checkbox(self):
        self.dont_show_checkbox = QCheckBox("Don't show this again")
        return self.dont_show_checkbox

    def handle_close_button(self):
        self.dont_show_again = self.dont_show_checkbox.isChecked()
        self.accept()

    def show_dialog(self, parent_geometry):
        # Fixed dialog size
        dialog_width = 605
        dialog_height = 400
        self.setFixedSize(dialog_width, dialog_height)

        # Center coordinates
        px = parent_geometry.x() + (parent_geometry.width() - dialog_width) // 2
        py = parent_geometry.y() + (parent_geometry.height() - dialog_height) // 2

        self.move(px, py)
        return self.exec()
