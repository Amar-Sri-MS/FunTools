#define _POSIX_SOURCE
#define LINUX
/*
 * machdep.c
 *
 * This source herein may be modified and/or distributed by anybody who
 * so desires, with the following restrictions:
 *    1.)  No portion of this notice shall be removed.
 *    2.)  Credit shall not be taken for the creation of this source.
 *    3.)  This code is not to be traded, sold, or used for personal
 *         gain or profit.
 *
 */

/* Included in this file are all system dependent routines.  Extensive use
 * of #ifdef's will be used to compile the appropriate code on each system:
 *
 *    UNIX:        all UNIX systems.
 *    UNIX_BSD4_2: UNIX BSD 4.2 and later, UTEK, (4.1 BSD too?)
 *    UNIX_SYS5:   UNIX system 5
 *    UNIX_V7:     UNIX version 7
 *
 * All UNIX code should be included between the single "#ifdef UNIX" at the
 * top of this file, and the "#endif UNIX" at the bottom.
 * 
 * To change a routine to include a new UNIX system, simply #ifdef the
 * existing routine, as in the following example:
 *
 *   To make a routine compatible with UNIX system 5, change the first
 *   function to the second:
 *
 *      md_function()
 *      {
 *         code;
 *      }
 *
 *      md_function()
 *      {
 *      #ifdef UNIX_SYS5
 *         sys5code;
 *      #else
 *         code;
 *      #endif
 *      }
 *
 * Appropriate variations of this are of course acceptible.
 * The use of "#elseif" is discouraged because of non-portability.
 * If the correct #define doesn't exist, "UNIX_SYS5" in this case, make it up
 * and insert it in the list at the top of the file.  Alter the CFLAGS
 * in you Makefile appropriately.
 *
 */

#ifdef UNIX

#include <stdio.h>
#include <sys/file.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <signal.h>
#include "rogue.h"

#ifdef _POSIX_SOURCE
#include <unistd.h>
#include <termios.h>
#endif _POSIX_SOURCE

/* md_slurp:
 *
 * This routine throws away all keyboard input that has not
 * yet been read.  It is used to get rid of input that the user may have
 * typed-ahead.
 *
 * This function is not necessary, so it may be stubbed.  The might cause
 * message-line output to flash by because the game has continued to read
 * input without waiting for the user to read the message.  Not such a
 * big deal.
 */

md_slurp()
{
#ifdef UNIX_BSD4_2
	long ln;
	int i, n;
	ioctl(0, FIONREAD, &ln);
	n = (int) (stdin->_cnt + ln);

	for (i = 0; i < n; i++) {
		(void) getchar();
	}
#endif UNIX_BSD4_2
}

/* md_control_keyboard():
 *
 * This routine is much like md_cbreak_no_echo_nonl() above.  It sets up the
 * keyboard for appropriate input.  Specifically, it prevents the tty driver
 * from stealing characters.  For example, ^Y is needed as a command
 * character, but the tty driver intercepts it for another purpose.  Any
 * such behavior should be stopped.  This routine could be avoided if
 * we used RAW mode instead of CBREAK.  But RAW mode does not allow the
 * generation of keyboard signals, which the program uses.
 *
 * The parameter 'mode' when true, indicates that the keyboard should
 * be set up to play rogue.  When false, it should be restored if
 * necessary.
 *
 * This routine is not strictly necessary and may be stubbed.  This may
 * cause certain command characters to be unavailable.
 */

md_control_keybord(mode)
short mode;
{
	static boolean called_before = 0;
#ifdef _POSIX_SOURCE
        static struct termios tc_orig ;
        static struct termios tc_temp ;
#else
	static struct ltchars ltc_orig;
	static struct tchars tc_orig;
	struct ltchars ltc_temp;
	struct tchars tc_temp;
#endif
	signal(SIGTSTP,SIG_IGN);

	if (!called_before) {
		called_before = 1;
#ifdef _POSIX_SOURCE
        tcgetattr(0,&tc_orig);	
#else
		ioctl(0, TIOCGETC, &tc_orig);
		ioctl(0, TIOCGLTC, &ltc_orig);
#endif
	}
#ifndef _POSIX_SOURCE
	ltc_temp = ltc_orig;
#endif _POSIX_SOURCE
	tc_temp = tc_orig;

	if (!mode) {
#ifdef _POSIX_SOURCE
	/* tc_temp.c_cc[VSUSP] = -1; */
	tc_temp.c_cc[VERASE] = -1;
	tc_temp.c_cc[VSTART] = -1;
	tc_temp.c_cc[VSTOP] = -1;
#endif _POSIX_SOURCE
#ifdef UNIX_BSD4_2
		ltc_temp.t_suspc = ltc_temp.t_dsuspc = -1;
#endif UNIX_BSD4_2
#ifndef _POSIX_SOURCE
		ltc_temp.t_rprntc = ltc_temp.t_flushc = -1;
		ltc_temp.t_werasc = ltc_temp.t_lnextc = -1;
		tc_temp.t_startc = tc_temp.t_stopc = -1;
#endif _POSIX_SOURCE
	}
#ifdef _POSIX_SOURCE
       tcsetattr(0,TCSANOW,&tc_temp);
#else
	ioctl(0, TIOCSETC, &tc_temp);
	ioctl(0, TIOCSLTC, &ltc_temp);
#endif
}

