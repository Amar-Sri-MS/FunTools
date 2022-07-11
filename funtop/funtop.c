/* Tool to display statistics from a running funos */

#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <curses.h>
#include <inttypes.h>
#include <ctype.h>
#include <sys/socket.h>
#include <sys/un.h>

#define PLATFORM_POSIX	1

#include <FunOS/utils/threaded/fun_json.h>
#include <FunOS/services/commander/fun_commander.h>

#ifndef MIN
#define MIN(x,y) ((x) < (y) ? (x) : (y))
#endif

static int
_open_sock(const char *name)
{
	int sock;
	int r;

	struct sockaddr_un server;

	sock = socket(AF_UNIX, SOCK_STREAM, 0);
	assert(sock > 0);

	server.sun_family = AF_UNIX;
	strcpy(server.sun_path, name);

	r = connect(sock, (struct sockaddr *)&server, sizeof(server));
	if (r) {
		perror("connect");
		exit(1);
	}
		      

	return sock;
}

struct word_parameters {
    char *buf; // where the output goes
    size_t buf_max; // max width of the word
    bool right_justified;
};
static inline void print_in_buf(struct word_parameters *wparams, const char *str) {
    size_t len = strlen(str);
    size_t off = wparams->right_justified && (len < wparams->buf_max) ? wparams->buf_max - len : 0;
    memcpy(wparams->buf + off, str, MIN(wparams->buf_max, len));
}

// Fill buf with exactly buf_max characters (NOT zero terminated), defaulted to space
static void print_atomic_json(struct word_parameters *wparams, NULLABLE struct fun_json *item) {
	memset(wparams->buf, ' ', wparams->buf_max);
	if (!item) return;

	if (fun_json_is_error_message(item)) {
		return print_in_buf(wparams, "***");
	} else if (fun_json_is_null(item)) {
		return print_in_buf(wparams, "null");
	} else if (fun_json_is_bool(item)) {
		return print_in_buf(wparams, fun_json_to_bool(item, false) ? "true" : "false");
	} else if (fun_json_is_int(item)) {
		char temp[100];
		sprintf(temp, "%" PRId64 "", fun_json_to_int64(item, 0));
		return print_in_buf(wparams, temp);
	} else if (fun_json_is_double(item)) {
		char temp[100];
		sprintf(temp, "%.2f", fun_json_to_double(item, 0.0));
		if (!index(temp, 'e') && !index(temp, 'E') && !index(temp, '.') && (isdigit(temp[0]) || (temp[0] == '-'))) {
			// For round numbers, without exponent, and avoiding specials like 'NaN', we append .0 to make sure they are read back as double rather than int
			strcat(temp, ".0");
		}
		return print_in_buf(wparams, temp);
	} else if (fun_json_is_string(item)) {
		return print_in_buf(wparams, fun_json_to_string(item, ""));
	} else {
		return print_in_buf(wparams, "???");
	}
}

struct parameters {
    WINDOW *mainwin;
    size_t num_rows; // number of rows, including header
    size_t line_max; // maximum line size, must be greater than the sum of the width of each column + (cols-1) spaces
    size_t num_columns;
    const char **column_headers; // user name of the columns
    const char **column_keys; // names of the keys of the columns
    const size_t *widths; // width of each column
    const bool *right_just; // whether the column is right justified
};

// Fill buf with the proper columns, each column separated by a space
// buf must be line_max in size
static void print_row_json(struct parameters *params, NULLABLE struct fun_json *row_json, char *buf) {
    memset(buf, ' ', params->line_max);
    if (fun_json_is_dict(row_json)) {
        char *current = buf;
        for (size_t cc = 0; cc < params->num_columns; cc++) {
            if (cc) {
                // NOT first column, we add a space
                current++;
            }
            struct fun_json *item = fun_json_dict_at(row_json, params->column_keys[cc]);
            size_t width = params->widths[cc];
            bool just = params->right_just[cc];
            struct word_parameters wparams = { .buf = current, .buf_max = width, .right_justified = just };
            print_atomic_json(&wparams, item);
            current += width;
            if (current >= buf + params->line_max) break; // terminal too small
        }
    }
}

