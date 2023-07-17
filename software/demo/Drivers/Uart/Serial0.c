#include "Serial0.h"

#include <irq.h>
#include <generated/csr.h>


char Serial0_read(void)
{
	char c;
	while (serial0_rxempty_read());
	c = serial0_rxtx_read();
	serial0_ev_pending_write(SERIAL0_EV_RX);
	return c;
}

int Serial0_read_nonblock(void)
{
	return (serial0_rxempty_read() == 0);
}

void Serial0_write(char c)
{
	while (serial0_txfull_read());
	serial0_rxtx_write(c);
	serial0_ev_pending_write(SERIAL0_EV_TX);
}

void Serial0_init(void)
{
	serial0_ev_pending_write(serial0_ev_pending_read());
	serial0_ev_enable_write(SERIAL0_EV_TX | SERIAL0_EV_RX);
}

void Serial0_sync(void)
{
	while (serial0_txfull_read());
}


