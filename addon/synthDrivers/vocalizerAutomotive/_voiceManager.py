#vocalizer/_voiceManager.py
#A part of the vocalizer driver for NVDA (Non Visual Desktop Access)
#Copyright (C) 2012 Rui Batista <ruiandrebatista@gmail.com>
#Copyright (C) 2012 Tiflotecnia, lda. <www.tiflotecnia.com>
#This file is covered by the GNU General Public License.
#See the file GPL.txt for more details.

from collections import OrderedDict, defaultdict
import itertools
import operator
import languageHandler
from logHandler import log
from synthDriverHandler import VoiceInfo
from . import _config
from . import _languages
from . import _tuningData
from . import _vocalizer
from functools import reduce


PARAMETERS_TO_UPDATE = [_vocalizer.VAUTO_PARAM_VOLUME, _vocalizer.VAUTO_PARAM_SPEECHRATE]

class VoiceManager(object):
	def __init__(self):
		_config.load()
		self._createCaches()
		self._defaultInstance, self._defaultVoiceName = _vocalizer.open()
		self.onVoiceLoad(self._defaultVoiceName, self._defaultInstance)
		log.debug("Created voiceManager instance. Default voice is %s", self._defaultVoiceName)
		self._instanceCache = {self._defaultVoiceName : self._defaultInstance}

	@property
	def defaultVoiceInstance(self):
		return self._defaultInstance

	@property
	def defaultVoiceName(self):
		return self._defaultVoiceName

	def setDefaultVoice(self, voiceName):
		if voiceName not in self._voiceInfos:
			log.debugWarning("Voice not available, using default voice.")
			return
		instance = self.getVoiceInstance(voiceName)
		self._defaultInstance = instance
		self._defaultVoiceName = voiceName

	def getVoiceInstance(self, voiceName):
		try:
			instance = self._instanceCache[voiceName]
		except KeyError:
			instance = self._createInstance(voiceName)
		if self._voiceParametersCount[instance] < self._voiceParametersCount[self._defaultInstance]:
			self._updateParameters(instance)
		return instance

	def _createInstance(self, voiceName):
		instance, name = _vocalizer.open(voiceName)
		self.onVoiceLoad(voiceName, instance)
		self._instanceCache[name] = instance
		return instance

	def close(self):
		_vocalizer.sync() # Don't close while someething is still running
		for voiceName, instance in self._instanceCache.items():
			self.onVoiceUnload(voiceName, instance)
			_vocalizer.close(instance)
		_config.save() # Flush the configuration file

	def _createCaches(self):
		""" Create tables and caches to keep information that won't change on the synth. """
		self._localesToVoices = {}
		self._voiceParametersCount = defaultdict(lambda : 0)
		languages = _vocalizer.getLanguageList()
		voiceInfos = []
		self._languageNamesToLocales = {l.szLanguage : _languages.getLocaleNameFromTLW(l.szLanguageTLW) for l in languages}
		self._localesToLanguageNames = {v : k for (k, v) in self._languageNamesToLocales.items()}
		# Keep lists of voices appropriate for each locale.
		# Also collect existing voices for quick listing.
		for l in languages:
			voices = _vocalizer.getVoiceList(l.szLanguage)
			voiceInfos.extend([self._makeVoiceInfo(v) for v in voices])
			voiceNames = [v.szVoiceName for v in voices]
			self._localesToVoices[self._languageNamesToLocales[l.szLanguage]] = voiceNames

		# For locales with no country (i.g. "en") use all voices from all sub-locales
		locales = sorted(self._localesToVoices.keys(), key=self._localeGroupKey)
		for key, locales in itertools.groupby(locales, key=self._localeGroupKey):
			if key not in self._localesToVoices:
				self._localesToVoices[key] = reduce(operator.add, [self._localesToVoices[l] for l in locales])

		log.debug("Voices : %s", self._localesToVoices)
		# Kepp a list with existing voices in VoiceInfo objects.
		# sort voices by language and then voice name
		voiceInfos = sorted(voiceInfos, key=lambda v: (v.language, v.id))
		items = [(v.id, v) for v in voiceInfos]
		self._voiceInfos = OrderedDict(items)

	def setVoiceParameter(self, instance, param, value):
		_vocalizer.setParameter(instance, param, value)
		if param in PARAMETERS_TO_UPDATE and instance == self._defaultInstance:
			self._voiceParametersCount[instance] += 1

	def _updateParameters(self, instance):
		newParams = [(param, _vocalizer.getParameter(self._defaultInstance, param)) for param in PARAMETERS_TO_UPDATE]
		_vocalizer.setParameters(instance, newParams)
		self._voiceParametersCount[instance] = self._voiceParametersCount[self._defaultInstance]

	@property
	def voiceInfos(self):
		return self._voiceInfos

	@property
	def languages(self):
		return iter(self._localesToLanguageNames.keys())

	@property
	def localeToVoicesMap(self):
		return self._localesToVoices.copy()

	def getVoiceNameForLanguage(self, language):
		configured =  self._getConfiguredVoiceNameForLanguage(language)
		if configured is not None and configured in self.voiceInfos:
			return configured
		voices = self._localesToVoices.get(language, None)
		if voices is None:
			if '_' in language:
				voices = self._localesToVoices.get(language.split('_')[0], None)
		if voices is None:
			return None
		voice = self.defaultVoiceName if self.defaultVoiceName in voices else voices[0]
		return voice

	def getVoiceInstanceForLanguage(self, language):
		voiceName = self.getVoiceNameForLanguage(language)
		if voiceName:
			return self.getVoiceInstance(voiceName)
		return None

	def _getConfiguredVoiceNameForLanguage(self, language):
		if language in _config.vocalizerConfig['autoLanguageSwitching']:
			return _config.vocalizerConfig['autoLanguageSwitching'][language]['voice']
		return None

	def onVoiceLoad(self, voiceName, instance):
		""" Restores variant and other settings if available, when a voice is loaded."""
		_tuningData.onVoiceLoad(instance, voiceName)
		if voiceName in _config.vocalizerConfig['voices']:
			variant = _config.vocalizerConfig['voices'][voiceName]['variant']
			if variant is not None:
				_vocalizer.setParameter(instance, _vocalizer.VAUTO_PARAM_VOICE_MODEL, variant)

	def onVoiceUnload(self, voiceName, instance):
		""" Saves variant to be restored for each voice."""
		variant = _vocalizer.getParameter(instance, _vocalizer.VAUTO_PARAM_VOICE_MODEL, type_=str)
		if voiceName not in _config.vocalizerConfig['voices']:
			_config.vocalizerConfig['voices'][voiceName] = {}
		_config.vocalizerConfig['voices'][voiceName]['variant'] = variant

	def _localeGroupKey(self, localeName):
		if '_' in localeName:
			return localeName.split('_')[0]
		else:
			return localeName

	def getVoiceLanguage(self, voiceName=None):
		if voiceName is None:
			voiceName = self._defaultVoiceName
		return self._voiceInfos[voiceName].language

	def _makeVoiceInfo(self, v):
		localeName = self._languageNamesToLocales.get(v.szLanguage, None)
		langDescription = None
		# if we have the locale name use the localized language description from windows:
		if localeName is not None:
			langDescription = languageHandler.getLanguageDescription(localeName)
		if not langDescription:
			# For some languages (i.g. scotish english) windows doesn't gives us any description.
			# The synth returned something in english, it is better than nothing.
			langDescription = v.szLanguage
		name = "%s - %s" % (v.szVoiceName, langDescription)
		return VoiceInfo(v.szVoiceName, name, localeName or None)
