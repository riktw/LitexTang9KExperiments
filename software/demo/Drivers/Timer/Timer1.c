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