import os
import re

import sublime
import sublime_plugin


class PropertyType:
    Number, Bool, Text, Array, Map, Image = range(0, 6)

COLORS = [
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

BUILTIN_VARS = ['_index_', '_width_', 'config', 'state', '_data_', '_response_', '_prev_', '_next_']

BUNDLES = ["O2O.bundle/", "ALPPass.bundle/",
           "APCommonUI.bundle/", "O2OPurchase.bundle/"]

KEY_VALUES = {
    "sectioned": 'true',
    "native": PropertyType.Text,
    "reuse-identifier": PropertyType.Text,
    "identifier": PropertyType.Text,
    "controller": PropertyType.Text,
    "config": PropertyType.Map,
    "script": PropertyType.Text,
    "async-display": PropertyType.Bool,
    "state": PropertyType.Map,
    "template": PropertyType.Map,

    "layout": PropertyType.Map,
    "styles": PropertyType.Map,
    
    "style": PropertyType.Map,
    "class": PropertyType.Text,
    "type": ["node", "stack", "text", "image", "button", "scroll", "paging", "indicator", "line"],
    "direction": ["horizontal", "vertical", "horizontal-reverse", "vertical-reverse"],
    "flex-basis": ["auto", "content"],
    "flex-grow": PropertyType.Number,
    "flex-shrink": PropertyType.Number,
    "align-items": ["stretch", "start", "end", "center", "baseline"],
    "align-self": ["auto", "stretch", "start", "end", "center", "baseline"],
    "align-content": ["stretch", "start", "end", "center", "space-between", "space-around"],
    "justify-content": ["start", "end", "center", "space-between", "space-around"],
    "items-per-line": PropertyType.Number,
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
    "wrap": ['nowrap', 'wrap', 'wrap-reverse'],
    "gone": r'"\${$1}"',
    # "hidden": PropertyType.Bool,
    "clip": 'true',
    "user-interaction-enabled": 'false',
    "border-width": PropertyType.Number,
    "corner-radius": PropertyType.Number,
    "corner-radius-top-left": PropertyType.Number,
    "corner-radius-top-right": PropertyType.Number,
    "corner-radius-bottom-left": PropertyType.Number,
    "corner-radius-bottom-right": PropertyType.Number,
    "background-color": COLORS,
    "highlight-background-color": COLORS,
    "border-color": COLORS,
    "alpha": PropertyType.Number,
    "dash-length": PropertyType.Number,
    "space-length": PropertyType.Number,
    "repeat": PropertyType.Number,
    "vars": '{$1}',
    "ref": r'"\${$1}"',
    "view-class": PropertyType.Text,
    "exposure-log": PropertyType.Map,
    "tag": PropertyType.Number,
    "spm-tag": PropertyType.Text,
    "properties": PropertyType.Map,
    "async-display": 'true',
    "action": '{$1}',
    "display": '{$1}',
    "completion": PropertyType.Map,
    "log": PropertyType.Map,
    "update-state": PropertyType.Map,
    "on-tap": '{$1}',
    "on-display": '{$1}',
    "on-display-once": '{$1}',
    "on-complete": '{$1}',
    "on-create": '{$1}',
    "on-create-once": '{$1}',
    "on-switch": '{$1}',
    "updateState:": PropertyType.Map,
    "openUrl:": PropertyType.Number,
    "url": PropertyType.Text,
    "monitor": PropertyType.Text,
    "source": PropertyType.Text,
    "selector": PropertyType.Text,
    "condition": PropertyType.Text,
    "clickLog:": PropertyType.Map,
    "exposureLog:": PropertyType.Map,
    "seed": PropertyType.Text,
    "params": PropertyType.Array,
    "action-id": ["clicked", "exposure", "slided"],
    "children": '[\n\t{\n\t\t$1\n\t}\n]',
    'is-accessibility-element': 'true',
    'accessibility-label': PropertyType.Text,

    "text": PropertyType.Text,
    "html-text": PropertyType.Text,
    "kern": PropertyType.Number,
    "color": COLORS,
    "font-size": PropertyType.Number,
    "adjusts-font-size": 'true',
    "mini-scale-factor": PropertyType.Number,
    "baseline-adjustment": ["baseline", "center", "none"],
    "font-style": [
        "ultra-light",
        "thin",
        "light",
        "normal",
        "medium",
        "bold",
        "heavy",
        "black",
        "italic",
        "bold-italic"
    ],
    "font-name": PropertyType.Text,
    "alignment": ["natural", "justify", "left", "center", "right"],
    "vertical-alignment": ["top", "center", "bottom"],
    "truncation-mode": [
        "truncating-head",
        "truncating-middle",
        "truncating-tail",
        "clip",
        "none"
    ],
    "line-break-mode": [
        "word",
        "char",
    ],
    "lines": PropertyType.Number,

    "title": PropertyType.Text,
    "title-color": COLORS,
    "background-image": PropertyType.Image,
    "enlarge-size": PropertyType.Number,

    "normal": PropertyType.Text,
    "highlighted": PropertyType.Text,
    "disabled": PropertyType.Text,
    "selected": PropertyType.Text,

    "image": PropertyType.Image,
    "backing-view": PropertyType.Text,
    "image-url": PropertyType.Text,
    "error-image": PropertyType.Image,
    "download-scale": PropertyType.Number,
    "business": [
        "O2O_common",
        "O2O_home",
        "O2O_search",
        "O2O_detail",
        "O2O_detail_foodie",
        "O2O_detail_dish",
        "O2O_album_large",
        "O2O_album_small",
        "O2O_dish_large",
        "O2O_dish_small",
        "O2O_comment_large",
        "O2O_comment_small",
        "O2O_voucher"
    ],
    "content-mode": [
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
        "scale-to-fill",
        "scale-aspect-fit",
        "scale-aspect-fill"
    ],

    "paging": PropertyType.Bool,
    "scroll-enabled": 'false',
    "scroll-direction": ["none", "horizontal", "vertical", "both"],
    "animation-duration": PropertyType.Number,
    "infinite-loop": 'true',
    "auto-scroll": PropertyType.Number,
    "page-control": 'true',
    "page-control-color": COLORS,
    "page-control-selected-color": COLORS,
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
            line_start = view.find_by_class(
                point, False, sublime.CLASS_LINE_START)
            str_to_line_start = view.substr(sublime.Region(line_start + 1, point))
            quote_position = str_to_line_start.rfind('"')
            key = str_to_line_start[quote_position + 1:]
            if view.substr(point) == '"':
                line_end = view.find_by_class(
                    point, True, sublime.CLASS_LINE_END)
                point += 1
                str_to_line_end = view.substr(sublime.Region(point, line_end))
                match = re.search(r'^\S*:', str_to_line_end)
                if match:
                    return
                else:
                    view.insert(edit, point, ': ')
                    point += 2
            else:
                view.insert(edit, point, '": ')
                point += 3

            view.sel().clear()
            view.sel().add(sublime.Region(point, point))

            if key in KEY_VALUES:
                value = KEY_VALUES[key]
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
                elif value == PropertyType.Image:
                    snippet = '"$1"'

                if snippet is not None:
                    view.run_command('insert_snippet', {'contents': snippet})
        elif view.match_selector(point, "string.vzt"):
            if view.substr(point) == '"' and view.substr(point - 1) != '/':
                point += 1
                view.sel().clear()
                view.sel().add(sublime.Region(point, point))


class VZTemplateAutoComplete(sublime_plugin.EventListener):

    PROPERTY_NAME_REGEX = re.compile(r'"(?P<prop_name>[-a-z]+)"\s*:\s*$')
    IMAGE_REGEX = re.compile(r'([^/]+?)(@[23]x)?\.(png|jpg|gif)$')

    def find_root_path(self, path):
        folder = path if os.path.isdir(
            path) else os.path.dirname(os.path.realpath(path))
        while len(folder) > 1:
            if os.path.isdir(folder + '/.git'):
                return folder
            folder = os.path.dirname(folder)
        return None

    def is_xcode_project_dir(self, dir):
        return os.path.exists(dir + '/' + os.path.basename(dir) + '.xcodeproj')

    def get_xcode_projects(self, dir):
        projs = []
        for filename in os.listdir(dir):
            path = dir + '/' + filename
            if os.path.isdir(path) and self.is_xcode_project_dir(path):
                projs.append(path)
        return projs

    def get_images(self, view):
        path = view.file_name()
        if path is None:
            folders = view.window().folders()
            if len(folders) > 0:
                path = folders[0]
            else:
                return []

        root_path = self.find_root_path(path)

        if root_path is None:
            print('目录无效')
            return []

        proj_dirs = self.get_xcode_projects(root_path)
        if len(proj_dirs) == 0:
            print('找不到工程')
            return []

        images = []
        for proj in proj_dirs:
            bundle = os.path.basename(proj) + '.bundle/'
            res_dir = proj + '/Resources/' + bundle
            if not os.path.isdir(res_dir):
                continue
            for filename in os.listdir(res_dir):
                match = VZTemplateAutoComplete.IMAGE_REGEX.search(filename)
                if match:
                    image_name = match.group(1)
                    image_name = bundle + \
                        (image_name if match.group(3) == 'png' else match.group(0))
                    images.append(image_name)
        return list(set(images))

    def key_at_point(self, view, point):
        region = view.line(point)
        line = view.substr(region)[:point - region.begin() - 1]
        match = VZTemplateAutoComplete.PROPERTY_NAME_REGEX.search(line)
        if match is not None:
            return match.group('prop_name')
        return None

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(0, "source.vzt"):
            return

        sugs = []
        if view.match_selector(locations[0], "object.vzt"):
            sugs = [(p, '"' + p) for p in KEY_VALUES]
        elif view.match_selector(locations[0], "key.string.vzt"):
            sugs = [(p,) for p in KEY_VALUES]
        elif view.match_selector(locations[0], "string.vzt"):
            if view.match_selector(locations[0], "constant.other.expression.vzt"):
                return [(p,) for p in BUILTIN_VARS]
            else:
                key = self.key_at_point(view, locations[0] - len(prefix))
                if key is not None and key in KEY_VALUES:
                    value = KEY_VALUES[key]
                    if isinstance(value, list):
                        sugs = [(p,) for p in value]
                    elif value == PropertyType.Image:
                        sugs = [(p,) for p in self.get_images(view) + BUNDLES]
        elif view.match_selector(locations[0], "value.object.vzt"):
            pass

        return (sugs, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def on_selection_modified(self, view):
        if not view.match_selector(0, "source.vzt"):
            return

        for sel in view.sel():
            location = sel.end()
            if view.match_selector(location, "string.vzt"):
                if view.substr(location - 1) == '"':
                    key = self.key_at_point(view, location)
                    if key and key in KEY_VALUES:
                        value = KEY_VALUES[key]
                        if (isinstance(value, list) and len(value) > 1
                                or value == PropertyType.Image):
                            view.run_command('auto_complete')
            elif (not view.match_selector(location, "key.string.vzt") and
                  not view.match_selector(location, "object.vzt")):
                view.run_command('hide_auto_complete')

    def on_text_command(self, view, command_name, args):
        if not view.match_selector(0, "source.vzt"):
            return

        if command_name == 'left_delete' or command_name == 'right_delete':
            forward = command_name == 'right_delete'
            for sel in view.sel():
                point = sel.end()
                word_region = view.word(point)
                if view.match_selector(word_region.begin(), "constant.language.vzt"):
                    return ('delete_word', {'forward': forward})

    def on_post_text_command(self, view, command_name, args):
        if not view.match_selector(0, "source.vzt"):
            return

        if command_name == 'commit_completion':
            for sel in view.sel():
                location = sel.end()
                view.run_command('completion_committed', {'point': location})
