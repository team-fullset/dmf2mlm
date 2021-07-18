from enum import Enum, IntEnum
from .. import dmf
from ..defs import *
from .song import *

class SoundData:
	"""
	Contains everything to reproduce music and sound effects.
	Basically anything in the m1rom that isn't code nor LUTs.
	"""

	songs: [Song]

	def __init__(self):
		self.songs = []

	def from_dmf(modules: [dmf.Module]):
		self = SoundData()
		for mod in modules:
			self.songs.append(Song.from_dmf(mod))
		return self

	def compile(self) -> bytearray:
		header_size = len(self.songs) * 2 + 1
		comp_sdata = bytearray(header_size)
		head_ofs = 0

		comp_sdata[head_ofs] = len(self.songs)
		head_ofs += header_size # Leave space for MLM header

		for i in range(len(self.songs)):
			comp_song, song_ofs = self.songs[i].compile(head_ofs)
			comp_sdata[1 + i*2]     = song_ofs & 0xFF
			comp_sdata[1 + i*2 + 1] = song_ofs >> 8
			comp_sdata.extend(comp_song)
			head_ofs += len(comp_song)
		
		return comp_sdata