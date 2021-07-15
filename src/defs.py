from enum import Enum, IntEnum

M1ROM_SDATA_MAX_SIZE = 30 * 1024

class Panning(IntEnum):
	NONE   = 0x00
	RIGHT  = 0x40
	LEFT   = 0x80
	CENTER = 0xC0

class ChannelKind(IntEnum):
	ADPCMA = 0
	FM     = 1
	SSG    = 2