/* md_heed_signals():
 *
 * This routine tells the program to call particular routines when
 * certain interrupts/events occur:
 *
 *      SIGINT: call onintr() to interrupt fight with monster or long rest.
 *      SIGQUIT: call byebye() to check for game termination.
 *      SIGHUP: call error_save() to save game when terminal hangs up.
 *
 *		On VMS, SIGINT and SIGQUIT correspond to ^C and ^Y.
 *
 * This routine is not strictly necessary and can be stubbed.  This will
 * mean that the game cannot be interrupted properly with keyboard
 * input, this is not usually critical.
 */

md_heed_signals()
{
	signal(SIGINT, onintr);
	signal(SIGQUIT, byebye);
	signal(SIGHUP, error_save);
}

/* md_ignore_signals():
 *
 * This routine tells the program to completely ignore the events mentioned
 * in md_heed_signals() above.  The event handlers will later be turned on
 * by a future call to md_heed_signals(), so md_heed_signals() and
 * md_ignore_signals() need to work together.
 *
 * This function should be implemented or the user risks interrupting
 * critical sections of code, which could cause score file, or saved-game
 * file, corruption.
 */

md_ignore_signals()
{
	signal(SIGQUIT, SIG_IGN);
	signal(SIGINT, SIG_IGN);
	signal(SIGHUP, SIG_IGN);
	signal(SIGTSTP,SIG_IGN);	/* No ^Z ! */
}

/* md_get_file_id():
 *
 * This function returns an integer that uniquely identifies the specified
 * file.  It need not check for the file's existence.  In UNIX, the inode
 * number is used.
 *
 * This function need not be implemented.  To stub the routine, just make
 * it return 0.  This will make the game less able to prevent users from
 * modifying saved-game files.  This is probably no big deal.
 */

int
md_get_file_id(fname)
char *fname;
{
	struct stat sbuf;

	if (stat(fname, &sbuf)) {
		return(-1);
	}
	return((int) sbuf.st_ino);
}

/* md_link_count():
 *
 * This routine returns the number of hard links to the specified file.
 *
 * This function is not strictly necessary.  On systems without hard links
 * this routine can be stubbed by just returning 1.
 */

int
md_link_count(fname)
char *fname;
{
	struct stat sbuf;

	stat(fname, &sbuf);
	return((int) sbuf.st_nlink);
}

/* md_gct(): (Get Current Time)
 *
 * This function returns the current year, month(1-12), day(1-31), hour(0-23),
 * minute(0-59), and second(0-59).  This is used for identifying the time
 * at which a game is saved.
 *
 * This function is not strictly necessary.  It can be stubbed by returing
 * zeros instead of the correct year, month, etc.  If your operating
 * system doesn't provide all of the time units requested here, then you
 * can provide only those that it does, and return zeros for the others.
 * If you cannot provide good time values, then users may be able to copy
 * saved-game files and play them.  
 */

md_gct(rt_buf)
struct rogue_time *rt_buf;
{
	struct timeval tv;
	struct timezone tzp;
	struct tm *t;
	long seconds;

	gettimeofday(&tv, &tzp);
	seconds = (long) tv.tv_sec;
	t = localtime(&seconds);

	rt_buf->year = t->tm_year;
	rt_buf->month = t->tm_mon + 1;
	rt_buf->day = t->tm_mday;
	rt_buf->hour = t->tm_hour;
	rt_buf->minute = t->tm_min;
	rt_buf->second = t->tm_sec;
}

