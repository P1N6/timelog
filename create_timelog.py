import sublime
import sublime_plugin
import os
import time


class CreateTimelogCommand(sublime_plugin.WindowCommand):
    home = os.path.expanduser("~")
    filepath = home + "/timelog.txt"
    date_format = "%Y-%m-%d.timelog"
    time_format = "%H:%m"

    def run(self):
        with open(time.strftime(self.date_format), "a") as f:
            f.write(time.strftime(self.time_format))
        self.window.open_file(self.filepath)


class AddTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(time.strftime(self.time_format))
