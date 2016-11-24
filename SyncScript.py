#! /usr/bin/env python   
# -*- coding: utf-8 -*-   
import sublime, sublime_plugin, os, re
from sublime import Region

try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO

class SyncScriptListener(sublime_plugin.EventListener):
	def on_pre_save(self, view):
		view.run_command('sync_script')
		
class SyncScriptCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		if not view.file_name().endswith('.js'):
			return

		jsContent = jsmin(view.substr(Region(0, view.size()))).replace('\n', '\\n').replace('"', '\\"')
		if not jsContent:
			return

		template = os.path.splitext(view.file_name())[0] + '.mist'
		templateView = view.window().find_open_file(template)

		if templateView:
			region = templateView.find('"script"\s*:\s*"\K.*?(?=",)', 0, 0)

			if region == Region(-1, -1):
				scriptLine = '"script": "' + jsContent + '",\n  '
				templateView.insert(edit, 4, scriptLine)
				print('当前脚本已插入 ' + template)
			else:
				if jsContent == templateView.substr(region):
					return

				templateView.replace(edit, region, jsContent)
				print('当前脚本已同步至 ' + template)

			sublime.set_timeout_async(lambda:templateView.run_command('save'), 50)
			
		else:
			replaceJSInTemplate(template, jsContent)
			print('当前脚本已同步至 ' + template)

def jsmin(js):
	ins = StringIO(js)
	outs = StringIO()
	JavascriptMinify().minify(ins, outs)
	str = outs.getvalue()
	if len(str) > 0 and str[0] == '\n':
		str = str[1:]
	return str

def replaceJSInTemplate(templatePath, jsContent):
	if not os.path.isfile(templatePath):
		sublime.message_dialog("没有找到模板文件 " + templatePath)

	originContent = ''
	originScript = ''
	with open(templatePath, 'r', encoding='utf-8') as templateFile:
		originContent = templateFile.read()
		script = re.compile('"script"\s*:\s*".*?",').search(originContent)
		if script:
			originScript = script.group()

	newScript = '"script": "' + jsContent + '",'
	if originScript == newScript:
		return
	else:
		newContent = originContent.replace(originScript, newScript)
		with open(templatePath, 'w', encoding='utf-8') as templateFile:
			templateFile.write(newContent)

# jsminify

def isAlphanum(c):
	"""return true if the character is a letter, digit, underscore,
		   dollar sign, or non-ASCII character.
	"""
	return ((c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') or
			(c >= 'A' and c <= 'Z') or c == '_' or c == '$' or c == '\\' or (c is not None and ord(c) > 126));

class UnterminatedComment(Exception):
	pass

class UnterminatedStringLiteral(Exception):
	pass

class UnterminatedRegularExpression(Exception):
	pass

class JavascriptMinify(object):

	def _outA(self):
		self.outstream.write(self.theA)
	def _outB(self):
		self.outstream.write(self.theB)

	def _get(self):
		"""return the next character from stdin. Watch out for lookahead. If
		   the character is a control character, translate it to a space or
		   linefeed.
		"""
		c = self.theLookahead
		self.theLookahead = None
		if c == None:
			c = self.instream.read(1)
		if c >= ' ' or c == '\n':
			return c
		if c == '': # EOF
			return '\000'
		if c == '\r':
			return '\n'
		return ' '

	def _peek(self):
		self.theLookahead = self._get()
		return self.theLookahead

	def _next(self):
		"""get the next character, excluding comments. peek() is used to see
		   if an unescaped '/' is followed by a '/' or '*'.
		"""
		c = self._get()
		if c == '/' and self.theA != '\\':
			p = self._peek()
			if p == '/':
				c = self._get()
				while c > '\n':
					c = self._get()
				return c
			if p == '*':
				c = self._get()
				while 1:
					c = self._get()
					if c == '*':
						if self._peek() == '/':
							self._get()
							return ' '
					if c == '\000':
						raise UnterminatedComment()

		return c

	def _action(self, action):
		"""do something! What you do is determined by the argument:
		   1   Output A. Copy B to A. Get the next B.
		   2   Copy B to A. Get the next B. (Delete A).
		   3   Get the next B. (Delete B).
		   action treats a string as a single character. Wow!
		   action recognizes a regular expression if it is preceded by ( or , or =.
		"""
		if action <= 1:
			self._outA()

		if action <= 2:
			self.theA = self.theB
			if self.theA == "'" or self.theA == '"':
				while 1:
					self._outA()
					self.theA = self._get()
					if self.theA == self.theB:
						break
					if self.theA <= '\n':
						raise UnterminatedStringLiteral()
					if self.theA == '\\':
						self._outA()
						self.theA = self._get()


		if action <= 3:
			self.theB = self._next()
			if self.theB == '/' and (self.theA == '(' or self.theA == ',' or
									 self.theA == '=' or self.theA == ':' or
									 self.theA == '[' or self.theA == '?' or
									 self.theA == '!' or self.theA == '&' or
									 self.theA == '|' or self.theA == ';' or
									 self.theA == '{' or self.theA == '}' or
									 self.theA == '\n'):
				self._outA()
				self._outB()
				while 1:
					self.theA = self._get()
					if self.theA == '/':
						break
					elif self.theA == '\\':
						self._outA()
						self.theA = self._get()
					elif self.theA <= '\n':
						raise UnterminatedRegularExpression()
					self._outA()
				self.theB = self._next()


	def _jsmin(self):
		"""Copy the input to the output, deleting the characters which are
		   insignificant to JavaScript. Comments will be removed. Tabs will be
		   replaced with spaces. Carriage returns will be replaced with linefeeds.
		   Most spaces and linefeeds will be removed.
		"""
		self.theA = '\n'
		self._action(3)

		while self.theA != '\000':
			if self.theA == ' ':
				if isAlphanum(self.theB):
					self._action(1)
				else:
					self._action(2)
			elif self.theA == '\n':
				if self.theB in ['{', '[', '(', '+', '-']:
					self._action(1)
				elif self.theB == ' ':
					self._action(3)
				else:
					if isAlphanum(self.theB):
						self._action(1)
					else:
						self._action(2)
			else:
				if self.theB == ' ':
					if isAlphanum(self.theA):
						self._action(1)
					else:
						self._action(3)
				elif self.theB == '\n':
					if self.theA in ['}', ']', ')', '+', '-', '"', '\'']:
						self._action(1)
					else:
						if isAlphanum(self.theA):
							self._action(1)
						else:
							self._action(3)
				else:
					self._action(1)

	def minify(self, instream, outstream):
		self.instream = instream
		self.outstream = outstream
		self.theA = '\n'
		self.theB = None
		self.theLookahead = None

		self._jsmin()
		self.instream.close()