static void print_header_row(struct parameters *params, char *buf) {
    memset(buf, ' ', params->line_max);
    struct word_parameters wparams = { .buf = buf };
    for (size_t cc = 0; cc < params->num_columns; cc++) {
        if (cc) {
            // NOT first column, we add a space
            wparams.buf++;
        }
        const char *header = params->column_headers[cc];
        wparams.buf_max = params->widths[cc];
        wparams.right_justified = params->right_just[cc];
        print_in_buf(&wparams, header);
        wparams.buf += wparams.buf_max;
    }
}

static NULLABLE CALLER_TO_RELEASE struct fun_json *do_peek(int sock, const char *key_path) {
    static int64_t tid = 1;
    const char *template = "{ verb: peek, tid: %ld, arguments: [%s] }";
    char input_text[1024];
    sprintf(input_text, template, tid++, key_path);
    struct fun_json *input = fun_json_create_from_text(input_text);
    if (!input) {
        fun_json_printf("*** Can't parse command '%s'\n", input);
        return NULL;
    }
    bool ok = fun_json_write_to_fd(input, sock);
    fun_json_release(input);
    if (!ok) return NULL;
    struct fun_json *decorated = fun_json_read_from_fd(sock);
    if (!decorated) return NULL;
    return fun_json_lookup(decorated, "result");
}

struct compare_by_count_context {
    struct fun_json *this;
    struct fun_json *previous;
};

static int compare_by_count(void *per_call_context, const char *left, const char *right) {
    struct compare_by_count_context *con = per_call_context;
    struct fun_json *jleft = fun_json_dict_at(con->this, left);
    struct fun_json *jright = fun_json_dict_at(con->this, right);

    assert(fun_json_is_int(jleft));
    assert(fun_json_is_int(jright));
    int64_t l = fun_json_to_int64(jleft, 0);
    int64_t r = fun_json_to_int64(jright, 0);
    int64_t dyn_l = l;
    int64_t dyn_r = r;
    if (con->previous) {
        struct fun_json *pleft = fun_json_dict_at(con->previous, left);
        struct fun_json *pright = fun_json_dict_at(con->previous, right);
        if (pleft) dyn_l -= fun_json_to_int64(pleft, 0);
        if (pright) dyn_r -= fun_json_to_int64(pright, 0);
    }
    if (dyn_l != dyn_r) return -(dyn_l - dyn_r); // first sort the most actives
    if (l != r) return -(l - r); // then by the largest count
    return strcmp(left, right); // then by name to provide stability
}

static CALLER_TO_RELEASE struct fun_json *sort_wu_stats_by_count(struct fun_json *wu_stats, struct fun_json *previous, struct fun_json *durations) {
    assert(fun_json_is_dict(wu_stats));
    struct compare_by_count_context con = { .this = wu_stats, .previous = previous };
    size_t c = fun_json_dict_count(wu_stats);
    const char **keys = calloc(c, sizeof(const char *));
    fun_json_dict_fill_and_sort_keys_with_comparator(wu_stats, keys, &con, compare_by_count);
    struct fun_json **items = calloc(c, sizeof(void *));
    for (size_t i = 0; i < c; i++) {
        const char *key = (void *)keys[i];
        int64_t count = fun_json_to_int64(fun_json_dict_at(wu_stats, key), 0);
        struct fun_json *dict = fun_json_create_empty_dict();
        fun_json_dict_add(dict, "wu_name", fun_json_no_copy_no_own, fun_json_create_string(key, fun_json_copy), true);
        fun_json_dict_add(dict, "wu_count", fun_json_no_copy_no_own, fun_json_create_int64(count), true);
        int64_t duration = 0;
        if (fun_json_is_dict(durations)) {
            struct fun_json *d = fun_json_dict_at(durations, key);
            if (fun_json_is_int(d)) duration = fun_json_to_int64(d, 0) / 1000;
        }
        fun_json_dict_add(dict, "wu_duration", fun_json_no_copy_no_own, fun_json_create_int64(duration), true);
        double avg = count ? (double)duration / (double)count : 0.0;
        fun_json_dict_add(dict, "wu_dur_avg", fun_json_no_copy_no_own, fun_json_create_double(avg), true);
        items[i] = dict;
    }
    free(keys);
    struct fun_json *result = fun_json_create_array(items, c);
    free(items);
    return result;
}

