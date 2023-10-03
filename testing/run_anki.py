from anki_testing import anki_running
from jp_helper import init_jp_helper

with anki_running() as app:

    # Initialize our addon
    init_jp_helper()

    # Run anki
    app.exec()
