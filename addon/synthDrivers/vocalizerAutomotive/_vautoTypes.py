#vocalizer/_vautoTypes.py
#A part of the vocalizer driver for NVDA (Non Visual Desktop Access)
#Copyright (C) 2012 Rui Batista <ruiandrebatista@gmail.com>
#Copyright (C) 2012 Tiflotecnia, lda. <www.tiflotecnia.com>
#This file is covered by the GNU General Public License.
#See the file GPL.txt for more details.

from ctypes import *


#Constant definitions
VAUTO_CURRENT_VERSION = 0x0520
VAUTO_MAX_STRING_LENGTH = 128
VPLATFORM_CURRENT_VERSION = 0x0100

# Error codes
NUAN_OK = 0
NUAN_E_TTS_USERSTOP = 0x80000807
NUAN_E_WRONG_STATE = 0x80000011
NUAN_E_NOTFOUND = 0x80000014

# NVDA license specific codes
NUAN_INVALID_NVDA_LICENSE = 0xf1
NUAN_ERROR_NVDA_LICENSE = 0xf2
NUAN_NVDA_DEMO_LICENSE_EXPIRED = 0xf3

# Text formats
VAUTO_NORM_TEXT = 0
VAUTO_HTML_TEXT = 1
VAUTO_XML_TEXT = 2

# Parameter ids
VAUTO_PARAM_FREQUENCY            = 1
VAUTO_PARAM_VOLUME               = 2
VAUTO_PARAM_SPEECHRATE           = 3
VAUTO_PARAM_PITCH                = 4
VAUTO_PARAM_WAITFACTOR           = 5
VAUTO_PARAM_READMODE             = 6
VAUTO_PARAM_LANGUAGE             = 7
VAUTO_PARAM_VOICE                = 8
VAUTO_PARAM_PPMODE               = 9
VAUTO_PARAM_MSGMODE              = 10
VAUTO_PARAM_TYPE_OF_CHAR         = 11
VAUTO_PARAM_MARKER_MODE          = 12
VAUTO_PARAM_INITMODE             = 13
VAUTO_PARAM_TEXTMODE             = 14
VAUTO_PARAM_LANGUAGE_NR          = 15
VAUTO_PARAM_DPLEX_MAXSIZE        = 16
VAUTO_PARAM_DPLEX_MAXMSGS        = 17
VAUTO_PARAM_MAX_INPUT_LENGTH     = 18
VAUTO_PARAM_VOICE_MODEL          = 19
VAUTO_PARAM_LIDSCOPE             = 20
VAUTO_PARAM_LIDVOICESWITCH       = 21
VAUTO_PARAM_EXTRAESCLANG         = 22
VAUTO_PARAM_EXTRAESCTN           = 23

# Init Modes
VAUTO_INITMODE_LOAD_ONCE_OPEN_ALL = 0xC
VAUTO_INITMODE_LOAD_OPEN_ALL_EACH_TIME = 0x3

# Text modes
VAUTO_TEXTMODE_STANDARD = 1
VAUTO_TEXTMODE_SMS = 2

# Marker modes
VAUTO_MRK_OFF = 0
VAUTO_MRK_ON = 1

# Message types
VAUTO_MSG_BEGINPROCESS   = 0x00000001
VAUTO_MSG_ENDPROCESS     = 0x00000002
VAUTO_MSG_INTEXTREQ      = 0x00000004
VAUTO_MSG_OUTBUFREQ      = 0x00000008
VAUTO_MSG_OUTBUFDONE     = 0x00000010
VAUTO_MSG_STOP           = 0x00000020
VAUTO_MSG_PAUSE          = 0x00000040
VAUTO_MSG_RESUME         = 0x00000080
VAUTO_MSG_BACKWARD       = 0x00000100
VAUTO_MSG_FORWARD        = 0x00000200
VAUTO_MSG_TEXTUNIT       = 0x00000400
VAUTO_MSG_WORD           = 0x00000800
VAUTO_MSG_PHONEME        = 0x00001000
VAUTO_MSG_BOOKMARK       = 0x00002000
VAUTO_MSG_ERROR          = 0x00004000
VAUTO_MSG_PROCESS        = 0x00008000
VAUTO_MSG_TAIBEGIN       = 0x00010000
VAUTO_MSG_TAIEND         = 0x00020000
VAUTO_MSG_TAIBUFREQ      = 0x00040000
VAUTO_MSG_TAIBUFDONE     = 0x00080000

# Mark types
VAUTO_MRK_BOOKMARK= 0x0008

