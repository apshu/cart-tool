#   Python adaptation of Atari 8bit cartridge information based on
#	Altirra - Atari 800/800XL/5200 emulator
#	I/O library - cartridge type utils
#	Copyright (C) 2009-2016 Avery Lee
#
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from dataclasses import dataclass, field
from enum import IntEnum, unique, auto, IntFlag
import struct
import itertools as it

from unicodedata import category


@unique
class SystemType(IntEnum):
    kType800 = 0
    kType5200 = auto()


@unique
class SizeType(IntFlag):
    kSize2K = 1
    kSize4K = 2
    kSize8K = 4
    kSize16K = 8
    kSize32K = 16
    kSize40K = 32
    kSize64K = 64
    kSize128K = 128
    kSize256K = 256
    kSize512K = 512
    kSize1M = 1024
    kSize2M = 2048
    kSize4M = 0x1000
    kSize32M = 0x2000
    kSize64M = 0x4000
    kSize128M = 0x8000


class WritableStoreType(IntEnum):
    kWrsNone = 0
    kWrs256B = auto()
    kWrs8K = auto()


class BankingType(IntEnum):
    kBankNone = 0
    kBankData = auto()
    kBankDataSw = auto()
    kBankAddr = auto()
    kBankAddrSw = auto()
    kBankAddr7x = auto()
    kBankAddrDx = auto()
    kBankAddrEx = auto()
    kBankAddrEFx = auto()
    kBankAny = auto()
    kBankBF = auto()
    kBankOther = auto()


class InitRange(IntEnum):
    kInit2K = 0
    kInit4K = auto()
    kInit8K = auto()
    kInit8KR = auto()
    kInit16K = auto()
    kInit32K = auto()


class HeaderType(IntEnum):
    kHeaderFirst4K = 0
    kHeaderFirst8K = auto()
    kHeaderFirst8K_PreferAll8K = auto()
    kHeaderFirst16K = auto()
    kHeaderFirst16K_PreferAll16K = auto()
    kHeaderFirst32K = auto()
    kHeaderLast32K = auto()
    kHeaderLast16B = auto()
    kHeaderLast8K_PreferAll8K = auto()


class ATCartridgeMode(IntEnum):
    Mode_None = 0
    Mode_8K = 1
    Mode_16K = 2
    Mode_OSS_034M = 3
    Mode_5200_32K = 4
    Mode_DB_32K = 5
    Mode_5200_16K_TwoChip = 6
    Mode_BountyBob5200 = 7
    Mode_Williams_64K = 8
    Mode_Express_64K = 9
    Mode_Diamond_64K = 10
    Mode_SpartaDosX_64K = 11
    Mode_XEGS_32K = 12
    Mode_XEGS_64K = 13
    Mode_XEGS_128K = 14
    Mode_OSS_M091 = 15
    Mode_5200_16K_OneChip = 16
    Mode_Atrax_128K = 17
    Mode_BountyBob800 = 18
    Mode_5200_8K = 19
    Mode_5200_4K = 20
    Mode_RightSlot_8K = 21
    Mode_Williams_32K = 22
    Mode_XEGS_256K = 23
    Mode_XEGS_512K = 24
    Mode_XEGS_1M = 25
    Mode_MegaCart_16K = 26
    Mode_MegaCart_32K = 27
    Mode_MegaCart_64K = 28
    Mode_MegaCart_128K = 29
    Mode_MegaCart_256K = 30
    Mode_MegaCart_512K = 31
    Mode_MegaCart_1M = 32
    Mode_Switchable_XEGS_32K = 33
    Mode_Switchable_XEGS_64K = 34
    Mode_Switchable_XEGS_128K = 35
    Mode_Switchable_XEGS_256K = 36
    Mode_Switchable_XEGS_512K = 37
    Mode_Switchable_XEGS_1M = 38
    Mode_Phoenix_8K = 39
    Mode_Blizzard_16K = 40
    Mode_MaxFlash_128K = 41
    Mode_MaxFlash_1024K = 42
    Mode_SpartaDosX_128K = 43
    Mode_OSS_8K = 44
    Mode_OSS_043M = 45
    Mode_Blizzard_4K = 46
    Mode_AST_32K = 47
    Mode_Atrax_SDX_64K = 48
    Mode_Atrax_SDX_128K = 49
    Mode_Turbosoft_64K = 50
    Mode_Turbosoft_128K = 51
    Mode_MicroCalc = 52
    Mode_RightSlot_8K_alt = 53
    Mode_SIC_128K = 54
    Mode_SIC_256K = 55
    Mode_SIC_512K = 56
    Mode_2K = 57
    Mode_4K = 58
    Mode_RightSlot_4K = 59
    Mode_Blizzard_32K = 60
    Mode_MegaMax_2M = 61
    Mode_TheCart_128M = 62
    Mode_MegaCart_4M_3 = 63
    Mode_MegaCart_2M = 64
    Mode_TheCart_32M = 65
    Mode_TheCart_64M = 66
    Mode_XEGS_64K_Alt = 67
    Mode_Atrax_128K_Raw = 68
    Mode_aDawliah_32K = 69
    Mode_aDawliah_64K = 70
    Mode_5200_64K_32KBanks = 71  # Used by M.U.L.E. 64K conversion
    Mode_5200_128K_32KBanks = 72
    Mode_5200_256K_32KBanks = 73
    Mode_5200_512K_32KBanks = 74
    Mode_MaxFlash_1024K_Bank0 = 75
    Mode_Williams_16K = 76
    Mode_TelelinkII = 78
    Mode_Pronto = 79
    Mode_JRC_RAMBOX = 80
    Mode_MDDOS = 81
    Mode_COS32K = 82
    Mode_SICPlus = 83
    Mode_Corina_1M_EEPROM = 84
    Mode_Corina_512K_SRAM_EEPROM = 85
    Mode_XEMulticart_8K = 86  # XE Multicart by Idorobots (Kajetan Rzepecki)
    Mode_XEMulticart_16K = 87
    Mode_XEMulticart_32K = 88
    Mode_XEMulticart_64K = 89
    Mode_XEMulticart_128K = 90
    Mode_XEMulticart_256K = 91
    Mode_XEMulticart_512K = 92
    Mode_XEMulticart_1M = 93
    Mode_JRC6_64K = 160  # (unofficial type 160 used by AVGCart)
    Mode_MegaCart_1M_2 = Mode_MegaCart_1M  # Hardware by Bernd for ABBUC JHV 2009
    Mode_BountyBob5200Alt = Mode_BountyBob5200  # Same as cart mapper 7 except that the fixed bank is first.
    Mode_MaxFlash_128K_MyIDE = 1000
    Mode_MegaCart_512K_3 = 1001
    Mode_Unknown = -1

    @property
    def is_virtual(self):
        return self < 0 or self > 255 or self in (self.Mode_Unknown, self.Mode_None)

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            try:
                return cls(int(value, 0))
            except ValueError:
                # It was not an integer
                pass
        return cls[value]


