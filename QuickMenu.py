import itertools
import os
import re

import sublime
import sublime_plugin

from .StatusBar import StatusBar


class MistMoveCaretCommand(sublime_plugin.TextCommand):

    def run(self, edit, point):
        view = self.view
        if view.is_loading():
            sublime.set_timeout_async(lambda: view.run_command(
                'mist_move_caret', {'point': point}), 50)
            return
        view.sel().clear()
        view.sel().add(sublime.Region(point, point))
        sublime.set_timeout_async(lambda: view.show(point), 50)


class QuickMenuItem:

    def __init__(self, title, callback):
        self.title = title
        self.callback = callback


class MistOpenQuickMenuCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        super().__init__(view)
        self._content = None
        self.file = None
        self.folder = None
        self.file_name = None
        self.file_ext = None

    @property
    def content(self):
        if self._content is None:
            self._content = self.view.substr(
                sublime.Region(0, self.view.size()))
        return self._content

    def run(self, edit):
        self.file = self.view.file_name()
        if self.file is None:
            sublime.message_dialog("请先保存到文件")
            return
        self.folder, _file = os.path.split(self.file)
        self.file_name, self.file_ext = os.path.splitext(_file)

        commands = []

        if self.file_ext == '.mist':
            commands.append(QuickMenuItem(
                "Jump to Data File", self.jump_to_data_file))
            commands.append(QuickMenuItem(
                "Jump to JS File", self.jump_to_js_file))
            commands.append(QuickMenuItem(
                "Format (Pretty Print)", self.callback))

        if self.file_ext == '.json':
            commands.append(QuickMenuItem(
                "Jump to Template File", self.jump_to_template_file))
            commands.append(QuickMenuItem(
                "List All Blocks", self.list_all_blocks))

        if self.file_ext == '.js':
            commands.append(QuickMenuItem(
                "Jump to Template File", self.jump_to_template_file))

        if len(commands) > 0:
            self.view.window().show_quick_panel(
                [c.title for c in commands], lambda i: commands[i].callback() if i >= 0 else None)

    def callback(self):
        sublime.message_dialog("对不起，功能暂未实现～")

    def jump_to_data_file(self):
        files = []
        for (_, _, filenames) in os.walk(self.folder):
            files.extend(filenames)
            break

        results = []

        for filename in files:
            if os.path.splitext(filename)[1] != '.json':
                continue

            path = os.path.join(self.folder, filename)
            with open(path, 'rb') as the_file:
                text = the_file.read().decode('utf-8')
                i = 1
                for result in re.finditer('"blockId"\\s*:\\s*"KOUBEI@%s"' % self.file_name, text):
                    results.append((filename, result.start(), "%s #%d" %
                                    (filename, i) if i > 1 else filename))
                    i += 1

        jump_to_index = lambda i: self.jump_to_file(
            results[i][0], results[i][1]) if i >= 0 else None

        if len(results) == 0:
            StatusBar.set(self.view, "未找到使用模版 '%s' 的数据文件" % self.file_name)
        elif len(results) == 1:
            jump_to_index(0)
        else:
            self.view.window().show_quick_panel(
                [r[2] for r in results], jump_to_index)

    def jump_to_template_file(self):
        if self.file_ext == '.js':
            file_name = self.file_name
            if file_name.endswith("_js"):
                file_name = file_name[:-3]
            self.jump_to_file(file_name + ".mist")
            return
        else:
            block = self.block_id_at_caret()
            if block:
                self.jump_to_file(block + ".mist")
            else:
                StatusBar.set(self.view, '请确保光标在block区块内')

    def list_all_blocks(self):
        blocks = self.get_all_blocks()
        names = ["%s #%d" % (b["id"], b["index"]) if "index" in b else b[
            "id"] for b in blocks]
        self.view.window().show_quick_panel(names, lambda i: self.view.run_command(
            'mist_move_caret', {'point': blocks[i]["point"]}) if i >= 0 else None)

    def jump_to_js_file(self):
        file_name = None
        match = re.search(r'"script-name"\s*:\s*"([^"\n]*)"', self.content)
        if match:
            file_name = match.group(1)
        else:
            file_name = self.file_name

        if not file_name.endswith(".js"):
            file_name += ".js"
        self.jump_to_file(file_name)

    def jump_to_file(self, file, point=-1):
        if not os.path.isabs(file):
            file = os.path.join(self.folder, file)

        window = self.view.window()
        view = window.find_open_file(file)
        if view:
            window.focus_view(view)
        else:
            if os.path.exists(file):
                if not os.path.isfile(file):
                    sublime.message_dialog("'%s' 不是一个有效的文件")
                    return
            else:
                if not sublime.ok_cancel_dialog("文件 '%s' 不存在，是否创建？" % file, "Create"):
                    return
            window.run_command('open_file', {"file": file})
        if point >= 0:
            view = window.active_view()
            view.run_command('mist_move_caret', {'point': point})

    def get_all_blocks(self):
        blocks = []
        for match in re.finditer(r'"blockId"\s*:\s*"(KOUBEI@[^"\n]*)"', self.content):
            block = {"id": match.group(1), "point": match.start(1)}
            found = next(filter(lambda b, a=block: b["id"] == a["id"], reversed(blocks)), None)
            if found:
                block["index"] = found["index"] + 1 if "index" in found else 2
            blocks.append(block)
        return blocks

    def scope_generator(self, point):
        length = self.view.size()
        text = self.content

        def _left_generator():
            i = point - 1
            j = 0
            while i >= 0:
                char = text[i]
                if char == '{':
                    if j == 0:
                        yield i
                    else:
                        j -= 1
                elif char == '}':
                    j += 1
                i -= 1

        def _right_generator():
            i = point
            j = 0
            while i < length:
                char = text[i]
                if char == '}':
                    if j == 0:
                        yield i + 1
                    else:
                        j -= 1
                elif char == '{':
                    j += 1
                i += 1

        left_itr = _left_generator()
        right_itr = _right_generator()

        for left in left_itr:
            yield (left, next(right_itr, length))

    def block_id_at_caret(self):
        text = self.content
        pos = self.view.sel()[0].b

        line = self.view.line(pos)
        match = re.search(r'"KOUBEI@([^"\n]*)"', text[line.a:line.b])
        if match:
            return match.group(1)

        for left, right in self.scope_generator(pos):
            if left == 0:
                return None
            match = re.search(r'"blockId"\s*:\s*"KOUBEI@([^"\n]*)"', text[left:right])
            if match is not None:
                return match.group(1)
