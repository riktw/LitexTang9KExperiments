#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# SPDX-License-Identifier: BSD-2-Clause

import os
from migen import *

from litex.gen import *

from platform import sipeed_tang_nano_9k
from pwm_core import *

from litex.soc.cores.clock.gowin_gw1n import GW1NPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.timer import *
from litex.soc.cores.gpio import *
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores import uart

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------
class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
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
    # Actual SoC builder
    def __init__(self, sys_clk_freq=27e6, bios_flash_offset=0x0,
        **kwargs):
        platform = sipeed_tang_nano_9k.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["integrated_rom_size"] = 128*kB
        kwargs["integrated_ram_size"] = 8*kB
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano 9K", **kwargs)

        # HyperRAM ---------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            # TODO: Use second 32Mbit PSRAM chip.
            dq      = platform.request("IO_psram_dq")
            rwds    = platform.request("IO_psram_rwds")
            reset_n = platform.request("O_psram_reset_n")
            cs_n    = platform.request("O_psram_cs_n")
            ck      = platform.request("O_psram_ck")
            ck_n    = platform.request("O_psram_ck_n")
            class HyperRAMPads:
                def __init__(self, n):
                    self.clk   = Signal()
                    self.rst_n = reset_n[n]
                    self.dq    = dq[8*n:8*(n+1)]
                    self.cs_n  = cs_n[n]
                    self.rwds  = rwds[n]
            # FIXME: Issue with upstream HyperRAM core, so use old one. Need to investigate.
            if not os.path.exists("hyperbus.py"):
                os.system("wget https://github.com/litex-hub/litex-boards/files/8831568/hyperbus.py.txt")
                os.system("mv hyperbus.py.txt hyperbus.py")
            from hyperbus import HyperRAM
            hyperram_pads = HyperRAMPads(0)
            self.comb += ck[0].eq(hyperram_pads.clk)
            self.comb += ck_n[0].eq(~hyperram_pads.clk)
            self.hyperram = HyperRAM(hyperram_pads)
            self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=self.mem_map["main_ram"], size=4*mB))
            
        self.add_constant("CONFIG_MAIN_RAM_INIT") # This disables the memory test on the hyperram and saves some boottime
        
        self.timer1 = Timer()
        self.timer2 = Timer()
        
        self.leds = GPIOOut(pads = platform.request_all("user_led"))
        
        self.pwm0 = PwmModule(platform.request("pwm0"))
        
        # Serial stuff 
        self.i2c0 = I2CMaster(pads = platform.request("i2c0"))
        
        self.add_uart("serial0", "uart0")
        
        self.gpio = GPIOIn(platform.request("user_btn", 1), with_irq=True)
        self.irq.add("gpio", use_loc_if_exists=True)
        
        self.irq.add("timer1",  use_loc_if_exists=True)
        self.irq.add("timer2",  use_loc_if_exists=True)


# Build --------------------------------------------------------------------------------------------
def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_9k.Platform, description="LiteX SoC on Tang Nano 9K.")
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
