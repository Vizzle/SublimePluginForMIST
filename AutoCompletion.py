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

image_snippet = ["O2O.bundle/", "ALPPass.bundle/", "APCommonUI.bundle/"] #'${1/([^$].*)|(.*)/(?1:"O2O.bundle\/:")/}${1:name}"'

key_values = {
    "sectioned": 'true',
    "native": PropertyType.Text,
    "controller": PropertyType.Text,
    "config": PropertyType.Map,
    "state": PropertyType.Map,
    "template": PropertyType.Map,

    "type": ["node", "stack", "text", "image", "button", "scroll", "paging", "indicator", "line"],
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
    "fixed": 'true',
    "wrap": 'true',
    "gone": '"\${$1}"',
    # "hidden": PropertyType.Bool,
    "clip": 'true',
    "user-interaction-enabled": 'false',
    "border-width": PropertyType.Number,
    "corner-radius": PropertyType.Number,
    "corner-radius-top-left": PropertyType.Number,
    "corner-radius-top-right": PropertyType.Number,
    "corner-radius-bottom-left": PropertyType.Number,
    "corner-radius-bottom-right": PropertyType.Number,
    "background-color": colors,
    "highlight-background-color": colors,
    "border-color": colors,
    "dash-length": PropertyType.Number,
    "space-length": PropertyType.Number,
    "repeat": PropertyType.Number,
    "vars": '{$1}',
    "ref": '"\${$1}"',
    "view-class": PropertyType.Text,
    "exposure-log": PropertyType.Map,
    "tag": PropertyType.Text,
    "spm-tag": PropertyType.Text,
    "async-display": 'true',
    "action": '{$1}',
    "completion": PropertyType.Map,
    "log": PropertyType.Map,
    "update-state": PropertyType.Map,
    "url": PropertyType.Text,
    "monitor": PropertyType.Text,
    "source": PropertyType.Text,
    "selector": PropertyType.Text,
    "condition": PropertyType.Text,
    "seed": PropertyType.Text,
    "params": PropertyType.Array,
    "action-id": ["clicked", "exposure", "slided"],
    "children": '[\n\t{\n\t\t$1\n\t}\n]',
    'is-accessibility-element': 'true',
    'accessibility-label': PropertyType.Text,

    "include": PropertyType.Text,

    "text": PropertyType.Text,
    "html-text": PropertyType.Text,
    "color": colors,
    "font-size": PropertyType.Number,
    "font-style": ["ultra-light", "thin", "light", "normal", "medium", "bold", "heavy", "black", "italic", "bold-italic"],
    "font-name": PropertyType.Text,
    "alignment": ["natural", "justify", "left", "center", "right"],
    "line-break-mode": ["word", "char", "clip", "truncating-head", "truncating-middle", "truncating-tail"],
    "lines": PropertyType.Number,

    "title": PropertyType.Text,
    "title-color": colors,
    "background-image": image_snippet,
    "enlarge-size": PropertyType.Number,

    "normal": PropertyType.Text,
    "highlighted": PropertyType.Text,
    "disabled": PropertyType.Text,
    "selected": PropertyType.Text,

    "image": image_snippet,
    "image-url": PropertyType.Text,
    "error-image": image_snippet,
    "download-scale": PropertyType.Number,
    "business": ["O2O_common", "O2O_home", "O2O_search", "O2O_detail", "O2O_detail_foodie", "O2O_detail_dish", "O2O_album_large", "O2O_album_small", "O2O_dish_large", "O2O_dish_small", "O2O_comment_large", "O2O_comment_small", "O2O_voucher"],
    "content-mode": ["center", "top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right", "scale-to-fill", "scale-aspect-fit", "scale-aspect-fill"],

    "paging": PropertyType.Bool,
    "scroll-enabled": 'false',
    "scroll-direction": ["none", "horizontal", "vertical", "both"],

    "infinite-loop": 'true',
    "auto-scroll": PropertyType.Number,
    "page-control": 'true',
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

            view.sel().clear()
            view.sel().add(sublime.Region(point, point))

            if key in key_values:
                value = key_values[key]
                snippet = None
                if isinstance(value, tuple) and len(value) >= 2:
                    snippet = value[1]
                elif isinstance(value, str):
                    snippet = value
                elif value == PropertyType.Map:
                    snippet = '{\n\t$1\n}'
                elif value == PropertyType.Array:
                    snippet = '[$1]'
                elif value == PropertyType.Text or isinstance(value, list) and len(value) > 1:
                    snippet = '"$1"'

                if snippet is not None:
                    view.run_command('insert_snippet', { 'contents': snippet })
        elif view.match_selector(point, "string.vzt"):
            if view.substr(point) == '"' and view.substr(point-1) != '/':
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
        if not view.match_selector(0, "source.vzt"):
            return

        sugs = []
        if view.match_selector(locations[0], "object.vzt"):
            sugs = [(p, '"' + p) for p in key_values]
        elif view.match_selector(locations[0], "key.string.vzt"):
            sugs = [(p,) for p in key_values]
        elif view.match_selector(locations[0], "string.vzt"):
            if view.match_selector(locations[0], "constant.other.expression.vzt"):
                return [(p,) for p in ['_index_', '_width_', 'config', 'state', '_data_', '_response_', '_prev_', '_next_']]
            else:
                key = self.keyAtPoint(view, locations[0]-len(prefix))
                if key is not None and key in key_values:
                    value = key_values[key]
                    if isinstance(value, list):
                        sugs = [(p,) for p in value]
        elif view.match_selector(locations[0], "value.object.vzt"):
            pass

        return (sugs, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def on_selection_modified(self, view):
        if not view.match_selector(0, "source.vzt"):
            return

        for s in view.sel():
            location = s.end()
            if view.match_selector(location, "string.vzt"):
                if view.substr(location-1) == '"':
                    key = self.keyAtPoint(view, location)
                    if key is not None and key in key_values and isinstance(key_values[key], list) and len(key_values[key]) > 1:
                        view.run_command('auto_complete')
            elif not view.match_selector(location, "key.string.vzt") and not view.match_selector(location, "object.vzt"):
                view.run_command('hide_auto_complete')

    def on_text_command(self, view, command_name, args):
        if not view.match_selector(0, "source.vzt"):
            return

        if command_name == 'left_delete' or command_name == 'right_delete':
            forward = command_name == 'right_delete'
            for s in view.sel():
                point = s.end()
                word_region = view.word(point)
                if view.match_selector(word_region.begin(), "constant.language.vzt"):
                    return ('delete_word', { 'forward': forward })

    def on_post_text_command(self, view, command_name, args):
        if not view.match_selector(0, "source.vzt"):
            return

        if command_name == 'commit_completion':
            for s in view.sel():
                location = s.end()
                view.run_command('completion_committed', {'point': location})
