# -*- coding: utf-8 -*-
#vocalizer_globalPlugin/__init__.py
#A part of the vocalizer driver for NVDA (Non Visual Desktop Access)
#Copyright (C) 2012 Rui Batista <ruiandrebatista@gmail.com>
#Copyright (C) 2012 Tiflotecnia, lda. <www.tiflotecnia.com>
#This file is covered by the GNU General Public License.
#See the file GPL.txt for more details.

import datetime
import gettext
import os.path
import shutil
import time
import webbrowser
import subprocess
import configobj
import wx
import addonHandler
addonHandler.initTranslation()
import core
import globalVars
import globalPluginHandler
import gui
import languageHandler
from logHandler import log
import speech
# For update process
from . update import *
from .dialogs import *
from .utils import *


aboutMessage =_("""
 URL: {url}
 
This product is composed of two independent components:
- Nuance Vocalizer speech synthesizer.
- NVDA speech driver and interface for Nuance Vocalizer.
Licenses and conditions for these components are as follows:

Nuance Vocalizer speech synthesizer:

Copyright (C) 2011 Nuance Communications, Inc. All rights reserved.

Synthesizer Version: {synthVersion}
This copy of the Nuance Vocalizer synthesizer is licensed to be used exclusively with the NVDA screen reader (Non Visual Desktop Access).

License information:
{licenseInfo}

License management components are property of Tiflotecnia, LDA.
Copyright (C) 2012 Tiflotecnia, LDA. All rights reserved.


NVDA speech driver and interface for Nuance Vocalizer:

Copyright (C) 2012 Tiflotecnia, LDA.
Copyright (C) 2012 Rui Batista.
Copyright (C) 2019 Babbage B.V.

 Version: {driverVersion}
 
 NVDA speech driver and interface for Nuance Vocalizer is covered by the GNU General Public License (Version 2). You are free to share or change this software in any way you like as long as it is accompanied by the license and you make all source code available to anyone who wants it. This applies to both original and modified copies of this software, plus any derivative works.
For further details, you can view the license from the NVDA Help menu.
It can also be viewed online at: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html

This component was developed by Tiflotecnia, LDA and Rui Batista, with contributions from many others. Special thanks goes to:
{contributors}
""")

contributors = "NV Access ltd, ângelo Abrantes, Diogo Costa, Mesar Hameed, Babbage B.V.."


URL = "http://vocalizer-nvda.com"
VOICE_DOWNLOADS_URL_TEMPLATE = "http://www.vocalizer-nvda.com/downloads_redirect.php?lang={lang}"

def getDefaultLicensePath():
	import globalVars
	return os.path.join(globalVars.appArgs.configPath, "vocalizer_license.ini")

