from ..defs import *
from dataclasses import dataclass
from typing import Optional

######################## EVENT & NOTES ########################

class SongEvent:
	timing: int = 0

	def compile(self, ch: int, ticks) -> bytearray:
		comp_data = bytearray()
		if isinstance(ticks, int):
			t = ticks
		else:
			t = self.timing
			

		while (t > 0):
			if t > 0x100:
				comp_data.append(0x04)            # Wait word command
				comp_data.append(t & 0xFF)        # ticks LSB
				comp_data.append((t >> 8) & 0xFF) # ticks MSB
				t -= 0xFFFF
			elif t > 0x10:
				comp_data.append(0x03)         # Wait byte command
				comp_data.append((t-1) & 0xFF) # ticks 
				t -= 0x100
			elif t > 0:
				comp_data.append(0x10 | ((t-1) & 0x0F)) # Wait nibble command
				t -= 0x10

		return comp_data

@dataclass
class SongNote(SongEvent):
	note: int # Can also be a sample id in ADPCM channels

	def compile(self, ch: int, _symbols: dict) -> bytearray:
		comp_data = bytearray(2)
		t = self.timing

		comp_data[0] = 0x80 | (t & 0x7F)
		comp_data[1] = self.note
		t -= 0x7F

		if t > 0:
			comp_waitcom_data = super(SongNote, self).compile(ch, t)
			comp_data.extend(comp_waitcom_data)

		return comp_data

######################## COMMANDS ########################

@dataclass
class SongCommand(SongEvent):
	pass

class SongComEOEL(SongCommand):
	"""
	Song Command End of Event List
	------------------------------
	ends the playback for the current channel
	"""
	pass

@dataclass
class SongComNoteOff(SongCommand):
	"""
	Song Command Note Off
	------------------------------
	Stops the channel's playing note/sample
	"""
	
	def compile(self, ch: int, _symbols: dict) -> bytearray:
		comp_data = bytearray(2)
		t = self.timing

		comp_data[0] = 0x01     # Note off command
		comp_data[1] = t & 0xFF
		t -= 0xFF

		if t > 0:
			comp_waitcom_data = super(SongNote, self).compile(ch, t)
			comp_data.extend(comp_waitcom_data)

		return comp_data

@dataclass
class SongComChangeInstrument(SongCommand):
	"""
	Song Command Change Instrument
	------------------------------
	Changes selected instrument
	"""
	instrument: int

	def compile(self, ch: int, _symbols: dict) -> bytearray:
		comp_data = bytearray(2)

		comp_data[0] = 0x02            # Change instrument command
		comp_data[1] = self.instrument

		if self.timing > 0:
			comp_waitcom_data = super(SongNote, self).compile(ch)
			comp_data.extend(comp_waitcom_data)

		return comp_data

@dataclass
class SongComWaitTicks(SongCommand):
	"""
	Song Command Wait Ticks
	------------------------------
	Just waits the specified amount,
	it will occupy 1, 2 or 3 bytes depending 
	on how much ticks need to be waited
	"""

@dataclass
class SongComSetChannelVol(SongCommand):
	"""
	Song Command Set Channel Volume
	------------------------------
	Sets the channel's volume
	"""
	volume: int

	def compile(self, ch: int, _symbols: dict) -> bytearray:
		comp_data = bytearray(2)

		comp_data[0] = 0x05        # Set channel volume command
		comp_data[1] = self.volume 

		if self.timing > 0:
			comp_waitcom_data = super(SongNote, self).compile(ch)
			comp_data.extend(comp_waitcom_data)

		return comp_data

class SongComSetPanning(SongCommand):
	"""
	Song Command Set Panning
	------------------------------
	Set's the ADPCM-A master volume
	"""
	panning: Panning

@dataclass
class SongComJumpToSubEL(SongCommand):
	"""
	Song Command Jump to Sub Event List
	------------------------------
	Jumps to sub event list. Doesn't allow nesting.
	"""
	sub_el_idx: int # index to Song.sub_event_lists

	def compile(self, ch: int, symbols: dict) -> bytearray:
		comp_data = bytearray()

		if self.timing > 0:
			comp_waitcom_data = super(SongNote, self).compile(ch)
			comp_data.extend(comp_waitcom_data)

		comp_data.append(0x20) # Return from SubEL command
		return comp_data

class SongComPositionJump(SongCommand):
	"""
	Song Command Position Jump
	------------------------------
	Jumps to a specific event in the current event list.
	It can be 2 bytes long (using an offset) or 3 bytes
	long (using a fixed address) depending on the size
	of the jump
	"""
	event_idx: int

class SongComPortamentoSlide(SongCommand):
	"""
	Song Command Portamento Slide
	------------------------------
	Still not implemented
	"""
	pitch_offset: int

class SongComYM2610PortWriteA(SongCommand):
	"""
	Song Command YM2610 Port Write A
	------------------------------
	Directly writes to the YM2610 registers
	using port A
	"""
	address: int
	data: int

class SongComYM2610PortWriteB(SongCommand):
	"""
	Song Command YM2610 Port Write B
	------------------------------
	Directly writes to the YM2610 registers
	using port B
	"""
	address: int
	data: int

class SongComSetTimerAFreq(SongCommand):
	"""
	Song Command Set Timer A Frequency
	------------------------------
	Sets the frequency of timer a
	"""
	frequency: int

@dataclass
class SongComReturnFromSubEL(SongCommand):
	"""
	Song Command Return from Sub Event List
	------------------------------
	Returns from Sub event list
	"""
	
	def compile(self, ch: int, _symbols: dict) -> bytearray:
		comp_data = bytearray()

		if self.timing > 0:
			comp_waitcom_data = super(SongNote, self).compile(ch)
			comp_data.extend(comp_waitcom_data)

		comp_data.append(0x20) # Return from SubEL command
		return comp_data