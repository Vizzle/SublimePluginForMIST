import sublime, sublime_plugin
import re

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
    ("scroll",),
    ("scroll-direction",),
    ("loop",),
    ("auto-scroll",),
    ("auto-scroll-time",),
    ("auto-scroll-animated",),
    ("page-controll",),
    ("page-controll-color",),
    ("page-controll-selected-color",),
    ("page-controll-height",),
    ("page-controll-scale",),

    ("template",),
    ("sectioned",),
    ("native",),
    ("controller",),

    ("url",),
    ("log",),
    ("selector",),
    ("template",),

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
    "type": ["node", "stack", "text", "image", "button", "O2OPagingNode"],
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
    "alignment": ["natural", "justify", "left", "center", "right"],
    "line-break-mode": ["word", "char", "clip", "truncating-head", "truncating-middle", "truncating-tail"],
    "content-mode": ["center", "scale-to-fill", "scale-aspect-fit", "scale-aspect-fill"],
    "font-style": ["normal", "bold", "italic", "bold-italic"],
    "scroll-direction": ["horizontal", "vertical"]
}

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
                    # view.insert(edit, point + r.endpos, ' ')
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
            sugs = [('children []', '"children": [\n\t\\{\n\t\t$0\n\t\\}\n]')] + [('config {}', '"config": \\{\n\t$0\n\\}')] + [('state {}', '"state": \\{\n\t$0\n\\}')] + [('update-state {}', '"update-state": \\{\n\t$0\n\\}')] + [('action {}', '"action": \\{\n\t$0\n\\}')] + [('log {}', '"log": \\{\n\t$0\n\\}')] + [('open-page-log {}', '"open-page-log": \\{\n\t$0\n\\}')] + [(p[0], '"' + p[0]) for p in properties]
        elif view.match_selector(locations[0], "key.string.vzt"):
            sugs = [("children",)] + [("config",)] + [("state",)] + [("update-state",)] + [("action",)] + [("log",)] + [("open-page-log",)] + properties
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
                
