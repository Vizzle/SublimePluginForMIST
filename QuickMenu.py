import sublime, sublime_plugin, re, os, itertools
from .StatusBar import StatusBar


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


class QuickMenuItem:
    def __init__(self, title, callback):
        self.title = title
        self.callback = callback


class MistOpenQuickMenuCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        super().__init__(view)
        self._content = None

    @property
    def content(self):
        if self._content is None:
            self._content = self.view.substr(sublime.Region(0, self.view.size()))
        return self._content

    def run(self, edit):
        self.file = self.view.file_name()
        if self.file is None:
            sublime.message_dialog("请先保存到文件")
            return
        self.folder, file = os.path.split(self.file)
        self.fileName, self.fileExt = os.path.splitext(file)

        commands = []

        if self.fileExt == '.mist':
            commands.append(QuickMenuItem("Jump to Data File", self.jumpToDataFile))
            commands.append(QuickMenuItem("Jump to JS File", self.jumpToJsFile))
            commands.append(QuickMenuItem("Format (Pretty Print)", self.callback))
        
        if self.fileExt == '.json':
            commands.append(QuickMenuItem("Jump to Template File", self.jumpToTemplateFile))
            commands.append(QuickMenuItem("List All Blocks", self.listAllBlocks))

        if self.fileExt == '.js':
            commands.append(QuickMenuItem("Jump to Template File", self.jumpToTemplateFile))

        if len(commands) > 0:
            self.view.window().show_quick_panel([c.title for c in commands], lambda i: commands[i].callback() if i >= 0 else None)

    def callback(self):
        sublime.message_dialog("对不起，功能暂未实现～")

    def jumpToDataFile(self):
        files = []
        for (_, _, filenames) in os.walk(self.folder):
            files.extend(filenames)
            break

        results = []

        for file in files:
            if os.path.splitext(file)[1] != '.json':
                continue

            path = os.path.join(self.folder, file)
            with open(path, 'rb') as f:
                s = f.read().decode('utf-8')
                i = 1
                for result in re.finditer('"blockId"\\s*:\\s*"KOUBEI@%s"' % self.fileName, s):
                    results.append((file,result.start(), "%s #%d" % (file, i) if i > 1 else file))
                    i += 1

        jumpToIndex = lambda i: self.jumpToFile(results[i][0], results[i][1]) if i >= 0 else None

        if len(results) == 0:
            StatusBar.set(self.view, "未找到使用模版 '%s' 的数据文件" % self.fileName)
        elif len(results) == 1:
            jumpToIndex(0)
        else:
            self.view.window().show_quick_panel([r[2] for r in results], jumpToIndex)

    def jumpToTemplateFile(self):
        if self.fileExt == '.js':
            fileName = self.fileName
            if fileName.endswith("_js"):
                fileName = fileName[:-3]
            self.jumpToFile(fileName + ".mist")
            return
        else:
            block = self.blockIdAtCaret()
            if block:
                self.jumpToFile(block + ".mist")
            else:
                StatusBar.set(self.view, '请确保光标在block区块内')

    def listAllBlocks(self):
        blocks = self.getAllBlocks()
        names = ["%s #%d" % (b["id"], b["index"]) if "index" in b else b["id"] for b in blocks]
        self.view.window().show_quick_panel(names, lambda i:self.view.run_command('mist_move_caret', {'point': blocks[i]["point"]}) if i >= 0 else None)

    def jumpToJsFile(self):
        file = None
        match = re.search(r'"script-name"\s*:\s*"([^"\n]*)"', self.content)
        if match:
            file = match.group(1)
        else:
            file = self.fileName

        if not file.endswith(".js"):
            file += ".js"
        self.jumpToFile(file)

    def jumpToFile(self, file, point = -1):
        if not os.path.isabs(file):
            file = os.path.join(self.folder, file)
        window = self.view.window()
        if os.path.exists(file):
            if not os.path.isfile(file):
                sublime.message_dialog("'%s' 不是一个有效的文件")
        else:
            if not sublime.ok_cancel_dialog("文件 '%s' 不存在，是否创建？" % file, "Create"):
                return
        window.run_command('open_file', {"file": file})
        if point >= 0:
            view = window.active_view()
            view.run_command('mist_move_caret', {'point': point})

    def getAllBlocks(self):
        blocks = []
        print(itertools)
        for match in re.finditer(r'"blockId"\s*:\s*"(KOUBEI@[^"\n]*)"', self.content):
            block = {"id": match.group(1), "point": match.start(1)}
            found = next(filter(lambda b: b["id"] == block["id"], reversed(blocks)), None)
            if found:
                block["index"] = found["index"] + 1 if "index" in found else 2
            blocks.append(block)
        print(blocks)
        return blocks

    def scopeGenerator(self, point):
        length = self.view.size()
        s = self.content

        def leftGenerator():
            i = point-1
            j = 0
            while i >= 0:
                c = s[i]
                if c == '{':
                    if j == 0:
                        yield i
                    else:
                        j -= 1
                elif c == '}':
                    j += 1
                i -= 1

        def rightGenerator():
            i = point
            j = 0
            while i < length:
                c = s[i]
                if c == '}':
                    if j == 0:
                        yield i + 1
                    else:
                        j -= 1
                elif c == '{':
                    j += 1
                i += 1

        leftItr = leftGenerator()
        rightItr = rightGenerator()

        for l in leftItr:
            yield (l, next(rightItr, length))

    def blockIdAtCaret(self):
        length = self.view.size()
        s = self.content
        pos = self.view.sel()[0].b

        line = self.view.line(pos)
        match = re.search(r'"KOUBEI@([^"\n]*)"', s[line.a:line.b])
        if match:
            return match.group(1)

        for l, r in self.scopeGenerator(pos):
            if l == 0:
                return None
            match = re.search(r'"blockId"\s*:\s*"KOUBEI@([^"\n]*)"', s[l:r])
            if match is not None:
                return match.group(1)
