import sublime, sublime_plugin, re, os
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

class MistSwitchCommand(sublime_plugin.TextCommand):
    def run(self, edit, is_list = False):
        self.folder, file = os.path.split(self.view.file_name())
        fileName, fileExt = os.path.splitext(file)

        if fileExt == '.mist':
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
                        self.results = [(blockId + '.mist',)]
                        self.switchTo(0)
                        return

            self.results = []
            for result in re.finditer(r'"blockId"\s*:\s*"KOUBEI@([^"\n]*)"', s):
                r = result.group(1)
                if r not in self.results:
                    self.results.append((r + '.mist',))

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
