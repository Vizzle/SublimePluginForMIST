import sublime, sublime_plugin, re, os
from .StatusBar import StatusBar

properties = [
    ("type",),
    ("flex-basis",),
    ("flex-grow",),
    ("flex-shrink",),
    ("direction",),
    ("align-items",),
    ("align-self",),
    ("align-content",),
    ("justify-content",),
    ("width",),
    ("height",),
    ("min-width",),
    ("min-height",),
    ("max-width",),
    ("max-height",),
    ("margin",),
    ("margin-left",),
    ("margin-top",),
    ("margin-right",),
    ("margin-bottom",),
    ("padding",),
    ("padding-left",),
    ("padding-top",),
    ("padding-right",),
    ("padding-bottom",),
    ("spacing",),
    ("line-spacing",),
    ("fixed",),
    ("wrap",),
    ("gone",),
    ("hidden",),
    ("clip",),
    ("user-interaction-enabled",),
    ("border-width",),
    ("border-color",),
    ("corner-radius",),
    ("background-color",),
    ("repeat",),

    ("text",),
    ("color",),
    ("font-size",),
    ("font-name",),
    ("font-style",),
    ("alignment",),
    ("line-break-mode",),
    ("lines",),

    ("image",),
    ("image-url",),
    ("error-image",),
    ("content-mode",),

    ("paging",),
    ("scroll-enabled",),
    ("scroll-direction",),

    ("infinite-loop",),
    ("auto-scroll",),
    ("page-control",),
    ("page-control-color",),
    ("page-control-selected-color",),
    ("page-control-margin-left",),
    ("page-control-margin-right",),
    ("page-control-margin-top",),
    ("page-control-margin-bottom",),
    ("page-control-scale",),

    ("sectioned",),
    ("native",),
    ("controller",),

    ("url",),
    ("selector",),
    ("condition",),

    ("id",),
    ("seed",),
    ("params",),
]

colors = [
    "black",
    "gray",
    "white",
    "red",
    "green",
    "yellow",
    "blue",
    "lightGray",
    "darkGray",
    "cyan",
    "magenta",
    "purple",
    "brown",
    "orange",
    "transparent"
]

key_values = {
    "direction": ["horizontal", "vertical", "horizontal-reverse", "vertical-reverse"],
    "flex-basis": ["auto"],
    "align-items": ["stretch", "start", "end", "center"],
    "align-self": ["auto", "stretch", "start", "end", "center"],
    "align-content": ["stretch", "start", "end", "center", "space-between", "space-around"],
    "justify-content": ["start", "end", "center", "space-between", "space-around"],
    "type": ["node", "stack", "text", "image", "button", "scroll", "paging"],
    "width": ["auto"],
    "height": ["auto"],
    "margin": ["auto"],
    "margin-left": ["auto"],
    "margin-top": ["auto"],
    "margin-right": ["auto"],
    "margin-bottom": ["auto"],
    "background-color": colors,
    "border-color": colors,
    "color": colors,
    "page-control-color": colors,
    "page-control-selected-color": colors,
    "alignment": ["natural", "justify", "left", "center", "right"],
    "line-break-mode": ["word", "char", "clip", "truncating-head", "truncating-middle", "truncating-tail"],
    "content-mode": ["center", "scale-to-fill", "scale-aspect-fit", "scale-aspect-fill"],
    "font-style": ["normal", "bold", "italic", "bold-italic"],
    "scroll-direction": ["none", "horizontal", "vertical", "both"]
}

class MistMoveCaretCommand(sublime_plugin.TextCommand):
    def run(self, edit, point):
        self.point = point
        view = self.view
        if (view.is_loading()):
            sublime.set_timeout_async(lambda:view.run_command('mist_move_caret', {'point': point}), 50)
            return
        view.sel().clear()
        view.sel().add(sublime.Region(point, point))
        sublime.set_timeout_async(lambda:view.show(point), 50)

