import sublime
import sublime_plugin
import os
import re
import datetime as dt

time_format = "%H:%M"
project_delimiter = '$'
task_delimiter = '-'
description_delimiter = ':'
summary_heading = "--- Summary ---"
timestamp_format = "{0} {1} ".format(time_format, project_delimiter)
filepath = "~/timelogs"
file_format = "%Y-%m-%d"
levels = 3


class CreateTimelogCommand(sublime_plugin.WindowCommand):

    def run(self):
        # expand the path to timelogs and create it if it doesn't already exist
        fullpath = os.path.expanduser(filepath) if '~' in filepath else filepath
        filename_format = "{0}/{1}.timelog".format(fullpath, file_format)
        if not os.path.exists(fullpath):
            os.mkdir(fullpath)
        # create the new timelog, insert the first line and open it
        filename = dt.datetime.strftime(dt.datetime.now(), filename_format)
        with open(filename, "a") as f:
            top_line = "{0}".format(dt.datetime.strftime(dt.datetime.now(), timestamp_format))
            f.write(top_line)
        self.window.open_file(filename)


class StartTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        EndTimelogLineCommand.run(self, edit)
        region = self.view.line(self.view.sel()[0])
        line = self.view.substr(region)
        newline = dt.datetime.strftime(dt.datetime.now(), timestamp_format)
        print(line)
        if len(line) > 1:
            newline = "\n" + newline
        self.view.insert(edit, region.b, newline)


class EndTimelogLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = self.view.line(self.view.sel()[0])
        start_time = self.view.substr(region).split(project_delimiter)[0].strip()
        # if the time format doesn't match the specified one then don't parse this line
        try:
            dt.datetime.strptime(start_time, time_format)
        except ValueError:
            return
        end_time = dt.datetime.strftime(dt.datetime.now(), time_format)
        timelog_entry = "{0} -- {1}".format(start_time, end_time)
        region.b = region.a + len(time_format)
        self.view.replace(edit, region, timelog_entry)


class ParseTimelogCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window_vars = self.view.window().extract_variables()
        extension = window_vars.get('file_extension')
        if extension != "timelog":
            return
        filename = self.view.file_name()
        projects = self.get_time_dict(filename)
        summary = self.get_summary(projects)
        self.remove_trailing_newlines(edit)
        for s in self.view.sel():
            r = self.view.find(summary_heading, 0)
            if r.a is -1:
                self.view.insert(edit, self.view.size(), summary)
            else:
                r.b = self.view.size()
                print(self.view.find(summary_heading, 0))
                self.view.replace(edit, r, summary)

    def remove_trailing_newlines(self, edit):
        # this function shamelessy stolen from the Sublime Single Trailing Newline package
        # https://packagecontrol.io/packages/SingleTrailingNewLine
        # https://github.com/mattst/sublime-single-trailing-new-line
        last_sig_char = self.view.size() - 1
        while last_sig_char >= 0 and self.view.substr(last_sig_char).isspace():
            last_sig_char -= 1
        erase_region = sublime.Region(last_sig_char + 1, self.view.size())
        self.view.erase(edit, erase_region)
        self.view.insert(edit, self.view.size(), "\n\n")

    def get_time_dict(self, filename):
        projects = {}
        with open(filename, 'r') as f:
            for line in f:
                project, task, description = "none", "none", "none"
                split_line = line.split(project_delimiter)
                times = split_line[0].split("--")
                if len(times) <= 1:
                    continue
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
                    start_time = dt.datetime.strptime(times[0].strip(), time_format)
                    end_time = dt.datetime.strptime(times[1].strip(), time_format)
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
                    continue
        return projects

    def get_summary(self, projects):
        summary = summary_heading + "\n"
        summary_total = dt.timedelta()
        for project, tasks in projects.items():
            project_breakdown = ""
            project_total = dt.timedelta()
            for task, descriptions in tasks.items():
                task_breakdown = ""
                task_total = dt.timedelta()
                for description, description_time in descriptions.items():
                    task_breakdown += "\t\t{0}\t{1}\n".format(description, str(description_time))
                    task_total += description_time
                project_breakdown += "\t{0}\t{1}\n".format(task, task_total)
                project_breakdown += task_breakdown
                project_total += task_total
            summary += "{0}\t{1}\n".format(project, project_total)
            summary += project_breakdown
            summary_total += project_total
        summary += "Total Today: {0}".format(summary_total)
        return summary