class ATCartDetectFlags(IntEnum):
    NoDetect = 0
    DontRecommend = 1


# Instantiate based on CART type
class ATCartridgeInfo(IntEnum):
    Mode_None = (ATCartridgeMode.Mode_None, SystemType.kType800, SizeType.kSize2K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit2K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x0000, "No cartridge")  # Mode_None
    Mode_2K = (ATCartridgeMode.Mode_2K, SystemType.kType800, SizeType.kSize2K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit2K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x0800, "2K")  # Mode_2K
    Mode_4K = (ATCartridgeMode.Mode_4K, SystemType.kType800, SizeType.kSize4K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit4K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x1000, "4K")  # Mode_4K
    Mode_8K = (ATCartridgeMode.Mode_8K, SystemType.kType800, SizeType.kSize2K | SizeType.kSize4K | SizeType.kSize8K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x2000,
               "8K")  # Mode_8K
    Mode_16K = (ATCartridgeMode.Mode_16K, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x4000, "16K")  # Mode_16K
    Mode_XEGS_32K = (
        ATCartridgeMode.Mode_XEGS_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x8000, "32K XEGS")  # Mode_XEGS_32K
    Mode_XEGS_64K = (
        ATCartridgeMode.Mode_XEGS_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x10000, "64K XEGS")  # Mode_XEGS_64K
    Mode_XEGS_64K_Alt = (ATCartridgeMode.Mode_XEGS_64K_Alt, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x10000,
                         "XEGS 64K (alternate)")  # Mode_XEGS_64K_Alt
    Mode_XEGS_128K = (
        ATCartridgeMode.Mode_XEGS_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x20000, "128K XEGS")  # Mode_XEGS_128K
    Mode_XEGS_256K = (
        ATCartridgeMode.Mode_XEGS_256K, SystemType.kType800, SizeType.kSize256K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x40000, "256K XEGS")  # Mode_XEGS_256K
    Mode_XEGS_512K = (
        ATCartridgeMode.Mode_XEGS_512K, SystemType.kType800, SizeType.kSize512K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x80000, "512K XEGS")  # Mode_XEGS_512K
    Mode_XEGS_1M = (ATCartridgeMode.Mode_XEGS_1M, SystemType.kType800, SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x100000, "1M XEGS")  # Mode_XEGS_1M
    Mode_Switchable_XEGS_32K = (ATCartridgeMode.Mode_Switchable_XEGS_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x8000,
                                "32K Switchable XEGS")  # Mode_Switchable_XEGS_32K
    Mode_Switchable_XEGS_64K = (ATCartridgeMode.Mode_Switchable_XEGS_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x10000,
                                "64K Switchable XEGS")  # Mode_Switchable_XEGS_64K
    Mode_Switchable_XEGS_128K = (
        ATCartridgeMode.Mode_Switchable_XEGS_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x20000,
        "128K Switchable XEGS")  # Mode_Switchable_XEGS_128K
    Mode_Switchable_XEGS_256K = (
        ATCartridgeMode.Mode_Switchable_XEGS_256K, SystemType.kType800, SizeType.kSize256K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x40000,
        "256K Switchable XEGS")  # Mode_Switchable_XEGS_256K
    Mode_Switchable_XEGS_512K = (
        ATCartridgeMode.Mode_Switchable_XEGS_512K, SystemType.kType800, SizeType.kSize512K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x80000,
        "512K Switchable XEGS")  # Mode_Switchable_XEGS_512K
    Mode_Switchable_XEGS_1M = (ATCartridgeMode.Mode_Switchable_XEGS_1M, SystemType.kType800, SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x100000,
                               "1M Switchable XEGS")  # Mode_Switchable_XEGS_1M
    Mode_MaxFlash_128K = (ATCartridgeMode.Mode_MaxFlash_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankAddrSw, InitRange.kInit8K, HeaderType.kHeaderFirst8K_PreferAll8K, ATCartDetectFlags.NoDetect, 0x20000,
                          "MaxFlash 128K / 1Mbit")  # Mode_MaxFlash_128K
    Mode_MaxFlash_128K_MyIDE = (
        ATCartridgeMode.Mode_MaxFlash_128K_MyIDE, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankAddrSw, InitRange.kInit8K, HeaderType.kHeaderFirst8K_PreferAll8K, ATCartDetectFlags.NoDetect, 0x20000,
        "MaxFlash 128K + MyIDE")  # Mode_MaxFlash_128K_MyIDE
    Mode_MaxFlash_1024K = (ATCartridgeMode.Mode_MaxFlash_1024K, SystemType.kType800, SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankAddrSw, InitRange.kInit8K, HeaderType.kHeaderLast8K_PreferAll8K, ATCartDetectFlags.NoDetect, 0x100000,
                           "MaxFlash 1M / 8Mbit - older (bank 127)")  # Mode_MaxFlash_1024K
    Mode_MaxFlash_1024K_Bank0 = (
        ATCartridgeMode.Mode_MaxFlash_1024K_Bank0, SystemType.kType800, SizeType.kSize256K | SizeType.kSize512K | SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankAddrSw, InitRange.kInit8K, HeaderType.kHeaderFirst8K_PreferAll8K,
        ATCartDetectFlags.NoDetect, 0x100000, "MaxFlash 1M / 8Mbit - newer (bank 0)")  # Mode_MaxFlash_1024K_Bank0
    Mode_MegaCart_16K = (ATCartridgeMode.Mode_MegaCart_16K, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x4000,
                         "16K MegaCart")  # Mode_MegaCart_16K
    Mode_MegaCart_32K = (ATCartridgeMode.Mode_MegaCart_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x8000,
                         "32K MegaCart")  # Mode_MegaCart_32K
    Mode_MegaCart_64K = (ATCartridgeMode.Mode_MegaCart_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x10000,
                         "64K MegaCart")  # Mode_MegaCart_64K
    Mode_MegaCart_128K = (
        ATCartridgeMode.Mode_MegaCart_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x20000,
        "128K MegaCart")  # Mode_MegaCart_128K
    Mode_MegaCart_256K = (
        ATCartridgeMode.Mode_MegaCart_256K, SystemType.kType800, SizeType.kSize256K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x40000,
        "256K MegaCart")  # Mode_MegaCart_256K
    Mode_MegaCart_512K = (
        ATCartridgeMode.Mode_MegaCart_512K, SystemType.kType800, SizeType.kSize512K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x80000,
        "512K MegaCart")  # Mode_MegaCart_512K
    Mode_MegaCart_1M = (ATCartridgeMode.Mode_MegaCart_1M, SystemType.kType800, SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x100000,
                        "1M MegaCart")  # Mode_MegaCart_1M
    Mode_MegaCart_2M = (ATCartridgeMode.Mode_MegaCart_2M, SystemType.kType800, SizeType.kSize2M, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x200000,
                        "2M MegaCart")  # Mode_MegaCart_2M
    Mode_BountyBob800 = (ATCartridgeMode.Mode_BountyBob800, SystemType.kType800, SizeType.kSize40K, WritableStoreType.kWrsNone, BankingType.kBankOther, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0xA000,
                         "Bounty Bob (800)")  # Mode_BountyBob800
    Mode_OSS_034M = (
        ATCartridgeMode.Mode_OSS_034M, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x4000, "OSS '034M'")  # Mode_OSS_034M
    Mode_OSS_M091 = (
        ATCartridgeMode.Mode_OSS_M091, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst4K, ATCartDetectFlags.NoDetect, 0x4000, "OSS 'M091'")  # Mode_OSS_M091
    Mode_OSS_043M = (
        ATCartridgeMode.Mode_OSS_043M, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x4000, "OSS '043M'")  # Mode_OSS_043M
    Mode_OSS_8K = (ATCartridgeMode.Mode_OSS_8K, SystemType.kType800, SizeType.kSize8K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst4K, ATCartDetectFlags.NoDetect, 0x2000, "OSS 8K")  # Mode_OSS_8K
    Mode_Corina_1M_EEPROM = (ATCartridgeMode.Mode_Corina_1M_EEPROM, SystemType.kType800, SizeType.kSize1M, WritableStoreType.kWrs8K, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x102000,
                             "Corina 1M + 8K EEPROM")  # Mode_Corina_1M_EEPROM
    Mode_Corina_512K_SRAM_EEPROM = (
        ATCartridgeMode.Mode_Corina_512K_SRAM_EEPROM, SystemType.kType800, SizeType.kSize512K, WritableStoreType.kWrs8K, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x82000,
        "Corina 512K + 512K SRAM + 8K EEPROM")  # Mode_Corina_512K_SRAM_EEPROM
    Mode_BountyBob5200 = (ATCartridgeMode.Mode_BountyBob5200, SystemType.kType5200, SizeType.kSize40K, WritableStoreType.kWrsNone, BankingType.kBankOther, InitRange.kInit32K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0xA000,
                          "Bounty Bob (5200)")  # Mode_BountyBob5200
    Mode_BountyBob5200Alt = (ATCartridgeMode.Mode_BountyBob5200Alt, SystemType.kType5200, SizeType.kSize40K, WritableStoreType.kWrsNone, BankingType.kBankOther, InitRange.kInit32K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0xA000,
                             "Bounty Bob (5200) - Alternate layout")  # Mode_BountyBob5200Alt
    Mode_Williams_16K = (
        ATCartridgeMode.Mode_Williams_16K, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x4000,
        "Williams 16K")  # Mode_Williams_16K
    Mode_Williams_32K = (
        ATCartridgeMode.Mode_Williams_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x8000,
        "Williams 32K")  # Mode_Williams_32K
    Mode_Williams_64K = (
        ATCartridgeMode.Mode_Williams_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x10000,
        "Williams 64K")  # Mode_Williams_64K
    Mode_Diamond_64K = (
        ATCartridgeMode.Mode_Diamond_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x10000,
        "Diamond 64K")  # Mode_Diamond_64K
    Mode_Express_64K = (
        ATCartridgeMode.Mode_Express_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddr7x, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x10000,
        "Express 64K")  # Mode_Express_64K
    Mode_SpartaDosX_64K = (ATCartridgeMode.Mode_SpartaDosX_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddrEx, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x10000,
                           "SpartaDOS X 64K")  # Mode_SpartaDosX_64K
    Mode_SpartaDosX_128K = (ATCartridgeMode.Mode_SpartaDosX_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankAddrEFx, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x20000,
                            "SpartaDOS X 128K")  # Mode_SpartaDosX_128K
    Mode_Atrax_SDX_128K = (ATCartridgeMode.Mode_Atrax_SDX_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankAddrEFx, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x20000,
                           "Atrax SDX 128K")  # Mode_Atrax_SDX_128K
    Mode_Atrax_SDX_64K = (ATCartridgeMode.Mode_Atrax_SDX_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddrEx, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x10000,
                          "Atrax SDX 64K")  # Mode_Atrax_SDX_64K
    Mode_TelelinkII = (
        ATCartridgeMode.Mode_TelelinkII, SystemType.kType800, SizeType.kSize8K, WritableStoreType.kWrs256B, BankingType.kBankNone, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x2100, "8K Telelink II")  # Mode_TelelinkII
    Mode_RightSlot_4K = (
        ATCartridgeMode.Mode_RightSlot_4K, SystemType.kType800, SizeType.kSize4K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit8KR, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x1000,
        "Right slot 4K")  # Mode_RightSlot_4K
    Mode_RightSlot_8K = (
        ATCartridgeMode.Mode_RightSlot_8K, SystemType.kType800, SizeType.kSize8K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit8KR, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x2000,
        "Right slot 8K")  # Mode_RightSlot_8K
    Mode_RightSlot_8K_alt = (ATCartridgeMode.Mode_RightSlot_8K_alt, SystemType.kType800, SizeType.kSize8K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit8KR, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x2000,
                             "Right slot 8K (alternative)")  # Mode_RightSlot_8K_alt
    Mode_DB_32K = (ATCartridgeMode.Mode_DB_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x8000, "DB 32K")  # Mode_DB_32K
    Mode_Atrax_128K = (ATCartridgeMode.Mode_Atrax_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x20000,
                       "Atrax 128K (decoded order)")  # Mode_Atrax_128K
    Mode_Atrax_128K_Raw = (ATCartridgeMode.Mode_Atrax_128K_Raw, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.DontRecommend, 0x20000,
                           "Atrax 128K (raw order)")  # Mode_Atrax_128K_Raw
    Mode_Phoenix_8K = (
        ATCartridgeMode.Mode_Phoenix_8K, SystemType.kType800, SizeType.kSize8K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x2000, "Phoenix 8K")  # Mode_Phoenix_8K
    Mode_Blizzard_32K = (
        ATCartridgeMode.Mode_Blizzard_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit32K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x8000,
        "Blizzard 32K")  # Mode_Blizzard_32K
    Mode_Blizzard_16K = (
        ATCartridgeMode.Mode_Blizzard_16K, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x4000,
        "Blizzard 16K")  # Mode_Blizzard_16K
    Mode_Blizzard_4K = (
        ATCartridgeMode.Mode_Blizzard_4K, SystemType.kType800, SizeType.kSize4K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x1000, "Blizzard 4K")  # Mode_Blizzard_4K
    Mode_SIC_128K = (ATCartridgeMode.Mode_SIC_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x20000,
                     "SIC! 128K")  # Mode_SIC_128K
    Mode_SIC_256K = (ATCartridgeMode.Mode_SIC_256K, SystemType.kType800, SizeType.kSize256K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x40000,
                     "SIC! 256K")  # Mode_SIC_256K
    Mode_SIC_512K = (ATCartridgeMode.Mode_SIC_512K, SystemType.kType800, SizeType.kSize512K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x80000,
                     "SIC! 512K")  # Mode_SIC_512K
    Mode_AST_32K = (ATCartridgeMode.Mode_AST_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x8000, "AST 32K")  # Mode_AST_32K
    Mode_Turbosoft_64K = (ATCartridgeMode.Mode_Turbosoft_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x10000,
                          "Turbosoft 64K")  # Mode_Turbosoft_64K
    Mode_Turbosoft_128K = (ATCartridgeMode.Mode_Turbosoft_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x20000,
                           "Turbosoft 128K")  # Mode_Turbosoft_128K
    Mode_MegaCart_1M_2 = (
        ATCartridgeMode.Mode_MegaCart_1M_2, SystemType.kType800, SizeType.kSize256K | SizeType.kSize512K | SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit8K, HeaderType.kHeaderFirst8K,
        ATCartDetectFlags.NoDetect,
        0x100000, "Megacart 1M (2)")  # Mode_MegaCart_1M_2
    Mode_MegaCart_512K_3 = (ATCartridgeMode.Mode_MegaCart_512K_3, SystemType.kType800, SizeType.kSize512K, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x80000,
                            "MegaCart 512K (3)")  # Mode_MegaCart_512K_3
    Mode_MegaCart_4M_3 = (ATCartridgeMode.Mode_MegaCart_4M_3, SystemType.kType800, SizeType.kSize4M, WritableStoreType.kWrsNone, BankingType.kBankDataSw, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x400000,
                          "MegaCart 4M (3)")  # Mode_MegaCart_4M_3
    Mode_MicroCalc = (
        ATCartridgeMode.Mode_MicroCalc, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x8000, "MicroCalc 32K")  # Mode_MicroCalc
    Mode_MegaMax_2M = (ATCartridgeMode.Mode_MegaMax_2M, SystemType.kType800, SizeType.kSize2M, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit16K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x200000,
                       "MegaMax 2M")  # Mode_MegaMax_2M
    Mode_TheCart_32M = (
        ATCartridgeMode.Mode_TheCart_32M, SystemType.kType800, SizeType.kSize32M, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x2000000,
        "The!Cart 32M")  # Mode_TheCart_32M
    Mode_TheCart_64M = (
        ATCartridgeMode.Mode_TheCart_64M, SystemType.kType800, SizeType.kSize64M, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x4000000,
        "The!Cart 64M")  # Mode_TheCart_64M
    Mode_TheCart_128M = (ATCartridgeMode.Mode_TheCart_128M, SystemType.kType800, SizeType.kSize128M, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.NoDetect, 0x8000000,
                         "The!Cart 128M")  # Mode_TheCart_128M
    Mode_aDawliah_32K = (ATCartridgeMode.Mode_aDawliah_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.DontRecommend, 0x8000,
                         "aDawliah 32K")  # Mode_aDawliah_32K
    Mode_aDawliah_64K = (ATCartridgeMode.Mode_aDawliah_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAny, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.DontRecommend, 0x10000,
                         "aDawliah 64K")  # Mode_aDawliah_64K
    Mode_JRC6_64K = (
        ATCartridgeMode.Mode_JRC6_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderLast16B, ATCartDetectFlags.DontRecommend, 0x10000, "JRC 64K")  # Mode_JRC6_64K
    Mode_JRC_RAMBOX = (
        ATCartridgeMode.Mode_JRC_RAMBOX, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderFirst8K, ATCartDetectFlags.DontRecommend, 0x10000,
        "JRC RAMBOX")  # Mode_JRC_RAMBOX
    Mode_XEMulticart_8K = (ATCartridgeMode.Mode_XEMulticart_8K, SystemType.kType800, SizeType.kSize8K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x2000,
                           "XE Multicart (8K)")  # Mode_XEMulticart_8K
    Mode_XEMulticart_16K = (ATCartridgeMode.Mode_XEMulticart_16K, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x4000,
                            "XE Multicart (16K)")  # Mode_XEMulticart_16K
    Mode_XEMulticart_32K = (ATCartridgeMode.Mode_XEMulticart_32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x8000,
                            "XE Multicart (32K)")  # Mode_XEMulticart_32K
    Mode_XEMulticart_64K = (ATCartridgeMode.Mode_XEMulticart_64K, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x10000,
                            "XE Multicart (64K)")  # Mode_XEMulticart_64K
    Mode_XEMulticart_128K = (ATCartridgeMode.Mode_XEMulticart_128K, SystemType.kType800, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x20000,
                             "XE Multicart (128K)")  # Mode_XEMulticart_128K
    Mode_XEMulticart_256K = (ATCartridgeMode.Mode_XEMulticart_256K, SystemType.kType800, SizeType.kSize256K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x40000,
                             "XE Multicart (256K)")  # Mode_XEMulticart_256K
    Mode_XEMulticart_512K = (ATCartridgeMode.Mode_XEMulticart_512K, SystemType.kType800, SizeType.kSize512K, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x80000,
                             "XE Multicart (512K)")  # Mode_XEMulticart_512K
    Mode_XEMulticart_1M = (ATCartridgeMode.Mode_XEMulticart_1M, SystemType.kType800, SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankAddrDx, InitRange.kInit16K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x100000,
                           "XE Multicart (1MB)")  # Mode_XEMulticart_1M
    Mode_SICPlus = (
        ATCartridgeMode.Mode_SICPlus, SystemType.kType800, SizeType.kSize1M, WritableStoreType.kWrsNone, BankingType.kBankData, InitRange.kInit8K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.NoDetect, 0x100000, "SIC+")  # Mode_SICPlus
    Mode_MDDOS = (
        ATCartridgeMode.Mode_MDDOS, SystemType.kType800, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankAddr, InitRange.kInit8K, HeaderType.kHeaderFirst16K_PreferAll16K, ATCartDetectFlags.DontRecommend, 0x10000,
        "MDDOS")  # Mode_MDDOS
    Mode_COS32K = (
        ATCartridgeMode.Mode_COS32K, SystemType.kType800, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit16K, HeaderType.kHeaderFirst16K, ATCartDetectFlags.DontRecommend, 0x8000, "COS 32K")  # Mode_COS32K
    Mode_Pronto = (
        ATCartridgeMode.Mode_Pronto, SystemType.kType800, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit16K, HeaderType.kHeaderFirst16K, ATCartDetectFlags.DontRecommend, 0x4000, "Pronto")  # Mode_Pronto
    Mode_5200_32K = (
        ATCartridgeMode.Mode_5200_32K, SystemType.kType5200, SizeType.kSize32K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit32K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x8000, "5200 32K")  # Mode_5200_32K
    Mode_5200_16K_TwoChip = (ATCartridgeMode.Mode_5200_16K_TwoChip, SystemType.kType5200, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit32K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x4000,
                             "5200 16K (two chip)")  # Mode_5200_16K_TwoChip
    Mode_5200_16K_OneChip = (ATCartridgeMode.Mode_5200_16K_OneChip, SystemType.kType5200, SizeType.kSize16K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit32K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x4000,
                             "5200 16K (one chip)")  # Mode_5200_16K_OneChip
    Mode_5200_8K = (ATCartridgeMode.Mode_5200_8K, SystemType.kType5200, SizeType.kSize8K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit32K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x2000, "5200 8K")  # Mode_5200_8K
    Mode_5200_4K = (ATCartridgeMode.Mode_5200_4K, SystemType.kType5200, SizeType.kSize4K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit32K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x1000, "5200 4K")  # Mode_5200_4K
    Mode_5200_64K_32KBanks = (ATCartridgeMode.Mode_5200_64K_32KBanks, SystemType.kType5200, SizeType.kSize64K, WritableStoreType.kWrsNone, BankingType.kBankBF, InitRange.kInit32K, HeaderType.kHeaderLast32K, ATCartDetectFlags.NoDetect, 0x10000,
                              "5200 64K Super Cart (32K banks)")  # Mode_5200_64K_32KBanks
    Mode_5200_128K_32KBanks = (ATCartridgeMode.Mode_5200_128K_32KBanks, SystemType.kType5200, SizeType.kSize128K, WritableStoreType.kWrsNone, BankingType.kBankBF, InitRange.kInit32K, HeaderType.kHeaderLast32K, ATCartDetectFlags.NoDetect, 0x20000,
                               "5200 128K Super Cart (32K banks)")  # Mode_5200_128K_32KBanks
    Mode_5200_256K_32KBanks = (ATCartridgeMode.Mode_5200_256K_32KBanks, SystemType.kType5200, SizeType.kSize256K, WritableStoreType.kWrsNone, BankingType.kBankBF, InitRange.kInit32K, HeaderType.kHeaderLast32K, ATCartDetectFlags.NoDetect, 0x40000,
                               "5200 256K Super Cart (32K banks)")  # Mode_5200_256K_32KBanks
    Mode_5200_512K_32KBanks = (ATCartridgeMode.Mode_5200_512K_32KBanks, SystemType.kType5200, SizeType.kSize512K, WritableStoreType.kWrsNone, BankingType.kBankBF, InitRange.kInit32K, HeaderType.kHeaderLast32K, ATCartDetectFlags.NoDetect, 0x80000,
                               "5200 512K Super Cart (32K banks)")  # Mode_5200_512K_32KBanks
    Mode_Unknown = (
        ATCartridgeMode.Mode_Unknown, SystemType.kType800, SizeType.kSize2K, WritableStoreType.kWrsNone, BankingType.kBankNone, InitRange.kInit2K, HeaderType.kHeaderLast16B, ATCartDetectFlags.NoDetect, 0x0000, "Unknown cartridge")  # Mode_None

    def __new__(cls, mMode: ATCartridgeMode, *args, **kwargs):
        obj = int.__new__(cls, mMode.value)
        obj._value_ = int(mMode.value)
        return obj

    def __init__(self,
                 mMode: ATCartridgeMode,
                 mSystemType: SystemType,
                 mSizeTypes: int,
                 mWritableStoreType: WritableStoreType,
                 mBankingType: BankingType,
                 mInitRange: InitRange,
                 mHeaderType: HeaderType,
                 mFlags: ATCartDetectFlags,
                 mCartSize: int,
                 mCartDescription: str):
        self.mMode: ATCartridgeMode = mMode
        self.mSystemType: SystemType = mSystemType
        self.mSizeTypes: int = mSizeTypes
        self.mWritableStoreType: WritableStoreType = mWritableStoreType
        self.mBankingType: BankingType = mBankingType
        self.mInitRange: InitRange = mInitRange
        self.mHeaderType: HeaderType = mHeaderType
        self.mFlags: ATCartDetectFlags = mFlags
        self.mCartSize: int = mCartSize
        self.mCartDescription: str = mCartDescription
       # self._value_ = self.mMode.value

    @property
    def is_virtual(self):
        return self < 0 or self > 255 or self in (self.Mode_Unknown, self.Mode_None)

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>(ID={self.value}): {self.mCartDescription}'

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            try:
                return cls(int(value, 0))
            except ValueError:
                # It was not an integer
                return cls[value]
        return cls.Mode_Unknown

