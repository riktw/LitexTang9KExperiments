// This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
// License: BSD

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/i2c.h>
#include <generated/csr.h>
#include "Drivers/Uart/uarthelpers.h"
#include "Drivers/Timer/Timer1.h"
#include "Drivers/Timer/Timer2.h"
#include "Drivers/Uart/Serial0.h"
#include "Drivers/Gpio/GpioIn.h"

volatile bool buttonIRQSet = false;

void handle_isr(int irqs);
void IrqBlink(void);

void handle_isr(int irqs)
{	
	if(irqs & (1 << GPIO_INTERRUPT))
	{
		GpioInClearPendingInterrupt();
		buttonIRQSet = true;
	}
	else if(irqs & (1 << TIMER1_INTERRUPT))
	{
		Timer1ClearPendingInterrupt();
	}
	else if(irqs & (1 << TIMER2_INTERRUPT))
	{
		Timer2ClearPendingInterrupt();
		IrqBlink();
	}
	else
	{
		printf("Unexpected IRQ: %x\n", irqs);
	}
}

/*-----------------------------------------------------------------------*/
/* Help                                                                  */
/*-----------------------------------------------------------------------*/
static void help(void)
{
	puts("\nLiteX minimal demo app built "__DATE__" "__TIME__"\n");
	puts("Available commands:");
	puts("help               - Show this command");
	puts("reboot             - Reboot CPU");
	puts("blink              - Blink LEDs");
	puts("I2C_scan           - Scan the I2C bus");
	puts("serial0_test       - Send a message on serial0");
	puts("gpio_in            - Read gpio input");
	puts("start_irq_blink    - Use Timer2 in irq mode to blink some LEDs");
	puts("stop_irq_blink     - Stop Timer2 based blink");
}

/*-----------------------------------------------------------------------*/
/* Commands                                                              */
/*-----------------------------------------------------------------------*/
static void reboot_cmd(void)
{
	ctrl_reset_write(1);
}


/*-----------------------------------------------------------------------*/
/* Console service / Main                                                */
/*-----------------------------------------------------------------------*/
static void console_service(void)
{
	char *str;
	char *token;

	str = readstr();
	if(str == NULL) return;
	token = get_token(&str);
	if(strcmp(token, "help") == 0)
		help();
	else if(strcmp(token, "reboot") == 0)
		reboot_cmd();
	else if(strcmp(token, "blink") == 0)
	{
		for(int i = 0; i < 3; ++i)
		{
			leds_out_write(0x00);
			Timer1_busy_wait(500);
			leds_out_write(0xFF);
			Timer1_busy_wait(500);
		}
	}
	else if(strcmp(token, "I2C_scan") == 0)
	{
		for(int i = 0; i < 0x7F; ++i)
		{
			if(i2c_poll(i))
			{
				printf("I2C device found on address %x\n", i);
			}
		}
	}
	else if(strcmp(token, "serial0_test") == 0)
	{
		char hello[] = "Hello world!\n";
		for(int i = 0; i < sizeof(hello); ++i)
		{
			Serial0_write(hello[i]);
			printf("%c", hello[i]);
		}
		printf("Send hello world over serial0!\n");
	}
	else if(strcmp(token, "gpio_in") == 0)
	{
		printf("Waiting for interrupt. Press the user button to continue!\n");
		GpioInEnableInterrupt();
		while(!buttonIRQSet);
		buttonIRQSet = false;
		GpioInDisableInterrupt();
		printf("Button pressed!\n");
	}
	else if(strcmp(token, "start_irq_blink") == 0)
	{
		Timer2PeriodicInterrupt(500);
	}
	else if(strcmp(token, "stop_irq_blink") == 0)
	{
		Timer2DisableInterrupt();
	}
}

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
	irq_setmask(
		(1 << GPIO_INTERRUPT) 	|
		(1 << TIMER1_INTERRUPT) | 
		(1 << TIMER2_INTERRUPT));
	irq_setie(1);
#endif

	uart_init();
	//Serial0_init();
	//i2c_send_init_cmds();
	//GpioInInitInterrupt(MODE_EDGE, EDGE_FALLING);

	help();

	while(1) {
		console_service();
	}

	return 0;
}

void IrqBlink(void)
{
	leds_out_write(~leds_out_read());
}