# Character encodings
VAUTO_TYPE_OF_CHAR_UTF16   = 1
VAUTO_TYPE_OF_CHAR_UTF8    = 2

# Vocalizer gives  us sample rates in khz on an enumeration.
# We need those in hz, so this is the conversion table.
sampleRateConversions = {8 : 8000,
	11 : 11025,
	16 : 16000,
	22 : 22050}


	# type Definitions
class VAUTO_HSAFE(Structure):
	_fields_ = (('pHandleData', c_void_p),
	('u32Check', c_uint))
	def __eq__(self, other):
		return addressof(self) == addressof(other) or self.pHandleData == other.pHandleData

	def __hash__(self):
		return addressof(self) ^ self.pHandleData

class VAUTO_INSTALL(Structure):
	_fields_ = (('fmtVersion', c_ushort),
	('pBinBrokerInfo', c_char_p),
	('pIHeap', c_void_p),
	('hHeap', c_void_p),
	('pICritSec', c_void_p),
	('hCSClass', c_void_p),
	('pIDataStream', c_void_p),
	('pIDataMapping', c_void_p),
	('hDataClass', c_void_p),
	('pILog', c_void_p),
	('hLog', c_void_p))

class VPLATFORM_MEMBLOCK(Structure):
	_fields_ = [('start', c_void_p),
	('cByte', c_uint)]

class VPLATFORM_RESOURCES(Structure):
	_fields_ = (('fmtVersion', c_ushort),
	('u16NbrOfDataInstall', c_ushort),
	('apDataInstall', POINTER(c_wchar_p)),
	('stHeap', VPLATFORM_MEMBLOCK),
	('nvdaConfigDir', c_wchar_p),
	('pDatPtr_Table', c_void_p))

class VAUTO_INTEXT(Structure):
	_fields_ = (('eTextFormat;  ', c_int),
	('ulTextLength', c_uint),
	('szInText', c_void_p))

class VAUTO_LPARAM(Union):
	_fields_ = (('lValue', c_uint),
	('lError', c_uint))

class VAUTO_PARAM_VALUE(Union):
	_fields_ = (('usValue', c_ushort),
	('szValue', (c_wchar * VAUTO_MAX_STRING_LENGTH)))

class VAUTO_PARAM(Structure):
	_fields_ = (('ID', c_uint),
	('uValue', VAUTO_PARAM_VALUE))

class VAUTO_CALLBACKMSG(Structure):
	_fields_ = (('eMessage', c_uint),
	('uParam', VAUTO_LPARAM),
	('pParam', c_void_p))

VAUTO_CBOUTNOTIFY = CFUNCTYPE(c_uint, VAUTO_HSAFE, c_void_p, POINTER(VAUTO_CALLBACKMSG), c_void_p)

class VAUTO_OUTDEVINFO(Structure):
	_fields_ = (('hOutDevInstance', c_void_p),
	('pfOutNotify', VAUTO_CBOUTNOTIFY))

