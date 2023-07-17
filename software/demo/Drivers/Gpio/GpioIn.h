#ifndef __GPIOIN_H
#define __GPIOIN_H

#include <system.h>
#include <generated/csr.h>

#define MODE_EDGE 0x00
#define MODE_CHANGE 0x01
#define EDGE_RISING 0x00
#define EDGE_FALLING 0x01

void GpioInInitInterrupt(uint8_t mode, uint8_t edge);
void GpioInEnableInterrupt(void);
void GpioInDisableInterrupt(void);
void GpioInClearPendingInterrupt(void);

#endif /* __GPIOIN_H */