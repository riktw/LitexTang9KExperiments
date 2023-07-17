#ifndef __Serial0_H
#define __Serial0_H

#ifdef __cplusplus
extern "C" {
#endif

#define SERIAL0_EV_TX	0x1
#define SERIAL0_EV_RX	0x2

void Serial0_init(void);
void Serial0_isr(void);
void Serial0_sync(void);

void Serial0_write(char c);
char Serial0_read(void);
int Serial0_read_nonblock(void);

#ifdef __cplusplus
}
#endif

#endif