class VAUTO_LANGUAGE(Structure):
	_fields_ = (('szLanguage', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szLanguageTLW', (c_wchar * 4)),
	('szVersion', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('u16LangId', c_ushort))

class VAUTO_VOICEINFO(Structure):
	_fields_ = (('szVersion', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szLanguage', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szVoiceName', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szVoiceAge', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szVoiceType', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('u16LangId', c_ushort))

	def __eq__(self, other):
		return isinstance(other, type(self)) and addressof(self) == addressof(other)

class VAUTO_SPEECHDBINFO(Structure):
	_fields_ = (('szVersion', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szLanguage', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szVoiceName', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('szVoiceModel', (c_wchar * VAUTO_MAX_STRING_LENGTH)),
	('u16Freq', c_ushort),
	('u16LangId', c_ushort))

class VAUTO_MARKINFO(Structure):
	_fields_ = [('ulMrkInfo', c_uint),
	('eMrkType', c_uint),
	('ulSrcPos', c_uint),
	('ulSrcTextLen', c_uint),
	('ulDestPos', c_uint),
	('ulDestLen', c_uint),
	('usPhoneme', c_ushort),
	('ulMrkId', c_uint),
	('ulParam', c_uint),
	('szPromptID', c_char_p)]

class VAUTO_OUTDATA(Structure):
	_fields_ = (('eAudioFormat', c_uint),
	('ulPcmBufLen', c_uint),
	('pOutPcmBuf', c_void_p),
	('ulMrkListLen', c_uint),
	('pMrkList', POINTER(VAUTO_MARKINFO)))


	# FIXME:: remove this definitions if sure that don't need them anymore
# Nuance logging facilities sufix for our debugging purposes.
pfErrorFuncType = CFUNCTYPE(None, VAUTO_HSAFE, c_uint, c_uint, POINTER(c_char_p), POINTER(c_char_p))
pfDiagnosticFuncType = CFUNCTYPE(None, VAUTO_HSAFE, c_uint, c_char_p)
class VAUTO_LOG_INTERFACE_S(Structure):
	_fields_ = [('pfError', pfErrorFuncType),
	('pfDiagnostic', pfDiagnosticFuncType)]

# Error handling
class VautoError(RuntimeError):
	def __init__(self, code, msg):
		self.code = code
		super(RuntimeError, self).__init__(msg)

def vautoCheckForError(result, func, args):
	""" Checks for errors in a function from the vocalizer dlls and platform.
	
	If the error code is not positive it throws a runtime error.
	The error codes have no description, see the vocalizer SDK
	For reference."""
	if result  not in (NUAN_OK, NUAN_E_TTS_USERSTOP):
		raise VautoError(result, "Vocalizer Error: %s: %x" %(func.__name__, result))

# Load Libraries
def loadVautoDll(path):
	vautoDll = cdll.LoadLibrary(path)
	# Basic runtime type checks...
	vautoDll.vauto_ttsInitialize.errcheck = vautoCheckForError
	vautoDll.vauto_ttsInitialize.restype = c_uint
	vautoDll.vauto_ttsOpen.errcheck = vautoCheckForError
	vautoDll.vauto_ttsOpen.restype = c_uint
	vautoDll.vauto_ttsOpen.argtypes = (VAUTO_HSAFE, c_void_p, c_void_p, POINTER(VAUTO_HSAFE), c_void_p)
	vautoDll.vauto_ttsProcessText2Speech.errcheck = vautoCheckForError
	vautoDll.vauto_ttsProcessText2Speech.restype = c_uint
	vautoDll.vauto_ttsStop.errcheck = vautoCheckForError
	vautoDll.vauto_ttsStop.restype = c_uint
	vautoDll.vauto_ttsPause.errcheck = vautoCheckForError
	vautoDll.vauto_ttsPause.restype = c_uint
	vautoDll.vauto_ttsResume.errcheck = vautoCheckForError
	vautoDll.vauto_ttsResume.restype = c_uint
	vautoDll.vauto_ttsSetParamList.errcheck = vautoCheckForError
	vautoDll.vauto_ttsSetParamList.restype = c_uint
	vautoDll.vauto_ttsGetParamList.errcheck = vautoCheckForError
	vautoDll.vauto_ttsGetParamList.restype = c_uint
	vautoDll.vauto_ttsGetLanguageList.errcheck = vautoCheckForError
	vautoDll.vauto_ttsGetLanguageList.restype = c_uint
	vautoDll.vauto_ttsGetVoiceList.restype = c_uint
	vautoDll.vauto_ttsGetVoiceList.errcheck = vautoCheckForError
	vautoDll.vauto_ttsGetSpeechDBList.restype = c_uint
	vautoDll.vauto_ttsGetSpeechDBList.errcheck = vautoCheckForError
	vautoDll.vauto_ttsClose.restype = c_uint
	vautoDll.vauto_ttsClose.errcheck = vautoCheckForError
	vautoDll.vauto_ttsUnInitialize.restype = c_uint
	vautoDll.vauto_ttsUnInitialize.errcheck = vautoCheckForError
	vautoDll.vauto_ttsSetOutDevice.errcheck = vautoCheckForError
	vautoDll.vauto_ttsSetOutDevice.restype = c_uint
	vautoDll.vauto_ttsResourceLoad.errcheck = vautoCheckForError
	vautoDll.vauto_ttsResourceLoad.restype = c_uint
	return vautoDll

def loadPlatformDll(path):
	platformDll = cdll.LoadLibrary(path)
	platformDll.vplatform_GetInterfaces.errcheck = vautoCheckForError
	platformDll.vplatform_GetInterfaces.restype = c_uint
	platformDll.vplatform_GetInterfaces.argtypes = (POINTER(VAUTO_INSTALL), POINTER(VPLATFORM_RESOURCES))
	platformDll.vplatform_ReleaseInterfaces.errcheck = vautoCheckForError
	platformDll.vplatform_ReleaseInterfaces.restype = c_uint
	platformDll.VAUTONVDA_getLicenseInfo.restype = c_wchar_p
	return platformDll
