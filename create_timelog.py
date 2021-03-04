import sublime
import sublime_plugin
import os
import time

time_format = "%H:%m"
delimiter = '$'
timestamp_format = "{0} {1} ".format(time_format, delimiter)


class CreateTimelogCommand(sublime_plugin.WindowCommand):
    home = os.path.expanduser("~")
    filename_format = home + "/%Y-%m-%d.timelog"

    def run(self):
        filename = time.strftime(self.filename_format)
        with open(filename, "a") as f:
            f.write(time.strftime(timestamp_format))
        self.window.open_file(filename)


class AddTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert("\n" + time.strftime(self.time_format))


class ParseTimelogCommand(sublime_plugin.WindowCommand):
    def run(self):
        window_vars = self.window.extract_variables()
        extension = window_vars.get('file_extension')
        active_view = self.window.active_view()
        # if extension is "timelog":
        with open(active_view.file_name()) as f:
            for line in f:
                split_line = line.split(delimiter)
                print(split_line[0])
                try:
                    new_timestamp = time.strptime(split_line[0].strip(), time_format)
                    print(new_timestamp)

                except ValueError:
                    pass
