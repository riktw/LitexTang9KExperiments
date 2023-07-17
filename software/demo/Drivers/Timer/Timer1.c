#include "Timer1.h"

void Timer1_busy_wait(unsigned int ms)
{
	timer1_en_write(0);
	timer1_reload_write(0);
	timer1_load_write(CONFIG_CLOCK_FREQUENCY/1000*ms);
	timer1_en_write(1);
	timer1_update_value_write(1);
	while(timer1_value_read()) timer1_update_value_write(1);
}

void Timer1_busy_wait_us(unsigned int us)
{
	timer1_en_write(0);
	timer1_reload_write(0);
	timer1_load_write(CONFIG_CLOCK_FREQUENCY/1000000*us);
	timer1_en_write(1);
	timer1_update_value_write(1);
	while(timer1_value_read()) timer1_update_value_write(1);
}

void Timer1EnableInterrupt(void)
{
	Timer1ClearPendingInterrupt();
	timer1_ev_enable_write(0x1);
}

void Timer1DisableInterrupt(void)
{
	timer1_ev_enable_write(0x0);
	Timer1ClearPendingInterrupt();
}

void Timer1ClearPendingInterrupt(void)
{
	timer1_ev_pending_write(0x01);
}
void Timer1PeriodicInterrupt(unsigned int ms)
{
	timer1_en_write(0);
	timer1_load_write(0);
	timer1_reload_write(CONFIG_CLOCK_FREQUENCY/1000*ms);
	timer1_en_write(1);
	timer1_update_value_write(1);
	Timer1EnableInterrupt();
}
