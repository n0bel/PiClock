CFLAGS= -Wall -Werror -Wextra

all: gpio-keys

gpio-keys.o: gpio-keys.c uinput_names.inc

uinput_names.inc: 
	sh generate_uinput_names.sh >uinput_names.inc

clean:
	rm gpio-keys gpio-keys.o uinput_names.inc
