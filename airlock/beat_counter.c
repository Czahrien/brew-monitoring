#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <math.h>

int16_t buf[1024];
int buf_size = 0;
int cumulative_buf_size = 0;

void usage(const char *program, const char* message);
void usage(const char *program, const char* message) {
	fprintf(stderr,"USAGE: %s -s<samples per second> -t<threshold as percentage>\n%s", program, message);
}

int main(int argc, char **argv) { 
	setvbuf(stdout,NULL,_IOLBF,1024);
	printf("BEGIN!\n");
	//fflush(stdout);
	int opt;
	uint16_t THRESHOLD;
	int threshold_found = 0;
	uint16_t SAMPLES_PER_SECOND = 20;
	int samples_found = 0;
	float SECONDS_BETWEEN_PULSES = 0.5;

	while ((opt = getopt(argc, argv, "s:t:")) != -1) {
		switch (opt) {
			case 's':
				SAMPLES_PER_SECOND = atoi(optarg);
				samples_found = 1;
				break;
			case 't':
				THRESHOLD=SHRT_MAX / 100.0 * atoi(optarg);
				threshold_found = 1;
				break;
			default: /* '?' */
				usage(argv[0],"Unknown flag");
				exit(EXIT_FAILURE);
		}
	}

	if(!threshold_found || !samples_found) {
		usage(argv[0],"samples/sec and threshold are required arguments");
		exit(EXIT_FAILURE);
	}

	uint32_t last_sample_over_threshold;

	time_t now = time(NULL);
	printf("Starting @ %s\r\n", ctime(&now));

	int16_t max_amp = 0;

	while((buf_size = fread(buf,1,1024,stdin))) {
		//printf("%d.\r\n",buf_size);
		int samples = buf_size / 2;
		for(int i = 0; i < samples; ++i) {
			long cum = cumulative_buf_size + i;
			uint16_t sample = abs(buf[i]);
			if(sample > THRESHOLD) {
				if(sample > max_amp) {
					max_amp = sample;
				}
				if((cum - last_sample_over_threshold) / ((float)SAMPLES_PER_SECOND) > SECONDS_BETWEEN_PULSES) {
					now = time(NULL);
					printf("BUBBLE DETECTED\r\n"); // Line containing
								       //fflush(stdout);
					printf("%s   BOOP @ sample %ld!\r\n", ctime(&now), cum);
				}
				last_sample_over_threshold = cum;
			}
			else if(max_amp > 0 && (cum + i) - last_sample_over_threshold > SAMPLES_PER_SECOND * SECONDS_BETWEEN_PULSES)
			{ 
				printf("   max_amp = %hd\r\n", max_amp);
				max_amp = 0;	
			}

		}
		cumulative_buf_size += samples;
	}
}
