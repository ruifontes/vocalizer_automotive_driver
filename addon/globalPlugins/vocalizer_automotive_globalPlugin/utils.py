#vocalizer_globalPlugin/utils.py
#A part of the vocalizer driver for NVDA (Non Visual Desktop Access)
#Copyright (C) 2012 Rui Batista <ruiandrebatista@gmail.com>
#Copyright (C) 2012 - 2023 Tiflotecnia, lda. <www.tiflotecnia.net>
#This file is covered by the GNU General Public License.
#See the file GPL.txt for more details.

# Import the necessary modules
import synthDriverHandler


class VocalizerOpened(object):
	def __init__(self):
		self._opened = False
	def __enter__(self):
		from synthDrivers import vocalizerAutomotive
		from synthDrivers.vocalizerAutomotive import _vocalizer
		if synthDriverHandler.getSynth().name != vocalizerAutomotive.SynthDriver.name:
			try:
				_vocalizer.initialize()
				self._opened = True
			except _vocalizer.VautoError as e:
				if e.code not in(_vocalizer.NUAN_NVDA_DEMO_LICENSE_EXPIRED, _vocalizer.NUAN_INVALID_NVDA_LICENSE , _vocalizer.NUAN_ERROR_NVDA_LICENSE):
					raise
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		from synthDrivers import vocalizerAutomotive
		from synthDrivers.vocalizerAutomotive import _vocalizer
		if synthDriverHandler.getSynth().name != vocalizerAutomotive.SynthDriver.name and self._opened:
			try:
				_vocalizer.terminate()
			except _vocalizer.VautoError:
				pass
		return False

