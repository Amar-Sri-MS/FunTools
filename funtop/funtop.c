/* Tool to display statistics from a running funos */

#include <funos/fun_utils.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <funos/fun_json.h>
#include <unistd.h>
#include <funos/fun_commander.h>
#include <curses.h>
#include <inttypes.h>
#include <ctype.h>

#define MIN(x,y) (x < y ? x : y)

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
    switch (item->type) {
        case fun_json_error_type:
            return print_in_buf(wparams, "***");
        case fun_json_null_type:
            return print_in_buf(wparams, "null");
        case fun_json_bool_type:
            return print_in_buf(wparams, item->bool_value ? "true" : "false");
        case fun_json_int_type: {
            char temp[100];
            sprintf(temp, "%" PRId64 "", item->int_value);
            return print_in_buf(wparams, temp);
        }
        case fun_json_double_type: {
            char temp[100];
            sprintf(temp, "%.2f", item->double_value);
            if (!index(temp, 'e') && !index(temp, 'E') && !index(temp, '.') && (isdigit(temp[0]) || (temp[0] == '-'))) {
                // For round numbers, without exponent, and avoiding specials like 'NaN', we append .0 to make sure they are read back as double rather than int
                strcat(temp, ".0");
            }
            return print_in_buf(wparams, temp);
        }
        case fun_json_string_type:
            return print_in_buf(wparams, item->utf8_value);
        case fun_json_bjson_type:
            return print_atomic_json(wparams, fun_json_expand_if_needed(item));
        default:
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
    if (row_json && (row_json->type == fun_json_dict_type)) {
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

static void print_sorted_stats(struct parameters *params, struct fun_json *array) {
    char buf[1024];
    assert(params->line_max < 1024);
    print_header_row(params, buf); buf[params->line_max] = 0;
    mvwaddstr(params->mainwin, 0, 0, buf);
    for (int i = 1; i < params->num_rows; i++) {
        struct fun_json *sub = fun_json_array_at(array, i - 1);
        print_row_json(params, sub, buf);
        mvwaddstr(params->mainwin, i, 0, buf);
    }
}

static NULLABLE CALLER_TO_RELEASE struct fun_json *get_wu_stats(int sock, bool durations) {
    static int64_t tid = 1;
    const char *template = "{ verb: peek, tid: %ld, arguments: [wdi/%s] }";
    char input_text[1024];
    sprintf(input_text, template, tid++, durations ? "durations" : "counts");
    struct fun_json *input = fun_json_create_from_text(input_text);
    if (!input) {
        printf("*** Can't parse command '%s'\n", fun_json_to_text(input));
        return NULL;
    }
    bool ok = fun_json_write_to_fd(input, sock);
    fun_json_release(input);
    if (!ok) return NULL;
    /* receive a reply */
    return fun_json_read_from_fd(sock);
}

struct compare_by_count_context {
    struct fun_json *this;
    struct fun_json *previous;
};
static int compare_by_count(void *map_context, void *per_call_context, fun_map_key_t left, fun_map_key_t right) {
    struct compare_by_count_context *con = per_call_context;
    struct fun_json *jleft = fun_json_dict_at(con->this, (char *)left);
    struct fun_json *jright = fun_json_dict_at(con->this, (char *)right);
    assert(jleft->type == fun_json_int_type);
    assert(jright->type == fun_json_int_type);
    int64_t l = jleft->int_value;
    int64_t r = jright->int_value;
    int64_t dyn_l = l;
    int64_t dyn_r = r;
    if (con->previous) {
        struct fun_json *pleft = fun_json_dict_at(con->previous, (char *)left);
        struct fun_json *pright = fun_json_dict_at(con->previous, (char *)right);
        if (pleft) dyn_l -= pleft->int_value;
        if (pright) dyn_r -= pright->int_value;
    }
    if (dyn_l != dyn_r) return -(dyn_l - dyn_r); // first sort the most actives
    if (l != r) return -(l - r); // then by the largest count
    return strcmp((char *)left, (char *)right); // then by name to provide stability
}

static CALLER_TO_RELEASE struct fun_json *sort_wu_stats_by_count(struct fun_json *wu_stats, struct fun_json *previous, struct fun_json *durations) {
    assert(wu_stats->type == fun_json_dict_type);
    struct compare_by_count_context con = { .this = wu_stats, .previous = previous };
    fun_map_key_t *keys = fun_map_sorted_keys(wu_stats->dict, &con, compare_by_count);
    size_t c = fun_map_count(wu_stats->dict);
    const struct fun_json **items = calloc(c, sizeof(void *));
    for (size_t i = 0; i < c; i++) {
        const char *key = (void *)keys[i];
        int64_t count = fun_json_dict_at(wu_stats, key)->int_value;
        struct fun_json *dict = fun_json_create_empty_dict();
        fun_json_dict_add(dict, "wu_name", fun_json_no_copy_no_own, fun_json_create_string(key, fun_json_copy), true);
        fun_json_dict_add(dict, "wu_count", fun_json_no_copy_no_own, fun_json_create_int64(count), true);
        int64_t duration = 0;
        if (durations && (durations->type == fun_json_dict_type)) {
            struct fun_json *d = fun_json_dict_at(durations, key);
            if (d && (d->type == fun_json_int_type)) duration = d->int_value;
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
    static const char *column_headers[] = { "WU NAME", "WU COUNT", "SUM DURATION", "AVG DURATION" };
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

static bool get_stats_and_display(struct parameters *params, int sock, struct fun_json **previous) {
    params->num_rows = getmaxy(params->mainwin);
    params->line_max = getmaxx(params->mainwin);
    struct fun_json *wu_stats = get_wu_stats(sock, false);
    if (!wu_stats) {
        wclear(params->mainwin);
        refresh();
        return false;
    }
    struct fun_json *wu_durations = get_wu_stats(sock, true);
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
    struct fun_json *previous = NULL;
    while (get_stats_and_display(&params, sock, &previous)) {
        usleep(100*1000);
    }
}
