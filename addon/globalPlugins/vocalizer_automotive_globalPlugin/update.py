# -*- coding: UTF-8 -*-
# Copyright (C) 2021 Rui Fontes <rui.fontes@tiflotecnia.com> and Ângelo Abrantes <ampa4374@gmail.com>
# Update add-ons module based on the work of several add-on authors
# This file is covered by the GNU General Public License.
#
# You just need to place this module in the appModule or globalPlugin folder and include in the __init__.py file in the import section:
"""
# For update process
from . update import *
"""
# and in the def __init__(self):
"""
		_MainWindows = Initialize()
		_MainWindows.start()
"""

# import the necessary modules.
import ui
import wx
import os
import globalVars
import addonHandler
import addonHandler.addonVersionCheck
import winsound
from threading import Thread
import urllib.request
import json
import config
import gui
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from gui import guiHelper
import core
import shutil

# For translation
addonHandler.initTranslation()

def getOurAddon():
	for addon in addonHandler.getAvailableAddons():
		test0 = str(os.path.dirname(__file__).split("\\")[-1:]).replace("[", "").replace("\'", "").replace("]", "")
		test = test0.split("_")[0]+"_"+test0.split("_")[1]
		if  test in addon.manifest['name']:
			print(addon)
			return addon

ourAddon = getOurAddon()
print(ourAddon)
bundle = getOurAddon()

def initConfiguration():
	confspec = {
		"isUpgrade": "boolean(default=True)",
	}
	config.conf.spec[ourAddon.manifest["name"]] = confspec

def getConfig(key):
	value = config.conf[str(ourAddon.manifest["name"])][key]
	return value

def setConfig(key, value):
	try:
		config.conf.profiles[0][ourAddon.manifest["name"]][key] = value
	except:
		config.conf[ourAddon.manifest["name"]][key] = value

initConfiguration()
shouldUpdate = getConfig("isUpgrade")
urlRepos = "https://api.github.com/repos/ruifontes/vocalizer_expressive_driver/releases"
urlName = ""
urlN = ""
directory = ""


class Initialize(Thread):
	# Creating the constructor of the newly created GlobalPlugin class.
	def __init__(self):
		# Call of the constructor of the parent class.
		super(Initialize, self).__init__()
		# Add a section in NVDA configurations panel
		NVDASettingsDialog.categoryClasses.append(AddOnPanel)
		self.daemon = True
		wx.CallAfter(AddonFlow.upgradeVerify)


class AddonFlow(Thread):
	def __init__(self):
		super(AddonFlow, self).__init__()
		self.daemon = True

	def upgradeVerify():
		if globalVars.appArgs.secure or config.isAppX or globalVars.appArgs.launcher:
			AddonFlow.doNothing()
		if shouldUpdate == True:
			p = urllib.request.Request(urlRepos)
			r = urllib.request.urlopen(p).read()
			githubApi = json.loads(r.decode('utf-8'))
			if githubApi[0]["tag_name"] != ourAddon.manifest["version"]:
				# Translators: Message dialog box to ask user if wants to update.
				if gui.messageBox(_("It is available a new version of this add-on.\n Do you want to update?"), ourAddon.manifest["summary"], style=wx.ICON_QUESTION|wx.YES_NO) == wx.YES:
					AddonFlow.download()
				else:
					AddonFlow.doNothing()

	def download():
		global urlName, urlN, directory, bundle
		p = urllib.request.Request(urlRepos)
		r = urllib.request.urlopen(p).read()
		githubApi = json.loads(r.decode('utf-8'))
		urlName = githubApi[0]['assets'][0]['browser_download_url']
		urlN = str(urlName.split("/")[-1:]).replace("[", "").replace("\'", "").replace("]", "")
		directory = os.path.join(globalVars.appArgs.configPath, "updates")
		if os.path.exists(directory) == False:
			os.mkdir(directory)
		file = os.path.join(directory, urlN)
		req = urllib.request.Request(urlName, headers={'User-Agent': 'Mozilla/5.0'})
		response = urllib.request.urlopen(req)
		fileContents = response.read()
		response.close()
		f = open(file, "wb")
		f.write(fileContents)
		f.close()
		bundle = addonHandler.AddonBundle(file)
		if bundle.manifest["name"] == ourAddon.manifest['name']:
			AddonFlow.checkCompatibility()
		AddonFlow.doNothing()

	def checkCompatibility():
		if addonHandler.addonVersionCheck.isAddonCompatible(ourAddon):
			# It is compatible, so install
			AddonFlow.install()
		# It is not compatible, so do not install and inform user
		else:
			# Translators: Message dialog box to inform user that the add-on is not compatible
			gui.messageBox(_("This new version of this add-on is not compatible with your version of NVDA.\n The update process will be terminated."), ourAddon.manifest["summary"], style=wx.ICON_WARNING)
			AddonFlow.doNothing()

	def install():
		# To remove the old version
		ourAddon.requestRemove()
		# to install the new version
		addonHandler.installAddonBundle(bundle)
		# to delete the downloads folder
		shutil.rmtree(directory, ignore_errors=True)
		# to restart NVDA
		core.restart()

	def doNothing():
		pass


class AddOnPanel(SettingsPanel):
	title = ourAddon.manifest["summary"]

	def makeSettings(self, sizer):
		helper=guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: Checkbox name in the configuration dialog
		self.shouldUpdateChk = helper.addItem(wx.CheckBox(self, label=_("Check for updates at startup")))
		self.shouldUpdateChk	.Bind(wx.EVT_CHECKBOX, self.onChk)
		self.shouldUpdateChk	.Value = shouldUpdate

	def onSave(self):
		setConfig("isUpgrade", self.shouldUpdateChk.Value)

	def onChk(self, event):
		shouldUpdate = self.shouldUpdateChk.Value


