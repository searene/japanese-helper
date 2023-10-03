import os
import tempfile
from enum import Enum
from functools import lru_cache
from typing import Optional

import requests
from aqt.utils import showWarning
from aqt.qt import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLineEdit,
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    Qt,
    qtmajor,
)
from aqt.editor import Editor


last_query = ""


class StyleType(Enum):
    HIGH_FROM_HIGH = 1,
    LOW_FROM_LOW = 2,
    HIGH_FROM_LOW = 3,
    LOW_FROM_HIGH = 4


def post(path: str, body: dict) -> dict:
    url = "https://jotoba.de" + path
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=body, headers=headers)
    if response.status_code != 200:
        showWarning("Failed to fetch audio from jotoba.de, please try again later.")
    return response.json()


@lru_cache
def search_for_words(query: str) -> dict:
    body = {
        "query": query,
        "language": "English",
        "no_english": False
    }
    print("in it")
    return post("/api/search/words", body)


class JapaneseHelperDialog(QDialog):
    def __init__(self, editor: Editor, parent_window: QWidget):
        super().__init__()
        self.init_ui(editor, parent_window)
        if QApplication.clipboard().text():
            self.text_editor.setText(QApplication.clipboard().text())
        else:
            self.text_editor.setText(last_query)

    def init_ui(self, editor: Editor, parent_window: QWidget) -> None:
        self.editor = editor
        self.parent_window = parent_window
        self.setWindowTitle("Japanese Helper")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.text_editor = QLineEdit()
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Japanese: "))
        input_layout.addWidget(self.text_editor)
        self.layout.addLayout(input_layout)

        self.button_group = QButtonGroup()
        self.button_group_layout = QHBoxLayout()
        self.button_group_layout.addStretch()
        self.add_audio_button = QPushButton("Add audio")
        self.add_audio_button.clicked.connect(lambda _: self.on_add_audio(self.editor))
        self.add_pitch_accent_button = QPushButton("Add pitch accent")
        self.add_pitch_accent_button.clicked.connect(lambda _: self.on_add_pitch_accent(self.editor))
        self.button_group.addButton(self.add_audio_button)
        self.button_group.addButton(self.add_pitch_accent_button)
        self.button_group_layout.addWidget(self.add_audio_button)
        self.button_group_layout.addWidget(self.add_pitch_accent_button)
        self.layout.addLayout(self.button_group_layout)

    def on_add_pitch_accent(self, editor: Editor) -> None:
        global last_query
        last_query = self.get_query()
        pitch_accent = self.fetch_pitch_accent(self.get_query())
        if pitch_accent is None:
            showWarning("Cannot find pitch accent for this word.")
        else:
            self.close()
            editor.web.eval(f"wrap('<span class=\"pitch-accent\">{pitch_accent}</span>', '')")

    def fetch_pitch_accent(self, query: str) -> Optional[str]:
        response = search_for_words(query)
        word = self.get_word(response, query)
        if (word is None) or ("pitch" not in word) or (not word["pitch"]):
            return None
        return self.convert_pitch_list_to_html(word["pitch"])

    def convert_pitch_list_to_html(self, pitch_list: list) -> str:
        html_elements = []
        for i in range(len(pitch_list)):
            html_elements.append(self.convert_single_pitch_to_html(pitch_list, i))
        inner_elements = "".join(html_elements)
        return f"<span class=\"pitch-accent\">{inner_elements}</div>"

    def on_add_audio(self, editor: Editor) -> None:
        global last_query
        last_query = self.get_query()
        audio_file_path = self.fetch_audio(self.get_query())
        if audio_file_path is None:
            showWarning("Cannot find audio for this word.")
        editor.addMedia(audio_file_path)
        self.close()

    def get_query(self) -> str:
        return self.text_editor.text().strip()

    def get_word(self, response: dict, query: str) -> Optional[dict]:
        if not response["words"]:
            return None
        for word in response["words"]:
            if "reading" in word and self.is_same_word(query, word["reading"]):
                return word

    def fetch_audio(self, query: str) -> Optional[str]:
        """Fetch audio from jotoba.de"""
        response = search_for_words(query)
        word = self.get_word(response, query)
        if (word is None) or ("audio" not in word) or (word["audio"] is None):
            return None
        response = requests.get("https://jotoba.de" + word["audio"])
        if response.status_code != 200:
            return None
        base_name = word["audio"].split("/")[-1]
        abs_file_path = os.path.join(tempfile.mkdtemp(), base_name + ".mp3")
        with open(abs_file_path, 'wb') as f:
            f.write(response.content)
        return abs_file_path

    def convert_single_pitch_to_html(self, pitch_list: [dict], i: int) -> str:
        """Convert a single pitch to HTML"""
        style_type = self.get_style_type(pitch_list, i)
        css = self.get_css(style_type)
        return f"<span class=\"pitch-accent-{style_type}\" style=\"{css}\">{pitch_list[i]['part']}</span>"

    def get_style_type(self, pitch_list: [dict], i: int) -> StyleType:
        pitch = pitch_list[i]
        if i == 0 or pitch_list[i - 1]["high"] == pitch["high"]:
            return StyleType.HIGH_FROM_HIGH if pitch["high"] else StyleType.LOW_FROM_LOW
        return StyleType.HIGH_FROM_LOW if pitch["high"] else StyleType.LOW_FROM_HIGH

    def get_css(self, style_type: StyleType) -> str:
        if style_type == StyleType.HIGH_FROM_HIGH:
            return "border-top: 2px solid red;"
        elif style_type == StyleType.LOW_FROM_LOW:
            return "border-bottom: 2px solid red;"
        elif style_type == StyleType.HIGH_FROM_LOW:
            return "border-left: 2px solid red; border-top: 2px solid red;"
        else:
            return "border-left: 2px solid red; border-bottom: 2px solid red;"

    def is_same_word(self, query: str, reading_from_response: dict) -> bool:
        if "kana" in reading_from_response and reading_from_response["kana"] == query:
            return True
        if "kanji" in reading_from_response and reading_from_response["kanji"] == query:
            return True
        return False
