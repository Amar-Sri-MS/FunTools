#include "dpcsh_log.h"

#include <time.h>
#include <stdio.h>
#include <sys/time.h>

void print_utc_time(void)
{
  struct timeval tv;
	struct tm *ptm;

  gettimeofday(&tv, NULL);

	ptm = gmtime(&tv.tv_sec);

  char buf[100];
  strftime(buf, sizeof(buf) - 1, "%FT%T", ptm);

	if (ptm == NULL) goto unknown;

#ifdef __APPLE__
	printf("%s.%06dZ", buf, tv.tv_usec);
#else
	printf("%s.%06ldZ", buf, tv.tv_usec);
#endif

  return;

unknown:
	printf("<unknown time>");
}