class MistSwitchCommand(sublime_plugin.TextCommand):
    def run(self, edit, is_list = False):
        self.folder, file = os.path.split(self.view.file_name())
        fileName, fileExt = os.path.splitext(file)

        if fileExt == '.html':
            if self.view.find(r'"template"\s*:\s*\{', 0).begin() < 0:
                StatusBar.set(self.view, 'this is not a valid MIST template file!')
                return
            files = []
            for (_, _, filenames) in os.walk(self.folder):
                files.extend(filenames)
                break

            self.results = []

            for file in files:
                if os.path.splitext(file)[1] != '.json':
                    continue

                path = os.path.join(self.folder, file)
                with open(path, 'rb') as f:
                    s = f.read().decode('utf-8')
                    i = 1
                    for result in re.finditer('"blockId"\\s*:\\s*"KOUBEI@%s"' % fileName, s):
                        self.results.append((file,result.start(), "%s #%d" % (file, i) if i > 1 else file))
                        i += 1

            if len(self.results) == 0:
                StatusBar.set(self.view, 'there is no reference of template "%s"' % fileName)
            elif not is_list and len(self.results) == 1:
                self.switchTo(0)
            else:
                self.view.window().show_quick_panel([r[2] for r in self.results], self.switchTo)
        elif fileExt == '.json':
            length = self.view.size()
            s = self.view.substr(sublime.Region(0, length))
            if not is_list:
                pos = self.view.sel()[0].b
                left = []
                right = []
                i = pos-1
                j = 0
                while i >= 0:
                    c = s[i]
                    if c == '{':
                        if j == 0:
                            left.insert(0, i)
                        else:
                            j -= 1
                    elif c == '}':
                        j += 1
                    i -= 1
                i = pos
                j = 0
                while i < length:
                    c = s[i]
                    if c == '}':
                        if j == 0:
                            right.insert(0, i+1)
                        else:
                            j -= 1
                    elif c == '{':
                        j += 1
                    i += 1
                while len(right) < len(left):
                    right.insert(0, length)

                if len(left) >= 2:
                    result = re.search(r'"blockId"\s*:\s*"KOUBEI@([^"\n]*)"', s[left[1]:right[1]])
                    if result is not None:
                        blockId = result.group(1)
                        self.results = [(blockId + '.html',)]
                        self.switchTo(0)
                        return

            self.results = []
            for result in re.finditer(r'"blockId"\s*:\s*"KOUBEI@([^"\n]*)"', s):
                r = result.group(1)
                if r not in self.results:
                    self.results.append((r + '.html',))

            if len(self.results) == 0:
                StatusBar.set(self.view, 'can not find any blockId')
            elif not is_list and len(self.results) == 1:
                self.switchTo(0)
            else:
                self.view.window().show_quick_panel([r[0] for r in self.results], self.switchTo)
        else:
            StatusBar.set(self.view, 'this is not a valid MIST template file or data file!')

    def switchTo(self, index):
        if index >= 0:
            result = self.results[index]
            window = self.view.window()
            window.run_command('open_file', {"file":os.path.join(self.folder, result[0])})
            if len(result) > 1:
                view = window.active_view()
                view.run_command('mist_move_caret', {'point': result[1]})

class CompletionCommittedCommand(sublime_plugin.TextCommand):
    def run(self, edit, point):
        view = self.view
        if view.match_selector(point, "key.string.vzt"):
            lineStart = view.find_by_class(point, False, sublime.CLASS_LINE_START)
            strToLineStart = view.substr(sublime.Region(lineStart + 1, point))
            quotePosition = strToLineStart.rfind('"')
            key = strToLineStart[quotePosition+1:]
            if view.substr(point) == '"':
                lineEnd = view.find_by_class(point, True, sublime.CLASS_LINE_END)
                point += 1
                strToLineEnd = view.substr(sublime.Region(point, lineEnd))
                r = re.search(r'^\S*:', strToLineEnd)
                if r is None:
                    view.insert(edit, point, ': ')
                    point += 2
                else:
                    return
            else:
                view.insert(edit, point, '": ')
                point += 3

            if key in key_values and len(key_values[key]) > 1:
                view.insert(edit, point, '""')
                point += 1
            view.sel().clear()
            view.sel().add(sublime.Region(point, point))
        elif view.match_selector(point, "string.vzt"):
            if view.substr(point) == '"':
                point += 1
                view.sel().clear()
                view.sel().add(sublime.Region(point, point))

property_name_regex = re.compile(r'"(?P<prop_name>[-a-z]+)"\s*:\s*$')

class VZTemplateAutoComplete(sublime_plugin.EventListener):
    def keyAtPoint(self, view, point):
        r = view.line(point)
        line = view.substr(r)[:point-r.begin()-1]
        match = property_name_regex.search(line)
        if match is not None:
            return match.group('prop_name')
        return None

    def on_query_completions(self, view, prefix, locations):
        sugs = []
        if view.match_selector(locations[0], "object.vzt"):
            sugs = [('children []', '"children": [\n\t\\{\n\t\t$0\n\t\\}\n]')] + [('config {}', '"config": \\{\n\t$0\n\\}')] + [('state {}', '"state": \\{\n\t$0\n\\}')] + [('update-state {}', '"update-state": \\{\n\t$0\n\\}')] + [('action {}', '"action": \\{\n\t$0\n\\}')] + [('template {}', '"template": \\{\n\t$0\n\\}')] + [('completion {}', '"completion": \\{\n\t$0\n\\}')] + [('log {}', '"log": \\{\n\t$0\n\\}')] + [('open-page-log {}', '"open-page-log": \\{\n\t$0\n\\}')] + [('vars {}', '"vars": \\{\n\t$0\n\\}')] + [(p[0], '"' + p[0]) for p in properties]
        elif view.match_selector(locations[0], "key.string.vzt"):
            sugs = [("children",)] + [("config",)] + [("state",)] + [("update-state",)] + [("action",)] + [("template",)] + [("completion",)] + [("log",)] + [("open-page-log",)] + properties
        elif view.match_selector(locations[0], "string.vzt"):
            key = self.keyAtPoint(view, locations[0]-len(prefix))
            if key is not None and key in key_values:
                values = key_values[key]
                sugs = [(p,) for p in values]
        elif view.match_selector(locations[0], "value.object.vzt"):
            sugs = []

        return (sugs, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def on_selection_modified(self, view):
        for s in view.sel():
            location = s.end()
            if view.match_selector(location, "string.vzt"):
                if view.substr(location-1) == '"':
                    key = self.keyAtPoint(view, location)
                    if key is not None and key in key_values and len(key_values[key]) > 1:
                        view.run_command('auto_complete')
            elif not view.match_selector(location, "key.string.vzt") and not view.match_selector(location, "object.vzt"):
                view.run_command('hide_auto_complete')

    def on_post_text_command(self, view, command_name, args):
        if command_name == 'commit_completion':
            for s in view.sel():
                location = s.end()
                view.run_command('completion_committed', {'point': location})
                
