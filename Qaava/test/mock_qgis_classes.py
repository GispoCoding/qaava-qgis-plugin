from qgis.core import Qgis


class MockMessageBar:

    def __init__(self):
        self.messages = {Qgis.Info: [], Qgis.Warning: [], Qgis.Critical: []}

    def get_messages(self, level):
        """Used to test which messages have been logged"""
        return self.messages[level]

    def pushMessage(self, title, text, level, duration):
        msg = f"{title}:{text}"
        self.messages[level].append(msg)


class MainWindow:

    def blockSignals(self, *args):
        pass
