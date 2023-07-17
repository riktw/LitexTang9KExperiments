#include "GpioIn.h"

void GpioInInitInterrupt(uint8_t mode, uint8_t edge)
{
	gpio_mode_write(mode);
    gpio_edge_write(edge);
	GpioInClearPendingInterrupt();
}

void GpioInEnableInterrupt(void)
{
    GpioInClearPendingInterrupt();
    gpio_ev_enable_write(0x1);
}

void GpioInDisableInterrupt(void)
{
    gpio_ev_enable_write(0x0);
    GpioInClearPendingInterrupt();
}

void GpioInClearPendingInterrupt(void)
{
    gpio_ev_pending_write(0x01);
}