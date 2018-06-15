from sys import argv
from os import path, getcwd
from watchgod import watch
from watchgod.watcher import DefaultDirWatcher
from json import loads as load_json, dumps as dump_json
from uuid import uuid4
from traceback import format_exc as get_traceback
from .version import VERSION_STRING
from jsmin import jsmin
from sass import compile as sass_compile
import click
import re

class ValidationError(Exception):
	def __init__(self, message):
		super().__init__(message)

class EleranWatcher(DefaultDirWatcher):
	def should_watch_file(self, entry):
		return entry.name.endswith(('.scss', '.js', '.sass', '.json'))

class Eleran():
	def __init__(self, TargetDir=None, Mode=None):
		self.BasePath	= getcwd()
		self.WatchFiles	= []
		self.ConfigFile	= "eleran.json"
		self.Config		= {}
		self.Index		= {}
		self.Version	= VERSION_STRING
		self.Mode		= Mode

		# Path
		if TargetDir:
			self.BasePath = path.join(getcwd(), TargetDir)

		# Print
		echo_click(" * Eleran version", self.Version)
	
	def read_file(self, Filename, Mode="r"):
		FileObject	= open(Filename, Mode)
		String		= FileObject.read()
		return String

	def get_id(self, Filepath):
		ID = self.Index.get(Filepath)
		return ID

	def get_sass_imported(self, Source, ID):
		String		= self.read_file(Source)
		Result		= re.findall('^@import\s*".+"', String, re.MULTILINE|re.IGNORECASE)
		for Item in Result:
			Filename	= Item.replace(" ", "")
			Filename	= Filename.replace('@import"', "")
			Filename	= Filename[:-1]
			Filename	= "_" + Filename + ".scss"
			Filepath	= path.join(path.dirname(Source), Filename)
			if path.isfile(Filepath):
				if not Filepath in self.WatchFiles:
					self.Index[Filepath] = ID
					self.WatchFiles.append(Filepath)

	def watch(self):
		# Print
		echo_click(" * Watch for", self.BasePath, Color="green")
		echo_click(" * Press CTRL+C to quit", Color="green")

		# Config File
		ConfigFile = path.join(self.BasePath, self.ConfigFile)

		# Watch
		for Changes in watch(self.BasePath, watcher_cls=EleranWatcher):
			_Type, FileChange	= list(Changes)[0]
			TypeChange			= _Type.name.capitalize()
			if FileChange in self.WatchFiles:
				echo_click(" *", TypeChange, FileChange)
				ID = self.get_id(FileChange)
				if self.Mode == "debug":
					echo_click(" * Build ID:", ID)
				# Build
				self.build(ID)
			elif FileChange == ConfigFile:
				echo_click(" *", TypeChange, FileChange)
				self.reload_config()

	def build(self, ID):
		try:
			ConfigData	= self.Config.get(ID)
			ConfigType	= ConfigData.get("Type")

			if ConfigType == "sass":
				SassSource	= ConfigData.get("source")
				SassOutput	= ConfigData.get("output")
				SassStyle	= ConfigData.get("output_style")
				SassComment	= ConfigData.get("source_comments")
				Filepath	= path.join(self.BasePath, SassSource)
				String		= sass_compile(
					filename		= Filepath,
					output_style	= SassStyle,
					source_comments	= SassComment
				)

				# Detect new import
				self.get_sass_imported(Filepath, ID)

				# Save
				FileWrite = open(path.join(self.BasePath, SassOutput), "w")
				FileWrite.write(String)
				FileWrite.close()

			elif ConfigType == "js":
				JSInclude	= ConfigData.get("include")
				JSOutput	= ConfigData.get("output")
				JSString	= ""

				# Join
				for i in JSInclude:
					Filepath	= path.join(self.BasePath, i)
					String		= self.read_file(Filepath)
					JSString	+= String
				
				# Save
				JSString = jsmin(JSString)
				FileWrite = open(path.join(self.BasePath, JSOutput), "w")
				FileWrite.write(JSString)
				FileWrite.close()
				
		except Exception as e:
			echo_click(" * Error:", e, Color="red")

	def generate_config(self):
		Sample = [
			{
				"sass": {
					"source": "sass/style.scss",
					"output": "style.min.css",
					"output_style": "compressed",
					"source_comments": False
				}
			},
			{
				"js": {
					"include": [
						"js/fo.js",
						"js/bar.js"
					],
					"output": "script.min.js"
				}
			}
		]

		# Save
		String		= dump_json(Sample, indent="\t")
		Filepath	= path.join(self.BasePath, "eleran.json")

		# Print
		echo_click(" * Creating config file to", Filepath)

		# Save
		FileWrite = open(Filepath, "w")
		FileWrite.write(String)
		FileWrite.close()

	def reload_config(self):
		self.Index		= {}
		self.WatchFiles	= []
		self.Config		= {}
		self.load_config()

	def load_config(self):
		# Config
		ConfigFile = path.join(self.BasePath, self.ConfigFile)

		# Print
		echo_click(" * Loading config:", ConfigFile)
		
		# Is file exist
		if path.isfile(ConfigFile):
			# Load file
			Config	= self.read_file(ConfigFile)
			Config	= load_json(Config)

			for Item in Config:
				SassConfig	= Item.get("sass")
				JSConfig	= Item.get("js")
				ID			= str(uuid4())
				if SassConfig:
					# Config
					SassConfig["Type"]	= "sass"
					self.Config[ID]		= SassConfig

					# File
					File = SassConfig.get("source")
					if File:
						Filepath = path.join(self.BasePath, File)
						if path.isfile(Filepath):
							self.get_sass_imported(Filepath, ID)
							self.Index[Filepath] = ID
							self.WatchFiles.append(Filepath)

						else:
							echo_click(" *", File, "not found", Color="red")
					else:
						echo_click(" * Sass source file not found", Color="red")

				elif JSConfig:
					# Config
					JSConfig["Type"]	= "js"
					self.Config[ID]		= JSConfig

					# Files
					Files = JSConfig.get("include")
					if Files:
						for File in Files:
							Filepath = path.join(self.BasePath, File)
							if path.isfile(Filepath):
								self.Index[Filepath] = ID
								self.WatchFiles.append(Filepath)
							else:
								echo_click(" *", File, "not found", Color="red")
					else:
						echo_click(" * JS include files not found", Color="red")
				else:
					echo_click(" * Unknown config type", Color="red")
		else:
			raise ValidationError("Config file not found")

def echo_click(*args, Color=None):
	Text = []
	for i in args:
		Text.append(str(i))
	Text = " ".join(Text)
	if Color:
		click.echo(click.style(Text, fg=Color))
	else:
		click.echo(Text)

@click.command()
@click.argument('command', default='watch')
@click.argument('target', default='')
@click.option('--mode', default='')
def cli(command, target, mode):
	try:
		# App
		App = Eleran(target, mode)

		# Command
		if command == "watch":
			App.load_config()
			App.watch()
		elif command == "validate":
			App.load_config()
			echo_click(" * Config validation success!", Color="green")
		elif command == "generate":
			App.generate_config()
			echo_click(" * Success!", Color="green")

	except KeyboardInterrupt:
		print(" * Exit")
	
	except Exception as e:
		if mode == "debug":
			echo_click(" * " + str(get_traceback()), Color="red")
		else:
			echo_click(" * Error: " + str(e), Color="red")