/* md_gfmt: (Get File Modification Time)
 *
 * This routine returns a file's date of last modification in the same format
 * as md_gct() above.
 *
 * This function is not strictly necessary.  It is used to see if saved-game
 * files have been modified since they were saved.  If you have stubbed the
 * routine md_gct() above by returning constant values, then you may do
 * exactly the same here.
 * Or if md_gct() is implemented correctly, but your system does not provide
 * file modification dates, you may return some date far in the past so
 * that the program will never know that a saved-game file being modified.  
 * You may also do this if you wish to be able to restore games from
 * saved-games that have been modified.
 */

md_gfmt(fname, rt_buf)
char *fname;
struct rogue_time *rt_buf;
{
	struct stat sbuf;
	long seconds;
	struct tm *t;

	stat(fname, &sbuf);
	seconds = (long) sbuf.st_mtime;
	t = localtime(&seconds);

	rt_buf->year = t->tm_year;
	rt_buf->month = t->tm_mon + 1;
	rt_buf->day = t->tm_mday;
	rt_buf->hour = t->tm_hour;
	rt_buf->minute = t->tm_min;
	rt_buf->second = t->tm_sec;
}

/* md_df: (Delete File)
 *
 * This function deletes the specified file, and returns true (1) if the
 * operation was successful.  This is used to delete saved-game files
 * after restoring games from them.
 *
 * Again, this function is not strictly necessary, and can be stubbed
 * by simply returning 1.  In this case, saved-game files will not be
 * deleted and can be replayed.
 */

boolean
md_df(fname)
char *fname;
{
	if (unlink(fname)) {
		return(0);
	}
	return(1);
}

/* md_gln: (Get login name)
 *
 * This routine returns the login name of the user.  This string is
 * used mainly for identifying users in score files.
 *
 * A dummy string may be returned if you are unable to implement this
 * function, but then the score file would only have one name in it.
 */

char *
md_gln()
{
	char *getlogin();
	char *t;
	t = getlogin();
	return(t);
}

/* md_sleep:
 *
 * This routine causes the game to pause for the specified number of
 * seconds.
 *
 * This routine is not necessary at all, and can be stubbed with no ill
 * effects.
 */

md_sleep(nsecs)
int nsecs;
{
	(void) sleep(nsecs);
}

/* md_getenv()
 *
 * This routine gets certain values from the user's environment.  These
 * values are strings, and each string is identified by a name.  The names
 * of the values needed, and their use, is as follows:
 *
 *   TERMCAP
 *     The name of the users's termcap file, NOT the termcap entries
 *     themselves.  This is used ONLY if the program is compiled with
 *     CURSES defined (-DCURSES).  Even in this case, the program need
 *     not find a string for TERMCAP.  If it does not, it will use the
 *     default termcap file as returned by md_gdtcf();
 *   TERM
 *     The name of the users's terminal.  This is used ONLY if the program
 *     is compiled with CURSES defined (-DCURSES).  In this case, the string
 *     value for TERM must be found, or the routines in curses.c cannot
 *     function, and the program will quit.
 *   ROGUEOPTS
 *     A string containing the various game options.  This need not be
 *     defined.
 *   HOME
 *     The user's home directory.  This is only used when the user specifies
 *     '~' as the first character of a saved-game file.  This string need
 *     not be defined.
 *
 * If your system does not provide a means of searching for these values,
 * you will have to do it yourself.  None of the values above really need
 * to be defined except TERM when the program is compiled with CURSES
 * defined.  In this case, as a bare minimum, you can check the 'name'
 * parameter, and if it is "TERM" find the terminal name and return that,
 * else return zero.  If the program is not compiled with CURSES, you can
 * get by with simply always returning zero.  Returning zero indicates
 * that their is no defined value for the given string.
 */

char *
md_getenv(name)
char *name;
{
	char *value;
	char *getenv();

	value = getenv(name);

	return(value);
}

/* md_malloc()
 *
 * This routine allocates, and returns a pointer to, the specified number
 * of bytes.  This routines absolutely MUST be implemented for your
 * particular system or the program will not run at all.  Return zero
 * when no more memory can be allocated.
 */

char *
md_malloc(n)
int n;
{
	char *malloc();
	char *t;

	t = malloc(n);
	return(t);
}

/* md_gseed() (Get Seed)
 *
 * This function returns a seed for the random number generator (RNG).  This
 * seed causes the RNG to begin generating numbers at some point in it's
 * sequence.  Without a random seed, the RNG will generate the same set
 * of numbers, and every game will start out exactly the same way.  A good
 * number to use is the process id, given by getpid() on most UNIX systems.
 *
 * You need to find some single random integer, such as:
 *   process id.
 *   current time (minutes + seconds) returned from md_gct(), if implemented.
 *   
 * It will not help to return "get_rand()" or "rand()" or the return value of
 * any pseudo-RNG.  If you cannot a random number, you can just return 1,
 * but this means you games will ALWAYS start the same way, and will play
 * exactly the same way given the same input.
 */

