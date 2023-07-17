#include "Timer2.h"

void Timer2_busy_wait(unsigned int ms)
{
	timer2_en_write(0);
	timer2_reload_write(0);
	timer2_load_write(CONFIG_CLOCK_FREQUENCY/1000*ms);
	timer2_en_write(1);
	timer2_update_value_write(1);
	while(timer2_value_read()) timer2_update_value_write(1);
}

void Timer2_busy_wait_us(unsigned int us)
{
	timer2_en_write(0);
	timer2_reload_write(0);
	timer2_load_write(CONFIG_CLOCK_FREQUENCY/1000000*us);
	timer2_en_write(1);
	timer2_update_value_write(1);
	while(timer2_value_read()) timer2_update_value_write(1);
}

void Timer2EnableInterrupt(void)
{
	Timer2ClearPendingInterrupt();
	timer2_ev_enable_write(0x1);
}

void Timer2DisableInterrupt(void)
{
	timer2_ev_enable_write(0x0);
	Timer2ClearPendingInterrupt();
}

void Timer2ClearPendingInterrupt(void)
{
	timer2_ev_pending_write(0x01);
}
void Timer2PeriodicInterrupt(unsigned int ms)
{
	timer2_en_write(0);
	timer2_load_write(0);
	timer2_reload_write(CONFIG_CLOCK_FREQUENCY/1000*ms);
	timer2_en_write(1);
	timer2_update_value_write(1);
	Timer2EnableInterrupt();
}