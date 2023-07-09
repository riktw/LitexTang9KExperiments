#!/usr/bin/env python3

#
# Minimum tang nano 9k example. Should work with most board with minimal changes 
#

import os
from migen import *

from litex.gen import *

import sipeed_tang_nano_9K_platform  # It can be imported from litex_boards of course, but this way changes can be kept in the same repo

from litex.build.io import CRG
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

kB = 1024
mB = 1024*kB

# BaseSoC ------------------------------------------------------------------------------------------
class BaseSoC(SoCCore):
    def __init__(self, **kwargs):
        platform = sipeed_tang_nano_9K_platform.Platform()

        sys_clk_freq = int(1e9/platform.default_clk_period)

        # CRG --------------------------------------------------------------------------------------
        self.crg = CRG(platform.request(platform.default_clk_name))

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["integrated_rom_size"] = 64*kB  
        kwargs["integrated_sram_size"] = 8*kB
        SoCCore.__init__(self, platform, sys_clk_freq, ident="Tiny LiteX SoC on Tang Nano 9K", **kwargs)

# Build --------------------------------------------------------------------------------------------
def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_9K_platform.Platform, description="Tiny LiteX SoC on Tang Nano 9K.")
    parser.add_target_argument("--flash",                action="store_true",      help="Flash Bitstream.")
    args = parser.parse_args()

    soc = BaseSoC( **parser.soc_argdict)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer("openfpgaloader")
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer("openfpgaloader")
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs")) # FIXME
        prog.flash(0, builder.get_bios_filename(), external=True)

if __name__ == "__main__":
    main()