md_gseed()
{
	return(getpid());
}

/* md_exit():
 *
 * This function causes the program to discontinue execution and exit.
 * This function must be implemented or the program will continue to
 * hang when it should quit.
 */

md_exit(status)
int status;
{
	exit(status);
}

/* If you have a viable curses/termlib library, then use it and don't bother
 * implementing the routines below.  And don't compile with -DCURSES.
 */

#ifdef CURSES

/* md_cbreak_no_echo_nonl:
 *
 * This routine sets up some terminal characteristics.  The tty-driver
 * must be told to:
 *   1.)  Not echo input.
 *   2.)  Transmit input characters immediately upon typing. (cbreak mode)
 *   3.)  Move the cursor down one line, without changing column, and
 *        without generating a carriage-return, when it
 *        sees a line-feed.  This is only necessary if line-feed is ever
 *        used in the termcap 'do' (cursor down) entry, in which case,
 *        your system should must have a way of accomplishing this.
 *
 * When the parameter 'on' is true, the terminal is set up as specified
 * above.  When this parameter is false, the terminal is restored to the
 * original state.
 *
 * Raw mode should not to be used.  Keyboard signals/events/interrupts should
 * be sent, although they are not strictly necessary.  See notes in
 * md_heed_signals().
 *
 * This function must be implemented for rogue to run properly if the
 * program is compiled with CURSES defined to use the enclosed curses
 * emulation package.  If you are not using this, then this routine is
 * totally unnecessary.
 * 
 * Notice that information is saved between calls.  This is used to
 * restore the terminal to an initial saved state.
 *
 */

md_cbreak_no_echo_nonl(on)
boolean on;
{
#ifdef _POSIX_SOURCE
	struct termios tty_buf ;
	static struct termios save_buf ;
#else
	struct sgttyb tty_buf;
	int tty_save_flags;
#endif _POSIX_SOURCE

	if (on) 
         {
#ifdef _POSIX_SOURCE
        tcgetattr(0,&tty_buf);	
        tcgetattr(0,&save_buf);	
	tty_buf.c_iflag |= ICRNL ;
	tty_buf.c_iflag &= ~( IGNCR | INLCR ) ;
	tty_buf.c_lflag &= ~(ICANON | ECHO) ;
	tty_buf.c_oflag &= ~(OPOST);
        tty_buf.c_cc[VMIN] = 1;
        tty_buf.c_cc[VTIME] = 0; 
	tcsetattr(0,TCSANOW,&tty_buf);
#else
	ioctl(0, TIOCGETP, &tty_buf);
	tty_save_flags = tty_buf.sg_flags;
	tty_buf.sg_flags |= CBREAK;
	tty_buf.sg_flags &= ~(ECHO | CRMOD); /* CRMOD: see note above */
        ioctl(0, TIOCSETP, &tty_buf);
#endif _POSIX_SOURCE
	}
     	else 
        {
#ifdef _POSIX_SOURCE
	tcsetattr(0,TCSANOW,&save_buf);
        exit (0);
#else
	tty_buf.sg_flags = tty_save_flags;
	ioctl(0, TIOCSETP, &tty_buf);
#endif 
      }
}

/* md_gdtcf(): (Get Default Termcap File)
 *
 * This function is called ONLY when the program is compiled with CURSES
 * defined.  If you use your system's curses/termlib library, this function
 * won't be called.  On most UNIX systems, "/etc/termcap" suffices.
 *
 * If their is no such termcap file, then return 0, but in that case, you
 * must have a TERMCAP file returned from md_getenv("TERMCAP").  The latter
 * will override the value returned from md_gdtcf().  If the program is
 * compiled with CURSES defined, and md_gdtcf() returns 0, and
 * md_getenv("TERMCAP") returns 0, the program will have no terminal
 * capability information and will quit.
 */

char *
md_gdtcf()
{
	return("/etc/termcap");
}

/* md_tstp():
 *
 * This function puts the game to sleep and returns to the shell.  This
 * only applies to UNIX 4.2 and 4.3.  For other systems, the routine should
 * be provided as a do-nothing routine.  md_tstp() will only be referenced
 * in the code when compiled with CURSES defined.
 *
 */

md_tstp()
{
#ifdef UNIX_BSD4_2
	kill(0, SIGTSTP);
#endif UNIX_BSD4_2
}

#endif CURSES

#endif UNIX
