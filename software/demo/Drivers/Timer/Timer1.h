#ifndef __TIMER1_H
#define __TIMER1_H

#include <system.h>
#include <generated/csr.h>

void Timer1_busy_wait(unsigned int ms);
void Timer1_busy_wait_us(unsigned int us);

void Timer1EnableInterrupt(void);
void Timer1DisableInterrupt(void);
void Timer1ClearPendingInterrupt(void);
void Timer1PeriodicInterrupt(unsigned int ms);

#endif /* __TIMER2_H */