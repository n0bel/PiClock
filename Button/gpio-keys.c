/*
The MIT License (MIT)

Copyright (c) 2015 Kevin Uhlir <n0bel@n0bel.net>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


Portions taken from input_map.sh from lircd distribution http://www.lirc.org/
Copyright (C) 2008 Christoph Bartelmus <lirc@bartelmus.de> (MIT License)

Portions taken from RPi-GPIO https://pypi.python.org/pypi/RPi.GPIO
Copyright (c) 2012-2015 Ben Croston  (MIT License)



*/


#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <ctype.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <poll.h>
#include <string.h>
#include <signal.h>
#include <linux/input.h>
#include <linux/uinput.h>
#include <getopt.h>

int debug = 0;

typedef struct {
	int pin;
	int key;
	int last;
	int fd;
} pin_t;

struct uinput_key {
        char *name;
        unsigned short code;

} uinput_keys[] = {
#include "uinput_names.inc"
        {
        NULL, 0}
};

#define MAX_KEYS 50
static pin_t keys[MAX_KEYS];
struct pollfd pollfds[MAX_KEYS];
int pollfd_count = 0;

int ufd = -1;
static char *config_file = NULL;
static char *device_name = NULL;


int keycode(char *name)
{
	if (isdigit(name[0]))
	{
		int code = strtol(name,NULL,0);
		if (code == 0) return(-1);
		return(code);
	}
	struct uinput_key *i;
	for (i = uinput_keys; i->name; i++)
	{
		if (strcmp(name,i->name) == 0)
		{
			return(i->code);
		}
	}
	return(-1);
}

static char keynametmp[50];
char * keyname(int code)
{
	struct uinput_key *i;
	for (i = uinput_keys; i->name; i++)
	{
		if (i->code == code)
		{
			return(i->name);
		}
	}
	sprintf(keynametmp,"unknown(0x%x)",code);
	return(keynametmp);
}

static int read_value (int fd)
{
	char v;

	if (lseek (fd, 0, SEEK_SET) < 0) {
		perror ("lseek");
		exit (0);
	}
	if (read (fd, &v, 1) != 1) {
		perror ("read");
		exit (0);
	}
	return v == '0' ? 0 : 1;
}


#define BCM2708_PERI_BASE_DEFAULT   0x20000000
#define GPIO_BASE_OFFSET            0x200000
#define FSEL_OFFSET                 0   // 0x0000
#define SET_OFFSET                  7   // 0x001c / 4
#define CLR_OFFSET                  10  // 0x0028 / 4
#define PINLEVEL_OFFSET             13  // 0x0034 / 4
#define EVENT_DETECT_OFFSET         16  // 0x0040 / 4
#define RISING_ED_OFFSET            19  // 0x004c / 4
#define FALLING_ED_OFFSET           22  // 0x0058 / 4
#define HIGH_DETECT_OFFSET          25  // 0x0064 / 4
#define LOW_DETECT_OFFSET           28  // 0x0070 / 4
#define PULLUPDN_OFFSET             37  // 0x0094 / 4
#define PULLUPDNCLK_OFFSET          38  // 0x0098 / 4

#define PAGE_SIZE  (4*1024)
#define BLOCK_SIZE (4*1024)


#define PUD_OFF  0
#define PUD_DOWN 1
#define PUD_UP   2


static volatile uint32_t *gpio_map;

void short_wait(void)
{
    int i;

    for (i=0; i<150; i++) {    // wait 150 cycles
        asm volatile("nop");
    }
}

