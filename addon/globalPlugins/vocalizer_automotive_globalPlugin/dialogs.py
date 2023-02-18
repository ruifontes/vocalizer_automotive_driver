#vocalizer_globalPlugin/dialogs.py
#A part of the vocalizer driver for NVDA (Non Visual Desktop Access)
#Copyright (C) 2012 Rui Batista <ruiandrebatista@gmail.com>
#Copyright (C) 2012 Tiflotecnia, lda. <www.tiflotecnia.com>
#This file is covered by the GNU General Public License.
#See the file GPL.txt for more details.

from collections import defaultdict
import wx
import addonHandler
addonHandler.initTranslation()
import gui
import languageHandler
from synthDrivers.vocalizerAutomotive import _config
from synthDrivers.vocalizerAutomotive._voiceManager import VoiceManager
from .utils import VocalizerOpened

class VocalizerLanguageSettingsDialog(gui.SettingsDialog):
	title = _("Vocalizer Automatic Language Switching Settings")
	def __init__(self, parent):
		with VocalizerOpened():
			manager = VoiceManager()
			self._localeToVoices = manager.localeToVoicesMap
			manager.close()
		self._dataToPercist = defaultdict(lambda : {})
		self._locales = sorted([l for l in self._localeToVoices if len(self._localeToVoices[l]) > 1])
		super(VocalizerLanguageSettingsDialog, self).__init__(parent)

	def makeSettings(self, sizer):
		helpLabel = wx.StaticText(self, label=_("Select a locale, and then configure the voice to be used:"))
		helpLabel.Wrap(self.GetSize()[0])
		sizer.Add(helpLabel)
		localesSizer = wx.BoxSizer(wx.HORIZONTAL)
		localesLabel = wx.StaticText(self, label=_("Locale Name:"))
		localesSizer.Add(localesLabel)
		localeNames = list(map(self._getLocaleReadableName, self._locales))
		self._localesChoice = wx.Choice(self, choices=localeNames)
		self.Bind(wx.EVT_CHOICE, self.onLocaleChanged, self._localesChoice)
		localesSizer.Add(self._localesChoice)
		voicesSizer = wx.BoxSizer(wx.HORIZONTAL)
		voicesLabel = wx.StaticText(self, label=_("Voice Name:"))
		voicesSizer.Add(voicesLabel)
		self._voicesChoice = wx.Choice(self, choices=[])
		self.Bind(wx.EVT_CHOICE, self.onVoiceChange, self._voicesChoice)
		voicesSizer.Add(self._voicesChoice)
		sizer.Add(localesSizer)
		sizer.Add(voicesSizer)

	def postInit(self):
		self._updateVoicesSelection()
		self._localesChoice.SetFocus()

	def _updateVoicesSelection(self):
		localeIndex = self._localesChoice.GetCurrentSelection()
		if localeIndex < 0:
			self._voicesChoice.SetItems([])
		else:
			locale = self._locales[localeIndex]
			voices = sorted(self._localeToVoices[locale])
			self._voicesChoice.SetItems(voices)
			if locale in _config.vocalizerConfig['autoLanguageSwitching']:
				voice = _config.vocalizerConfig['autoLanguageSwitching'][locale]['voice']
				if voice:
					self._voicesChoice.Select(voices.index(voice))

	def onLocaleChanged(self, event):
		self._updateVoicesSelection()

	def onVoiceChange(self, event):
		localeIndex = self._localesChoice.GetCurrentSelection()
		if localeIndex >= 0:
			locale = self._locales[localeIndex]
			self._dataToPercist[locale]['voice'] = self._voicesChoice.GetStringSelection()
		else:
			self._dataToPercist[locale]['voice'] = None

	def onOk(self, event):
		super(VocalizerLanguageSettingsDialog, self).onOk(event)
		# Update Configuration
		_config.vocalizerConfig['autoLanguageSwitching'].update(self._dataToPercist)
		_config.save()
		return True

	def _getLocaleReadableName(self, locale):
		description = languageHandler.getLanguageDescription(locale)
		return "%s - %s" % (description, locale) if description else locale