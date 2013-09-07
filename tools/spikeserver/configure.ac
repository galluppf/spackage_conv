AC_INIT([SpikeServer], [1.0], [sergio.davies@gmail.com])
AC_CONFIG_AUX_DIR([build])
AM_INIT_AUTOMAKE([foreign -Wall -Werror])
AC_PROG_CC
AC_PROG_CXX
AC_PROG_CPP

AC_CHECK_LIB([pthread], [pthread_create], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_mutex_lock], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_mutex_unlock], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_cond_wait], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_cond_signal], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_mutex_init], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_cond_init], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_detach], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_kill], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_join], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])
AC_CHECK_LIB([pthread], [pthread_exit], [PTHREADLIB=-lpthread], [AC_MSG_ERROR([Missing libpthread])])

AC_CHECK_LIB([rt], [timer_create], [RTLIB=-lrt], [AC_MSG_ERROR([Missing librt])])
AC_CHECK_LIB([rt], [timer_settime], [RTLIB=-lrt], [AC_MSG_ERROR([Missing librt])])
AC_CHECK_LIB([rt], [timer_delete], [RTLIB=-lrt], [AC_MSG_ERROR([Missing librt])])
AC_CHECK_LIB([rt], [clock_gettime], [RTLIB=-lrt], [AC_MSG_ERROR([Missing librt])])
AC_CHECK_LIB([rt], [clock_getres], [RTLIB=-lrt], [AC_MSG_ERROR([Missing librt])])

AC_CHECK_LIB([m], [floor], [MLIB=-lm], [AC_MSG_ERROR([Missing libm])])
AC_CHECK_LIB([m], [floorl], [MLIB=-lm], [AC_MSG_ERROR([Missing libm])])
AC_CHECK_LIB([m], [truncl], [MLIB=-lm], [AC_MSG_ERROR([Missing libm])])
AC_CHECK_LIB([m], [roundl], [MLIB=-lm], [AC_MSG_ERROR([Missing libm])])
AC_CHECK_LIB([m], [ceill], [MLIB=-lm], [AC_MSG_ERROR([Missing libm])])

AC_CHECK_HEADER([pthread.h], [AC_DEFINE([HAVE_PTHREAD_H], [1], [Defined to 1 if <pthread.h> is available])], [AC_MSG_ERROR([Missing <pthread.h>])])
AC_CHECK_HEADER([unistd.h], [AC_DEFINE([HAVE_UNISTD_H], [1], [Defined to 1 if <unistd.h> is available])], [AC_MSG_ERROR([Missing <unistd.h>])])
AC_CHECK_HEADER([stdbool.h], [AC_DEFINE([HAVE_STDBOOL_H], [1], [Defined to 1 if <stdbool.h> is available])], [AC_MSG_ERROR([Missing <stdbool.h>])])
AC_CHECK_HEADER([stdlib.h], [AC_DEFINE([HAVE_STDLIB_H], [1], [Defined to 1 if <stdlib.h> is available])], [AC_MSG_ERROR([Missing <stdlib.h>])])
AC_CHECK_HEADER([stdio.h], [AC_DEFINE([HAVE_STDIO_H], [1], [Defined to 1 if <stdio.h> is available])], [AC_MSG_ERROR([Missing <stdio.h>])])
AC_CHECK_HEADER([string.h], [AC_DEFINE([HAVE_STRING_H], [1], [Defined to 1 if <string.h> is available])], [AC_MSG_ERROR([Missing <string.h>])])
AC_CHECK_HEADER([sys/types.h], [AC_DEFINE([HAVE_SYS_TYPES_H], [1], [Defined to 1 if <sys/types.h> is available])], [AC_MSG_ERROR([Missing <sys/types.h>])])
AC_CHECK_HEADER([sys/socket.h], [AC_DEFINE([HAVE_SYS_SOCKET_H], [1], [Defined to 1 if <sys/socket.h> is available])], [AC_MSG_ERROR([Missing <sys/socket.h>])])
AC_CHECK_HEADER([netdb.h], [AC_DEFINE([HAVE_NETDB_H], [1], [Defined to 1 if <netdb.h> is available])], [AC_MSG_ERROR([Missing <netdb.h>])])
AC_CHECK_HEADER([signal.h], [AC_DEFINE([HAVE_SIGNAL_H], [1], [Defined to 1 if <signal.h> is available])], [AC_MSG_ERROR([Missing <signal.h>])])
AC_CHECK_HEADER([netinet/in.h], [AC_DEFINE([HAVE_NETINET_IN_H], [1], [Defined to 1 if <netinet/in.h> is available])], [AC_MSG_ERROR([Missing <netinet/in.h>])])
AC_CHECK_HEADER([arpa/inet.h], [AC_DEFINE([HAVE_ARPA_INET_H], [1], [Defined to 1 if <arpa/inet.h> is available])], [AC_MSG_ERROR([Missing <arpa/inet.h>])])
AC_CHECK_HEADER([time.h], [AC_DEFINE([HAVE_TIME_H], [1], [Defined to 1 if <time.h> is available])], [AC_MSG_ERROR([Missing <time.h>])])
AC_CHECK_HEADER([errno.h], [AC_DEFINE([HAVE_ERRNO_H], [1], [Defined to 1 if <errno.h> is available])], [AC_MSG_ERROR([Missing <errno.h>])])
AC_CHECK_HEADER([math.h], [AC_DEFINE([HAVE_MATH_H], [1], [Defined to 1 if <math.h> is available])], [AC_MSG_ERROR([Missing <math.h>])])

AC_SUBST([PTHREADLIB])
AC_SUBST([RTLIB])
AC_SUBST([MLIB])

AC_MSG_CHECKING([whether the timer has the appropriate resolution])

LIBS=-lrt

AC_LANG([C])

AC_RUN_IFELSE([AC_LANG_PROGRAM([[#include <stdio.h>
#include <unistd.h>
#include <time.h>]],
    [[struct timespec     clock_resolution;
int stat;

stat = clock_getres(CLOCK_REALTIME, &clock_resolution);

printf("Clock resolution is %ld seconds, %ld nanoseconds\n",
     clock_resolution.tv_sec, clock_resolution.tv_nsec);

return (!(clock_resolution.tv_sec == 0 && clock_resolution.tv_nsec == 1));
]])], [AC_MSG_RESULT([Timer has the appropriate resolution])], [AC_MSG_ERROR([Timer has not the appropriate resolution on this computer])], [AC_MSG_RESULT([Unable to test timer resolution])])

LIBS=

AC_CONFIG_HEADERS([src/config.h:src/config.h.in])
AC_CONFIG_FILES([Makefile src/Makefile])

AC_OUTPUT


#functions eventually to check for
#fopen
#fseek
#feof
#fclose
#fprintf
#printf
#fflush
#fwrite
#fread
#snprintf
#
#memset
#memcpy
#bzero
#
#getopt
#atoi
#strtok
#getaddrinfo
#socket
#bind
#close
#freeaddrinfo
#signal
#recvfrom
#perror
#gethostbyname
#inet_ntoa
#htons
#sendto
#
#realloc
#malloc
#calloc