@dataclass
class A8CARFileHeader:
    magic: bytes = field(default=b'CART')
    _cart_mode: int = 0
    csum: int = 0
    blob_offset: int = 0

    def read(self, max_bytes:int = 0):
        return self._as_bytes[:max_bytes] if max_bytes else self._as_bytes

    def __len__(self):
        return struct.calcsize(self._CART_HDR_STRUCT)

    def __init__(self, magic = None, typ: ATCartridgeInfo = 0, csum: int = 0, blob_offset: int = 0):
        self._CART_HDR_STRUCT = '>4sLLL'
        if magic == b'CART' or magic is None:
            self.magic: bytes = magic or b'CART'
            self._cart_mode: ATCartridgeInfo = ATCartridgeInfo(typ)
            self.csum: int = csum
            self.blob_offset: int = blob_offset
        elif magic is not None:
            if hasattr(magic, 'read'):
                magic = magic.read(struct.calcsize(self._CART_HDR_STRUCT))
                if isinstance(magic, bytes):
                    self.__init__(magic=magic, typ=typ, csum=csum, blob_offset=blob_offset)
                else:
                    raise TypeError('Need binary stream')
            elif isinstance(magic, str):
                with open(magic, 'rb') as f_in:
                    self.__init__(f_in, typ=typ, csum=csum, blob_offset=blob_offset)
            elif isinstance(magic, bytes):
                if len(magic) >= struct.calcsize(self._CART_HDR_STRUCT):
                    magic, typ, csum, blob_offset = struct.unpack_from(self._CART_HDR_STRUCT, magic)
                    if magic == b'CART':
                        self.__init__(magic=magic, typ=typ, csum=csum, blob_offset=blob_offset)
                    else:
                        raise ValueError('Invalid input stream')
                else:
                    raise ValueError('Insufficient bytes for header')
            else:
                raise TypeError(f'Can\'t init header with {type(magic)}')
        else:
            raise TypeError(f'Can\'t init header with {type(magic)}')

    @property
    def cart_mode(self):
        return self._cart_mode

    @cart_mode.setter
    def cart_mode(self, new_mode):
        self._cart_mode = ATCartridgeInfo(new_mode)

    @property
    def _as_bytes(self):
        return struct.pack(self._CART_HDR_STRUCT, self.magic, self._cart_mode, self.csum, self.blob_offset)

    def __iter__(self):
        return self._as_bytes.__iter__()


