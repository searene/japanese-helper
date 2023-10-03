#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from anki.hooks import addHook
from aqt.editor import Editor

from .window import JapaneseHelperDialog


def on_jp_sound(editor: Editor):
    dialog = JapaneseHelperDialog(editor, editor.parentWindow)
    dialog.exec()
    # editor.web.eval("document.execCommand('insertHTML', false, 'abc')")


def add_jp_sound_button(buttons: [str], editor: Editor):
    editor._links['jp-sound'] = on_jp_sound
    # Get path to the current script
    audio_icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res', 'audio.png')
    return buttons + [editor._addButton(
        audio_icon_path,
        "jp-sound",  # link name
        "Get Japanese sound")]


def init_jp_helper():
    addHook("setupEditorButtons", add_jp_sound_button)