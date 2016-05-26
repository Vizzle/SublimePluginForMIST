import sublime, sublime_plugin, re

class PropertyType:
    Number, Bool, Text, Array, Map = range(0 ,5)

colors = [
    "black",
    "darkgray",
    "lightgray",
    "white",
    "gray",
    "red",
    "green",
    "blue",
    "cyan",
    "yellow",
    "magenta",
    "orange",
    "purple",
    "brown",
    "transparent"
]

key_values = {
    "sectioned": PropertyType.Bool,
    "native": PropertyType.Text,
    "controller": PropertyType.Text,
    "config": PropertyType.Map,
    "state": PropertyType.Map,
    "template": PropertyType.Map,

    "type": ["node", "stack", "text", "image", "button", "scroll", "paging"],
    "direction": ["horizontal", "vertical", "horizontal-reverse", "vertical-reverse"],
    "flex-basis": ["auto", "content"],
    "flex-grow": PropertyType.Number,
    "flex-shrink": PropertyType.Number,
    "align-items": ["stretch", "start", "end", "center"],
    "align-self": ["auto", "stretch", "start", "end", "center"],
    "align-content": ["stretch", "start", "end", "center", "space-between", "space-around"],
    "justify-content": ["start", "end", "center", "space-between", "space-around"],
    "width": ["auto"],
    "height": ["auto"],
    "min-width": PropertyType.Number,
    "min-height": PropertyType.Number,
    "max-width": PropertyType.Number,
    "max-height": PropertyType.Number,
    "margin": ["auto"],
    "margin-left": ["auto"],
    "margin-top": ["auto"],
    "margin-right": ["auto"],
    "margin-bottom": ["auto"],
    "padding": PropertyType.Number,
    "padding-left": PropertyType.Number,
    "padding-top": PropertyType.Number,
    "padding-right": PropertyType.Number,
    "padding-bottom": PropertyType.Number,
    "spacing": PropertyType.Number,
    "line-spacing": PropertyType.Number,
    "fixed": PropertyType.Bool,
    "wrap": PropertyType.Bool,
    "gone": PropertyType.Bool,
    "hidden": PropertyType.Bool,
    "clip": PropertyType.Bool,
    "user-interaction-enabled": PropertyType.Bool,
    "border-width": PropertyType.Number,
    "corner-radius": PropertyType.Number,
    "background-color": colors,
    "border-color": colors,
    "repeat": PropertyType.Number,
    "vars": PropertyType.Map,
    "open-page-log": PropertyType.Map,
    "action": PropertyType.Map,
    "completion": PropertyType.Map,
    "log": PropertyType.Map,
    "update-state": PropertyType.Map,
    "url": PropertyType.Text,
    "monitor": PropertyType.Text,
    "source": PropertyType.Text,
    "selector": PropertyType.Text,
    "condition": PropertyType.Text,
    "id": PropertyType.Text,
    "seed": PropertyType.Text,
    "params": PropertyType.Array,
    "action": ["clicked", "openPage"],
    "children": ('children []', '"children": [\n\t\\{\n\t\t$0\n\t\\}\n]'),

    "text": PropertyType.Text,
    "color": colors,
    "font-size": PropertyType.Number,
    "font-style": ["normal", "bold", "italic", "bold-italic"],
    "font-name": PropertyType.Text,
    "alignment": ["natural", "justify", "left", "center", "right"],
    "line-break-mode": ["word", "char", "clip", "truncating-head", "truncating-middle", "truncating-tail"],
    "lines": PropertyType.Number,

    "image": PropertyType.Text,
    "image-url": PropertyType.Text,
    "error-image": PropertyType.Text,
    "content-mode": ["center", "scale-to-fill", "scale-aspect-fit", "scale-aspect-fill"],

    "paging": PropertyType.Bool,
    "scroll-enabled": PropertyType.Bool,
    "scroll-direction": ["none", "horizontal", "vertical", "both"],

    "infinite-loop": PropertyType.Bool,
    "auto-scroll": PropertyType.Number,
    "page-control": PropertyType.Bool,
    "page-control-color": colors,
    "page-control-selected-color": colors,
    "page-control-scale": PropertyType.Number,
    "page-control-margin-left": PropertyType.Number,
    "page-control-margin-right": PropertyType.Number,
    "page-control-margin-top": PropertyType.Number,
    "page-control-margin-bottom": PropertyType.Number,
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
            else:
                view.insert(edit, point, '": ')
                point += 3

            if key in key_values and (key_values[key] == PropertyType.Text or len(key_values[key]) > 1):
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
            sugs = [key_values[p] if isinstance(key_values[p], tuple) else ('%s {}' % p, '"%s": \\{\n\t$0\n\\}' % p) if key_values[p] == PropertyType.Map else ('%s []' % p, '"%s": [ $0 ]' % p) if key_values[p] == PropertyType.Array else (p, '"' + p) for p in key_values]
        elif view.match_selector(locations[0], "key.string.vzt"):
            sugs = [(p,) for p in key_values]
        elif view.match_selector(locations[0], "string.vzt"):
            key = self.keyAtPoint(view, locations[0]-len(prefix))
            if key is not None and key in key_values:
                values = key_values[key]
                if isinstance(values, list):
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
                    if key is not None and key in key_values and isinstance(key_values[key], list) and len(key_values[key]) > 1:
                        view.run_command('auto_complete')
            elif not view.match_selector(location, "key.string.vzt") and not view.match_selector(location, "object.vzt"):
                view.run_command('hide_auto_complete')

    def on_post_text_command(self, view, command_name, args):
        if command_name == 'commit_completion':
            for s in view.sel():
                location = s.end()
                view.run_command('completion_committed', {'point': location})
