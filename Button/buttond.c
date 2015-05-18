#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <string.h>
#include <signal.h>
#include <linux/input.h>
#include <linux/uinput.h>

typedef struct {
	int pin;
	int key;
	int last;
	int fd;
} pin_t;



static pin_t keys[] = {
	{ 23,   KEY_SPACE },
	{ 0, 0 }
};



struct pollfd *pollfds;
int pollfd_count = 0;

int ufd = -1;

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



static void init (void)
{
	int i;
	char path[300];
	char epath[300];
	char num[20];
	FILE *efp;
	FILE *fp;
	pin_t *k;

	pollfd_count = 0;

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

	struct uinput_user_dev uinp;
	snprintf (uinp.name, sizeof (uinp.name), "gpio button device");
	uinp.id.version = 4; /* lies, lies, lies */
	uinp.id.bustype = BUS_USB; 
	uinp.id.product = 1;
	uinp.id.vendor = 1;

	if (write (ufd, &uinp, sizeof (uinp)) != sizeof (uinp)) {
		perror ("write error initializing: /dev/uinput");
	        exit (1);
	}
	
    	snprintf (epath, sizeof (path), "/sys/class/gpio/export");
	efp = fopen (epath, "w");
	if (!efp) {
		fprintf(stderr,"open error:");
       	 	perror (path);
	        exit (1);
    	}
	for (k = keys; k->key; k++)
	{
		pollfd_count++;

		// see if the pin is exported
		snprintf (path, sizeof (path), "/sys/class/gpio/gpio%d/value", k->pin);
		int fd = open (path, O_RDONLY);
		if (fd < 0) // not
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
		}
		else
		{
			close(fd);
		}
	}
	usleep(100000);
	for (k = keys; k->key; k++)
	{

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

		if (ioctl (ufd, UI_SET_KEYBIT, k->key) < 0) {
		        perror ("ioctl UI_SET_KEYBIT");
			exit (1);
		}

	}
	fclose (efp);
	pollfds = (struct pollfd*)malloc(sizeof(struct pollfd)*pollfd_count);
	if (!pollfds) {
		perror ("malloc pollfds");
		exit (1);
	}
	struct pollfd *p = pollfds;
	for (k = keys; k->key; k++, p++)
	{
		p->fd = k->fd;
		p->events = POLLPRI;
		p->revents = 0;
	}


	if (ioctl(ufd, UI_DEV_CREATE) < 0) {
		perror ("ioctl UI_DEV_CREATE");
	        exit (1);
	}


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
	for (k = keys, p = pollfds, pc = pollfd_count; pc > 0; p++, pc--)
	{
		if (p->revents & POLLPRI)
		{
			usleep(20000); // 20ms debounce
			int v = read_value(k->fd);
			if (k->last != v)
			{
				sendkey(k->key,v ^ 1);
				printf("pin%d=%d key=%d\n",k->pin,v,k->key);
			}
			k->last = v;
		}
		p->revents = 0;
		p->events = POLLPRI;
	}

}


void sighandler(int s)
{
	if (ufd > -1) ioctl (ufd, UI_DEV_DESTROY );
}

int main(int argc, char **argv)
{
	init();
	signal(SIGINT, sighandler);
	for(;;)
	{
		one_event();
	}

	return(0);
}