static struct parameters set_up_params(void) {
    static const char *column_headers[] = { "WU NAME", "WU COUNT", "SUM uSECS", "AVG uSECS" };
    static const char *column_keys[] = { "wu_name", "wu_count", "wu_duration", "wu_dur_avg" };
    static const size_t widths[] = { 40, 15, 15, 15 };
    static const bool right_just[] = { false, true, true, true };
    WINDOW *mainwin = initscr();
    wclear(mainwin);
    struct parameters params = {
        .mainwin = mainwin,
        .num_rows = getmaxy(mainwin),
        .line_max = getmaxx(mainwin),
        .num_columns = 4,
        .column_headers = column_headers,
        .column_keys = column_keys,
        .widths = widths,
        .right_just = right_just,
    };
    return params;
}

static int get_num_VPs(int sock) {
    struct fun_json *all_vps = do_peek(sock, "config/all_vps");
    if (!all_vps) return 0;
    if (!fun_json_is_array(all_vps)) return 0;
    return fun_json_array_count(all_vps);
}

static int num_VPs = 0;

static void get_num_wus_received_sent(int sock, OUT uint64_t *received, OUT uint64_t *sent) {
    *received = 0;
    *sent = 0;
    struct fun_json *per_vp = do_peek(sock, "stats/per_vp");
    if (! per_vp) return;
    if (!fun_json_is_dict(per_vp)) return;
    size_t count = fun_json_dict_count(per_vp);
    const char **keys = calloc(count, sizeof(char *));
    fun_json_dict_fill_and_sort_keys(per_vp, keys);
    for (size_t i = 0; i < count; i++) {
	struct fun_json *sub = fun_json_dict_at(per_vp, keys[i]);
	if (!sub) continue;
	int64_t n = 0;
	if (fun_json_lookup_int64(sub, "wus_received", &n)) *received += n;
	if (fun_json_lookup_int64(sub, "wus_sent", &n)) *sent += n;
    }
    free(keys);
}

static void print_sorted_stats(struct parameters *params, struct fun_json *array) {
    char buf[1024];
    assert(params->line_max < 1024);
    print_header_row(params, buf); buf[params->line_max] = 0;
    mvwaddstr(params->mainwin, 2, 0, buf);
    for (int i = 3; i < params->num_rows; i++) {
        struct fun_json *sub = fun_json_array_at(array, i - 3);
        print_row_json(params, sub, buf);
        mvwaddstr(params->mainwin, i, 0, buf);
    }
}

static bool get_stats_and_display(struct parameters *params, int sock, struct fun_json **previous) {
    params->num_rows = getmaxy(params->mainwin);
    params->line_max = getmaxx(params->mainwin);
    struct fun_json *wu_stats = do_peek(sock, "stats/wus/counts");
    if (!wu_stats) {
        wclear(params->mainwin);
        refresh();
        return false;
    }
    uint64_t received = 0;
    uint64_t sent = 0;
    get_num_wus_received_sent(sock, &received, &sent);
    char header[1024];
    snprintf(header, 1024, "VPs: %d; WUs received: %" PRId64 "; WUs sent: %" PRId64, num_VPs, received, sent);
    mvwaddstr(params->mainwin, 0, 0, header);
    struct fun_json *wu_durations = do_peek(sock, "stats/wus/durations");
    struct fun_json *array = sort_wu_stats_by_count(wu_stats, *previous, wu_durations);
    print_sorted_stats(params, array);
    fun_json_release(array);
    if (*previous) fun_json_release(*previous);
    *previous = wu_stats;
    refresh();
    return true;
}

int main(int argc, char *argv[]) {
    printf("TOP\n");
    int sock = _open_sock("/tmp/funos-dpc.sock");
    struct parameters params = set_up_params();
    num_VPs = get_num_VPs(sock);
    struct fun_json *previous = NULL;
    while (get_stats_and_display(&params, sock, &previous)) {
        usleep(100*1000);
    }
}