class A8CARFile:
    @property
    def data_csum(self):
        return sum(self.rom_data) & 0xFFFFFFFF

    @property
    def is_valid(self):
        return self._header == self.header

    def __init__(self, fobj=None):
        self._header = A8CARFileHeader()
        self.rom_data = bytes()
        self.blob = bytes()
        if fobj is not None:
            if hasattr(fobj, 'read'):
                self._header = A8CARFileHeader(fobj)
                if self._header.blob_offset:
                    self.rom_data = fobj.read(self._header.blob_offset - len(self._header))
                    self.blob = fobj.read()
                else:
                    self.rom_data = fobj.read()
            else:
                with open(fobj, 'rb') as f_in:
                    self.__init__(f_in)

    def __len__(self):
        return sum(map(len, (self.header, self.rom_data, self.blob)))

    @property
    def _as_bytes(self):
        return it.chain(self.header, self.rom_data, self.blob)

    @property
    def header(self):
        new_hdr = A8CARFileHeader()
        new_hdr._cart_mode = ATCartridgeInfo(self._header._cart_mode)
        new_hdr.csum = self.data_csum
        new_hdr.blob_offset = len(new_hdr) + len(self.rom_data) if self.blob else 0
        self._header = new_hdr
        return self._header

    def __iter__(self):
        return self._as_bytes.__iter__()

    def read(self, max_bytes:int = 0):
        return self._as_bytes[:max_bytes] if max_bytes else self._as_bytes

