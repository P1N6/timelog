import sublime
import sublime_plugin
import os
from datetime import datetime, timedelta

time_format = "%H:%M"
project_delimiter = '$'
task_delimiter = '-'
description_delimiter = ':'
timestamp_format = "{0} {1} ".format(time_format, project_delimiter)
levels = 3
check_in = "check in --"
check_out = "-- check out --"


class CreateTimelogCommand(sublime_plugin.WindowCommand):
    home = os.path.expanduser("~")
    filename_format = home + "/%Y-%m-%d.timelog"

    def run(self):
        filename = datetime.strftime(self.filename_format)
        with open(filename, "a") as f:
            top_line = "{0}\n{1}".format(check_in, datetime.strftime(timestamp_format))
            f.write(top_line)
        self.window.open_file(filename)


class StartTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert("\n" + datetime.strftime(time_format))


class EndTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = self.view.line(self.view.sel()[0])
        start_time = self.view.substr(region).split(project_delimiter)[0].strip()
        # if the time format doesn't match the specified one then don't parse this line
        try:
            datetime.strptime(start_time, time_format)
        except ValueError:
            return
        end_time = datetime.strftime(time_format)
        timelog_entry = "{0} -- {1}".format(start_time, end_time)
        region.b = region.a + len(time_format)
        self.view.replace(edit, region, timelog_entry)


class ParseTimelogCommand(sublime_plugin.WindowCommand):
    def run(self):
        window_vars = self.window.extract_variables()
        extension = window_vars.get('file_extension')
        if extension != "timelog":
            print(extension)
            return
        filename = self.window.active_view().file_name()
        projects = self.get_time_dict(filename)
        summary = self.get_summary(projects)

    def get_time_dict(self, filename):
        projects = {}
        with open(filename, 'r') as f:
            for line in f:
                project, task, description = "none", "none", "none"
                split_line = line.split(project_delimiter)
                times = split_line[0].split("--")
                if len(split_line) > 1:
                    if description_delimiter in split_line[1]:
                        description = split_line[1].split(description_delimiter)[1].strip()
                        if task_delimiter not in split_line[1]:
                            project = split_line[1].split(description_delimiter)[0].strip()
                    if task_delimiter in split_line[1]:
                        project = split_line[1].split(task_delimiter)[0].strip()
                        task = split_line[1].split(task_delimiter)[1].strip()
                        if description_delimiter in split_line[1]:
                            task = task.split(description_delimiter)[0].strip()
                    if task_delimiter not in split_line[1] and description_delimiter not in split_line[1]:
                        description = split_line[1].strip()
                try:
                    start_time = datetime.strptime(times[0].strip(), time_format)
                    end_time = datetime.strptime(times[1].strip(), time_format)
                    delta = end_time - start_time
                    if project not in projects:
                        projects[project] = {task: {description: delta}}
                    elif task not in projects[project]:
                        projects[project][task] = {description: delta}
                    elif description not in projects[project][task]:
                        projects[project][task][description] = delta
                    else:
                        projects[project][task][description] += delta
                except ValueError:
                    pass
        return projects

    def get_summary(self, projects):
        for project, tasks in projects.items():
            print(project)
            for task, descriptions in tasks.items():
                print("\t" + task)
                for description, time in descriptions.items():
                    print("\t\t" + description + "\t" + str(time))
                    pass
        return "hello"