void gpio_setup(void)
{
    int mem_fd;
    uint8_t *gpio_mem;
    uint32_t peri_base = BCM2708_PERI_BASE_DEFAULT;
    uint32_t gpio_base; 
    unsigned char buf[4];
    FILE *fp;

    // get peri base from device tree
    if ((fp = fopen("/proc/device-tree/soc/ranges", "rb")) != NULL) {
        fseek(fp, 4, SEEK_SET);
        if (fread(buf, 1, sizeof buf, fp) == sizeof buf) {
            peri_base = buf[0] << 24 | buf[1] << 16 | buf[2] << 8 | buf[3] << 0;
        }
        fclose(fp);
    }

    gpio_base = peri_base + GPIO_BASE_OFFSET;

    // mmap the GPIO memory registers
    if ((mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
		perror ("/dev/mem");
	        exit (1);
	}

    if ((gpio_mem = malloc(BLOCK_SIZE + (PAGE_SIZE-1))) == NULL) {
		perror ("gpio malloc");
	        exit (1);
	}

    if ((uint32_t)gpio_mem % PAGE_SIZE)
        gpio_mem += PAGE_SIZE - ((uint32_t)gpio_mem % PAGE_SIZE);

    gpio_map = (uint32_t *)mmap( (caddr_t)gpio_mem, BLOCK_SIZE, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_FIXED, mem_fd, gpio_base);

    if ((void *)gpio_map == MAP_FAILED) {
		perror ("gpio memmap");
	        exit (1);
	}

}

void set_pullupdn(int gpio, int pud)
{
    int clk_offset = PULLUPDNCLK_OFFSET + (gpio/32);
    int shift = (gpio%32);

    if (pud == PUD_DOWN)
        *(gpio_map+PULLUPDN_OFFSET) = (*(gpio_map+PULLUPDN_OFFSET) & ~3) | PUD_DOWN;
    else if (pud == PUD_UP)
        *(gpio_map+PULLUPDN_OFFSET) = (*(gpio_map+PULLUPDN_OFFSET) & ~3) | PUD_UP;
    else  // pud == PUD_OFF
        *(gpio_map+PULLUPDN_OFFSET) &= ~3;

    short_wait();
    *(gpio_map+clk_offset) = 1 << shift;
    short_wait();
    *(gpio_map+PULLUPDN_OFFSET) &= ~3;
    *(gpio_map+clk_offset) = 0;
}

void gpio_cleanup(void)
{
    munmap((caddr_t)gpio_map, BLOCK_SIZE);
}

void uinput_setup()
{
	pin_t *k;
	ufd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
	if (ufd < 0) {
		perror ("open error: /dev/uinput");
	        exit (1);
	}

	if (ioctl (ufd, UI_SET_EVBIT, EV_KEY) < 0
		|| ioctl (ufd, UI_SET_EVBIT, EV_REL) < 0) {
		perror ("ioctl UI_SET_EVBIT");
	        exit (1);
	}
	if (debug > 1) fprintf(stderr,"opened uinput\n");

	struct uinput_user_dev uinp;
	snprintf (uinp.name, sizeof (uinp.name), device_name ? device_name : "gpio button device");
	uinp.id.version = 4; /* lies, lies, lies */
	uinp.id.bustype = BUS_USB; 
	uinp.id.product = 1;
	uinp.id.vendor = 1;

	if (write (ufd, &uinp, sizeof (uinp)) != sizeof (uinp)) {
		perror ("write error initializing: /dev/uinput");
	        exit (1);
	}
	
	if (debug > 0) fprintf(stderr,"setup uinput device %s\n",uinp.name);

	for (k = keys; k->key; k++)
	{
		if (ioctl (ufd, UI_SET_KEYBIT, k->key) < 0) {
		        perror ("ioctl UI_SET_KEYBIT");
			exit (1);
		}

		if (debug > 0) fprintf(stderr,"uinput keycode set 0x%x %s for gpio pin %d\n",
			k->key,keyname(k->key),k->pin);

	}
	if (ioctl(ufd, UI_DEV_CREATE) < 0) {
		perror ("ioctl UI_DEV_CREATE");
	        exit (1);
	}

	if (debug > 0) fprintf(stderr,"uinput device created\n");
}


void pollfd_setup()
{
	pin_t *k;
	pollfd_count = 0;
	for (k = keys; k->key; k++)
	{
		pollfd_count++;
	}

	struct pollfd *p = pollfds;
	for (k = keys; k->key; k++, p++)
	{
		p->fd = k->fd;
		p->events = POLLPRI;
		p->revents = 0;
	}



}

void gpio_sys_setup()
{
	char path[300];
	char epath[300];
	char num[20];
	FILE *efp;
	FILE *fp;
	pin_t *k;
    	snprintf (epath, sizeof (epath), "/sys/class/gpio/export");
	efp = fopen (epath, "w");
	if (!efp) {
		fprintf(stderr,"open error:");
       	 	perror (epath);
	        exit (1);
    	}
	for (k = keys; k->key; k++)
	{

		// see if the pin is exported
		snprintf (path, sizeof (path), "/sys/class/gpio/gpio%d/value", k->pin);
		int fd = open (path, O_RDONLY);
		if (fd < 0) // not exported
		{

			// export the pin
		    	snprintf (num, sizeof (num), "%d", k->pin);
    			if (fputs (num, efp) < 0) {
				fprintf(stderr,"write error:");
		        	perror (epath);
       			 	exit (1);
		    	}
    			if (fflush (efp) < 0) {
				fprintf(stderr,"flush error:");
		        	perror (epath);
       			 	exit (1);
		    	}
			if (debug > 1) fprintf(stderr,"exported gpio %d\n",k->pin);
		}
		else
		{
			if (debug > 1) fprintf(stderr,"gpio %d already exported\n",k->pin);
			close(fd);
		}
	}

	usleep(100000);

	for (k = keys; k->key; k++)
	{

		set_pullupdn(k->pin, PUD_UP);

		if (debug > 1) fprintf(stderr,"gpio %d pullup set\n",k->pin);

		// set direction input
		snprintf (path, sizeof (path), "/sys/class/gpio/gpio%d/direction", k->pin);
		fp = fopen (path, "w");
		if (!fp) {
			fprintf(stderr,"open error:");
			perror (path);
			exit (1);
		}
		if (fputs ("in", fp) < 0) {
			fprintf(stderr,"write error:");
			perror (path);
			exit (1);
		}
		if (fclose (fp) != 0) {
			fprintf(stderr,"close error:");
			perror (path);
			exit (1);
		}


		// set edge interrupt
		snprintf (path, sizeof (path), "/sys/class/gpio/gpio%d/edge", k->pin);
		fp = fopen (path, "w");
		if (!fp) {
			fprintf(stderr,"open error:");
			perror (path);
			exit (1);
		}
		if (fputs ("both", fp) < 0) {
			fprintf(stderr,"write error:");
			perror (path);
			exit (1);
		}
		if (fclose (fp) != 0) {
			fprintf(stderr,"close error:");
			perror (path);
			exit (1);
		}

		if (debug > 1) fprintf(stderr,"gpio %d edge interupt set\n",k->pin);
		// open value file


		snprintf (path, sizeof (path), "/sys/class/gpio/gpio%d/value", k->pin);
		int fd = open (path, O_RDONLY);
		if (fd < 0) {
			fprintf(stderr,"open error:");
			perror (path);
			exit (1);
		}


		k->fd = fd;
		k->last = read_value (k->fd);

	}

	fclose (efp);
}

static void init(void)
{

	gpio_setup();

	gpio_sys_setup();

	uinput_setup();

	pollfd_setup();

}



static void sendkey(int code, int val)
{
	struct input_event ev;

	memset (&ev, 0, sizeof (ev));
	ev.type = EV_KEY;
	ev.code = code;
	ev.value = val;

	if (write (ufd, &ev, sizeof (ev)) != sizeof (ev)) {
		perror ("write key_event");
		exit (1);
	}

	ev.type = EV_SYN;
	ev.code = SYN_REPORT;
	ev.value = 0;

	if (write (ufd, &ev, sizeof (ev)) != sizeof (ev)) {
		perror ("write syn_event");
		exit (1);
	}

	if (debug > 0) fprintf(stderr,"key sent 0x%x %s %s\n",code,keyname(code),val?"pressed":"released");

}

static void one_event(void )
{

        if (poll (pollfds, pollfd_count, -1) < 0) {
            perror ("poll");
            exit (1);
        }


	struct pollfd *p;
	pin_t *k;
	int pc;
	for (k = keys, p = pollfds, pc = pollfd_count; pc > 0; p++, k++, pc--)
	{
		if (p->revents & POLLPRI)
		{
			usleep(20000); // 20ms debounce
			int v = read_value(k->fd);
			if (k->last != v)
			{
				if (debug > 0) fprintf(stderr,"gpio button change %d value %d\n",k->pin,v);
				sendkey(k->key,v ^ 1);
			}
			k->last = v;
		}
		p->revents = 0;
		p->events = POLLPRI;
	}

}


void sighandler(int s)
{
	(void)s;
	if (debug > 0) fprintf(stderr,"shutting down\n");
	if (ufd > -1) ioctl (ufd, UI_DEV_DESTROY );
	if (debug > 0) fprintf(stderr,"uinput device destroyed\n");
	char epath[300];
    	snprintf (epath, sizeof (epath), "/sys/class/gpio/unexport");
	FILE *efp = fopen (epath, "w");
	if (!efp) {
		fprintf(stderr,"open error:");
       	 	perror (epath);
	        exit (1);
    	}
	pin_t *k;
	for (k = keys; k->key; k++)
	{
		close(k->fd);
		char num[10];
		snprintf (num, sizeof (num), "%d", k->pin);
    		if (fputs (num, efp) < 0) {
			fprintf(stderr,"write error:");
	        	perror (epath);
       		 	exit (1);
	    	}
    		if (fflush (efp) < 0) {
			fprintf(stderr,"flush error:");
	        	perror (epath);
       		 	exit (1);
	    	}
		if (debug > 0) fprintf(stderr,"unexported %d\n",k->pin);
		set_pullupdn(k->pin, PUD_OFF);
		if (debug > 1) fprintf(stderr,"pullup turned off %d\n",k->pin);
	}
	fclose(efp);
	if (debug > 0) fprintf(stderr,"shutdown complete\n");
	exit(0);
}

void usage(void)
{
	fprintf(stderr,"\ngpio-keys: [options] gpio:keyname, ...\n"
	"	-h 	--help 		this message\n"
	"	-c	--config-file	specify a config file\n"
	"	-n	--device-name	specify the device name for creating the uinput device\n"
	"	gpio:keyname		for specifying the gpio pin which will be mapped to a keyname\n"
	"\n"
	"	Multiple gpio:keyname can be specified\n"
	"\n"
	"	A config file consists of lines with gpio and keyname pairs, one per line\n"
	"	lines starting with # are taken as comment lines\n"
	"\n"
	"	gpio-keys requires root privileges (because it uses uinput)\n"
	);

}

int main(int argc, char **argv)
{

	int c;
	pin_t *kp = keys;
	pin_t *kp2;
	char *colon;
	
	memset(keys,0,sizeof(keys));
	while (1) {
		int option_index = 0;
		static struct option long_options[] = {
			{"config-file",     required_argument, 0,  'c' },
			{"device-name",     required_argument, 0,  'n' },
			{"help",	no_argument, 0,  'h' },
			{"debug",	no_argument, 0,  'd' },
			{0,         0,                 0,  0 }
		};

		c = getopt_long(argc, argv, "c:n:k:dh",
		long_options, &option_index);
		if (c == -1)
		break;

		switch (c) {
		case 'c':
			config_file = strdup(optarg);
			break;
		case 'n':
			device_name = strdup(optarg);
			break;
		case 'h':
			usage();
			exit(0);
			break;
		case 'd':
			debug++;
			break;

		case '?':
		default:
			fprintf(stderr,"Unknown option: %c\n",c);
			usage();
			exit(1);
		}
	}

	if (optind < argc) {
		while (optind < argc) {
			optarg = argv[optind++];
			colon = strchr(optarg,':');
			if (!colon)
			{
				fprintf(stderr,"Unknown key syntax: %s\n",optarg);
				usage();
				exit(1);
			}
			colon++;
			int pin = atoi(optarg);
			int key = keycode(colon);
			if (key < 0) 
			{
				fprintf(stderr,"Unknown key code: %s\n",colon);
				usage();
				exit(1);
			}			
			for (kp2 = keys; kp2->key; kp2++)
			{
				if (kp2->pin == pin)
				{
					fprintf(stderr,"gpio pin %d already set as keycode 0x%x %s for command line argument: %s\n",
						pin, kp2->key, keyname(kp2->key), optarg);
					usage();
					exit(1);
				}
			}
			if (debug > 0) fprintf(stderr,"adding gpio pin %d as keycode 0x%x %s\n",
				pin,key, keyname(key));
			kp->pin = pin;
			kp->key = key;
			kp++;
			if ((kp - keys) >= MAX_KEYS)
			{
				fprintf(stderr, " too many keys specfied.  %d max.\n",MAX_KEYS);
				usage();
				exit(1);
			}
		}
	}

	if (config_file)
	{
		FILE *fp;
		if ((fp = fopen(config_file, "r")) != NULL) {
			int pin;
			char name[51];
			char line[255];
			while(fgets(line,250,fp) != NULL)
			{
				if (line[0] == '#') continue;
				if (sscanf(line,"%d%50s",&pin,name) == 2)
				{
					int key = keycode(name);
					if (key < 0) 
					{
						fprintf(stderr,"Unknown key code while reading %s: %s\n",config_file,name);
						usage();
						exit(1);
					}
					for (kp2 = keys; kp2->key; kp2++)
					{
						if (kp2->pin == pin)
						{
							fprintf(stderr,"gpio pin %d already set as keycode 0x%x %s for config line: %s\n",
								pin, kp2->key, keyname(kp2->key),line);
							usage();
							exit(1);
						}
					}
					if (debug > 0) fprintf(stderr,"adding gpio pin %d as keycode 0x%x %s\n",
						pin,key, keyname(key));
					kp->pin = pin;
					kp->key = key;
					kp++;
					if ((kp - keys) >= MAX_KEYS)
					{
						fprintf(stderr, " too many keys specfied.  %d max.\n",MAX_KEYS);
						usage();
						exit(1);
					}
				}
			}
			fclose(fp);
		}
		else
		{
			fprintf(stderr,"can't open config file: %s\n",config_file);
			usage();
			exit(1);
		}
	}

	if (keys[0].key == 0)
	{
		fprintf(stderr,"No gpio keys specified... nothing to do... quitting.\n");
		usage();
		exit(1);
	}
	init();
	signal(SIGINT, sighandler);
	signal(SIGTERM, sighandler);

	for(;;)
	{
		one_event();
	}

	return(0);
}

