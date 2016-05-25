import time, threading

class StatusBar:
    timer = None
    tag = "mist"

    @staticmethod
    def set(view, msg, time = 3):
        if StatusBar.timer:
            StatusBar.timer.cancel()
        StatusBar.view = view;
        StatusBar.view.set_status(StatusBar.tag, msg)
        StatusBar.timer = threading.Timer(time, StatusBar.clear)
        StatusBar.timer.start()

    @staticmethod
    def clear():
        StatusBar.view.erase_status(StatusBar.tag)