try:
    # If running from MALCAT, execute the block
    from filetypes.base import *
    import malcat

    class HeaderBlock(Struct):
        def parse(self):
            yield String(4, name="Siganture")
            yield UInt32BE(name='Mode', values = [(carttype.name, carttype.value) for carttype in ATCartridgeInfo])
            yield UInt32BE(name='DataChecksum')
            yield UInt32BE(name='BlobOffset')


    class CartAnalyzer(FileTypeAnalyzer):
        category = malcat.FileType.ARCHIVE
        name = "CART"
        regexp = r"CART"

        def __init__(self):
            FileTypeAnalyzer.__init__(self)
            self.filesystem = {}

        def open(self, vfile, password=None):
            rd_where, rd_size = self.filesystem[vfile.path]
            return bytearray(self.read(rd_where, rd_size))

        def parse(self, hint):
            hdr = yield HeaderBlock(category=Type.HEADER)
            self.sections.append(malcat.Section(
                hdr.offset, len(hdr),
                hdr.offset, len(hdr),
                name = "HEADER", discard=True
            ))
            blob_offset = hdr['BlobOffset']
            blob_size = self.remaining() + len(hdr) - blob_offset if blob_offset else 0
            exec_offset = self.tell()
            exec_size = self.remaining() - blob_size

            self.filesystem['ROM'] = exec_offset, exec_size
            self.sections.append(malcat.Section(
                exec_offset, exec_size,
                exec_offset, exec_size,
                name = "ROM", exec = True
            ))
            self.files.append(malcat.VirtualFile('ROM', exec_size, "open"))
            yield Bytes(exec_size, name='ROM code', category=Type.DATA)
            yield Bytes(blob_size, name='Blob', category=Type.RESOURCE)
            if blob_size and blob_size:
                self.filesystem['BLOB'] = (blob_offset, blob_size)
                self.files.append(malcat.VirtualFile('BLOB', blob_size, "open"))
                self.sections.append(malcat.Section(
                    blob_offset, blob_size,
                    blob_offset, blob_size,
                    name = "BLOB",
                    discard=True
                ))
except ImportError:
    pass

