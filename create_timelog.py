import sublime
import sublime_plugin
import os
import time

time_format = "%H:%M"
delimiter = '$'
timestamp_format = "{0} {1} ".format(time_format, delimiter)
check_in = "check in --"
check_out = "-- check out --"


class CreateTimelogCommand(sublime_plugin.WindowCommand):
    home = os.path.expanduser("~")
    filename_format = home + "/%Y-%m-%d.timelog"

    def run(self):
        filename = time.strftime(self.filename_format)
        with open(filename, "a") as f:
            top_line = "{0}\n{1}".format(check_in, time.strftime(timestamp_format))
            f.write(top_line)
        self.window.open_file(filename)


class StartTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert("\n" + time.strftime(self.time_format))


class EndTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        split_line = self.view.substr(self.view.line(self.view.sel()[0])).split(delimiter)
        start_time = split_line[0].strip()
        try:
            time.strptime(start_time, time_format)
        except ValueError:
            return
        end_time = time.strftime(time_format)
        timelog_entry = "{0} -- {1}".format(start_time, end_time)
        region = self.view.line(self.view.sel()[0])
        region.b = region.a + len(time_format)
        self.view.replace(edit, region, timelog_entry)


class ParseTimelogCommand(sublime_plugin.WindowCommand):
    def run(self):
        window_vars = self.window.extract_variables()
        extension = window_vars.get('file_extension')
        active_view = self.window.active_view()
        # if extension is "timelog":
        with open(active_view.file_name()) as f:
            old_timestamp = ""
            for line in f:
                split_line = line.split(delimiter)
                print(split_line[0])
                try:

                    new_timestamp = time.strptime(split_line[0].strip(), time_format)
                    print(new_timestamp)

                except ValueError:
                    if line is check_out:
                        break
                    else:
                        pass