def getLicenseInfo():
	licenseInfo = _("No License.")
	from synthDrivers.vocalizerAutomotive import _vocalizer
	try:
		licenseInfo = _vocalizer.getLicenseInfo()
	except _vocalizer.VautoError:
		pass
	return licenseInfo


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self._running = False
		if globalVars.appArgs.secure:
			return

		# See if we have at least one voice installed
		if not any(addon.name.startswith("vocalizer-voice-") for addon in addonHandler.getRunningAddons()):
			wx.CallLater(2000, self.onNoVoicesInstalled)
			return
		with VocalizerOpened():
			self.createMenu()
			self.showInformations()
		self._running = True

		# To allow waiting end of network tasks
		core.postNvdaStartup.register(self.networkTasks)

	def networkTasks(self):
		# Calling the update process...
		_MainWindows = Initialize()
		_MainWindows.start()

	def createMenu(self):
		self.submenu_items = []
		self.submenu_vocalizer = wx.Menu()
		item = self.submenu_vocalizer.Append(wx.ID_ANY, _("Automatic &Language Switching Settings"), _("Configure which voice is to be used for each language."))
		self.submenu_items.append(item)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU , lambda e : gui.mainFrame._popupSettingsDialog(VocalizerLanguageSettingsDialog), item)
		licenseInfo = getLicenseInfo()
		isLicensed = licenseInfo.startswith("licensed")
		if not isLicensed and licenseInfo != "invalid":
			item = self.submenu_vocalizer.Append(wx.ID_ANY, _("Enter License"), _("Enter your license data for this computer."))
			self.submenu_items.append(item)
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU , self.onVocalizerLicenseMenu, item)
		else:
			item = self.submenu_vocalizer.Append(wx.ID_ANY, _("Remove License"), _("Remove your license from this NVDA copy"))
			self.submenu_items.append(item)
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU , self.onVocalizerLicenseRemoveMenu, item)
		item = self.submenu_vocalizer.Append(wx.ID_ANY, _("Download More Voices"), _("Open the vocalizer voices download page."))
		self.submenu_items.append(item)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onVoicesDownload, item)
		item = self.submenu_vocalizer.Append(wx.ID_ANY, _("About Nuance Vocalizer for NVDA"))
		self.submenu_items.append(item)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU , self.onAbout, item)
		self.submenu_item = gui.mainFrame.sysTrayIcon.menu.Insert(2, wx.ID_ANY, _("VocalizerAutomotive"), self.submenu_vocalizer)

	def removeMenu(self):
		if self.submenu_item is not None:
			try:
				gui.mainFrame.sysTrayIcon.menu.Remove(self.submenu_item)
			except AttributeError: # We can get this somehow from wx python when NVDA is shuttingdown, just ignore
				pass
			self.submenu_item.Destroy()


	def onVocalizerLicenseMenu(self, event):
		licensePath = getDefaultLicensePath()
		ret = gui.messageBox(_("""Choose the file that contains your license data on the dialog that will be opened.

If you don't have a vocalizer license for NVDA or are expiriencing other problems please contact Tiflotecnia, LDA. 
(tiflotecnia@tiflotecnia.com)
or your Vocalizer for NVDA distributor.

Unauthorized use of this product (i.g. without a valid license) is not allowed by most international laws on software rights.
The license file is intended soley for your private use.
If the Nuance Vocalizer license file doesn't belong to you should reframe from using this product.

Please note that a proportion of the price of Nuance Vocalizer for NVDA is donated for continuing NVDA's development.
Any shared license files will reduce donations to NVDA and good/cheap accessibility for the blind across the world.
Further more, Nuance Vocalizer for NVDA is priced at the lowest value possible, to allow as many people as possible to have a comercial syntheciser for NVDA.

Do you want to continue?"""),
		caption=_("Entering License Data:"), style=wx.YES_NO|wx.ICON_QUESTION)
		if ret == wx.YES:
			fd = wx.FileDialog(gui.mainFrame,
				message=_("Choose license file"),
				wildcard=(_("Nuance Vocalizer license files")+"|license*.ini"),
				defaultDir="c:",
				style=wx.FD_OPEN)
			if fd.ShowModal() != wx.ID_OK:
				return
			path = fd.GetPath()
			try:
				shutil.copy(path, licensePath)
				with VocalizerOpened():
					self.removeMenu()
					self.createMenu()
				if gui.messageBox(_("""License entered successfully!
For all changes to take effect NVDA must be restarted.
Do you want to restart NVDA now?"""),
					caption=_("Success!"), style=wx.YES_NO) == wx.YES:
					core.restart()
			except (IOError, WindowsError) as e:
				log.debugWarning("Error entering license", exc_info=True)
				gui.messageBox(_("Error copying license data: {error}").format(error=str(e)),
				caption=_("Error"), style=wx.ICON_ERROR)

	def onVocalizerLicenseRemoveMenu(self, event):
		ret = gui.messageBox(_("""Are you sure you want to remove your license?
This can not be reverted."""),
		caption=_("Remove License?"), style=wx.YES_NO)
		if ret == wx.YES:
			with VocalizerOpened():
				licenseInfo = getLicenseInfo()
				if licenseInfo == "invalid":
					# Try to remove from the default path.
					path = getDefaultLicensePath()
				else: # licensed
					i = licenseInfo.index(":")
					path = licenseInfo[i+1:]
				try:
					os.unlink(path)
					self.removeMenu()
					self.createMenu()
					gui.messageBox(_("License successfully removed. Restart NVDA fo the changes to ttake effect."),
					caption=_("License removed"), style=wx.ICON_INFORMATION)
				except(IOError, WindowsError) as e:
					log.debugWarning("Error removing Vocalizer License.", exc_info=True)
					gui.messageBox(_("Error removing license: {error}").format(error=str(e)), _("Error"))

	def onVoicesDownload(self, event):
		self._openVoicesDownload()

	def _openVoicesDownload(self):
		webbrowser.open(VOICE_DOWNLOADS_URL_TEMPLATE.format(lang=languageHandler.getLanguage()))

	def onAbout(self, event):
		from synthDrivers import vocalizerAutomotive
		from synthDrivers.vocalizerAutomotive import _vocalizer
		synthVersion = vocalizer.synthVersion
		driverVersion = vocalizer.driverVersion

		licenseInfo = _("License data not available")
		try:
			with VocalizerOpened():
				licenseInfo = getLicenseInfo()
			if licenseInfo.startswith("demo"):
				t = int(licenseInfo.split(":")[1])
				d = datetime.datetime.fromtimestamp(t)
				licenseInfo = _("Demo license. Expiration date: %s") % d.strftime("%Y-%m-%d")
			elif licenseInfo.startswith("licensed"):
				i = licenseInfo.index(':')
				path = licenseInfo[i+1:]
				log.debug("Reading license information from %s", path)
				ini = configobj.ConfigObj(path, default_encoding='utf-8', encoding='utf-8')
				l = []
				l.append(_("User Name: ") + ini['info']['username'])
				l.append(_("User Identification: ") + ini['info']['userid'])
				l.append(_("License Number: ") + ini['info']['licenseid'])
				l.append(_("Distributor: ") + ini['info']['distributor'])
				licenseInfo = "\n".join(l)
		except:
			log.exception("Error retrieving license data")
		msg = aboutMessage.format(url=URL, contributors=contributors, **locals())
		gui.messageBox(msg, _("About Nuance Vocalizer for NVDA"), wx.OK)

	def showInformations(self):
		from synthDrivers.vocalizerAutomotive import _config
		_config.load()
		licenseInfo = getLicenseInfo()
		if licenseInfo.startswith("licensed"):
			return
		elif licenseInfo == "expired":
			lastReportTime = _config.vocalizerConfig['demo_expired_reported_time']
			# If reported less than one day ago, don't bother the user.
			if (lastReportTime + 3600 * 24) > time.time():
				return
			wx.CallLater(2000, gui.messageBox,
			_("The Nuance Vocalizer for NVDA demonstration license has expired.\n"
			"To buy a  license for Nuance Vocalizer for NVDA, please visit {url}, or contact an authorized distributor.\n"
			"Note that a percentage of the license's price is donated to NV Access, ltd, to help continuing the development of the NVDA screen reader.").format(url=URL),
			_("Vocalizer Demo Expired"))
			_config.vocalizerConfig['demo_expired_reported_time'] = time.time()
			_config.save()
		elif licenseInfo == "invalid":
			wx.CallLater(2000, gui.messageBox,
			_("The Vocalizer license you are trying to use is invalid.\n"
			"This might be happening due to one of two reasons:\n"
			"1. The license file is damaged or is not a valid license file.\n"
			"2. The license was disabled for security reasons, due to illegal use or its data beeing compromized.\n"
			"If you own a license for Nuance Vocalizer for NVDA, please contact Tiflotecnia, lda. or your local distributor, so the problem can be further investigated.\n"
			"If this Nuance Vocalizer for NVDA license file doesn't belong to you should reframe from using this product.\n"
			"Unauthorized use of this product (i.g. without a valid license) is not allowed by most international laws on software rights.\n"
			"Please note that a proportion of the price of Nuance Vocalizer for NVDA is donated for continuing NVDA's development.\n"
			"By sharing license files you are working against NVDA and good and cheap accessibility for the blind across the world.\n"
			"Further more, Nuance Vocalizer for NVDA is priced at the lowest value possible, to allow as many people as possible to have a comercial quality syntheciser in NVDA.\n"
			"Please think twice about it.\n"
			"You can remove this invalid license using  the Vocalizer menu."),
			caption=_("Vocalizer License is Invalid."))
		elif licenseInfo.startswith("demo"):
			t = int(licenseInfo.split(":")[1])
			d  = datetime.datetime.fromtimestamp(t)
			dateStr = d.strftime("%Y-%m-%d")
			lastReportedTime = _config.vocalizerConfig['demo_license_reported_time']
			if (lastReportedTime + 3600 * 24) > time.time():
				return
			wx.CallLater(2000, gui.messageBox,
			_("You are running a demo version of Nuance Vocalizer for NVDA.\n"
			"This demo will expire on {date}. To use the syntheciser after that,\n"
			"You must buy a license. You can do so at any time visiting {url} or contacting a local distributor.\n"
			"Thanks for testing Nuance Vocalizer for NVDA.").format(url=URL, date=dateStr),
			_("Vocalizer Demo Version"))
			_config.vocalizerConfig['demo_license_reported_time'] = time.time()
			_config.save()

	def onNoVoicesInstalled(self):
		if gui.messageBox(_("You have no Vocalizer voices installed.\n"
		"You need at least one voice installed to use Vocalizer for NVDA.\n"
		"You can download all Vocalizer voices from the product web page.\n"
		"Would you want to open the vocalizer for NVDA voices download page now?"),
		caption=_("No voices installed."), style=wx.YES_NO|wx.ICON_WARNING) == wx.YES:
			self._openVoicesDownload()

	def  terminate(self):
		if not self._running:
			return
		try:
			self.removeMenu()
		except wx.PyDeadObjectError:
			pass
