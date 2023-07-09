#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# SPDX-License-Identifier: BSD-2-Clause

import os
from migen import *

from litex.gen import *

import sipeed_tang_nano_9K_platform

from litex.soc.cores.clock.gowin_gw1n import GW1NPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

kB = 1024
mB = 1024*kB

# CRG stands for Clock Reset Generator
# Here at least a clock and reset are added, and any PLLs. 
# In this case a PLL with the same in and output frequency and a user button is used as reset for the PLL. 
class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # Clk / Rst
        clk27 = platform.request("clk27")
        rst_n = platform.request("user_btn", 0)

        # PLL
        self.pll = pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------
class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=27e6, bios_flash_offset=0x0,
        **kwargs):
        platform = sipeed_tang_nano_9K_platform.Platform()

        # Notice the custom CRG here, _CRG instead of CRG
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["integrated_rom_size"] = 64*kB
        kwargs["integrated_sram_size"] = 8*kB
        SoCCore.__init__(self, platform, sys_clk_freq, ident="Still tiny LiteX SoC on Tang Nano 9K", **kwargs)


# Build --------------------------------------------------------------------------------------------
# Some extra arguments got added, sys-clk-freq to change the CPU frequency, we got a PLL after all. and a bios flash offset
# Try --sys-clk-freq=54e6 to run it at twice the clock speed!
def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_9K_platform.Platform, description="Still tiny LiteX SoC on Tang Nano 9K.")
    parser.add_target_argument("--flash",                action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq",         default=27e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--bios-flash-offset",    default="0x0",            help="BIOS offset in SPI Flash.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        bios_flash_offset   = int(args.bios_flash_offset, 0),
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer("openfpgaloader")
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer("openfpgaloader")
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME
        prog.flash(int(args.bios_flash_offset, 0), builder.get_bios_filename(), external=True)

if __name__ == "__main__":
    main()
