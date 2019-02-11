
/*
 *  frontend.cpp
 *
 *  Created by Hariharan Thantry on 2019-02-01
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 */

#include <iostream>
#include <sstream>
#include <string>
#include <deque>

#ifdef __cplusplus
extern "C" {
#endif
/* C header files */

#include <getopt.h>

#ifdef __cplusplus
}
#endif

#include "cli_mgr.h"


#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include <readline/readline.h>
#include <readline/history.h>
#ifdef __cplusplus
}
#endif

#define DPC_PORT 40221

/*
 * Tokenize based on spaces only until
 * a { or a } is discovered
 */


std::deque<std::string> tokenize(const char* buf) {
    std::string s{buf};
    std::istringstream iss{s};
    std::deque<std::string> sub_str;
    bool start_dict = false;
    char tokenizer;
    do {
        std::string sub;
	auto c = iss.peek();
	if (c == '\n') break;
	if (c == '{') {
	    iss.get();	
            start_dict = true;
	    continue;
	}
	if (start_dict) {
	    tokenizer = ','; 
	} else {
	    tokenizer = ' ';
	}
	std::getline(iss, sub, tokenizer);
	sub.erase(std::remove_if(sub.begin(),
				sub.end(),
				[](unsigned char x) {
				    return (std::isspace(x) || (x == '}'));
				}), sub.end());

        if (sub.empty()) continue;
        sub_str.emplace_back(sub);
    } while(iss);

    return sub_str;
}

void help(void) {
    std::cout << std::endl;
    std::cout << std::endl;
    std::cout << "**** BPF frontend for transfering/installing ebpf bytes to FunOS ***" << std::endl;
    std::cout << "-h: This help" << std::endl;
    std::cout << "-S {hostname} | --dpc_host={hostname}: remote dpc host to connect to (default: localhost)" << std::endl;
    std::cout << "-p {portnum}  | --dpc_port={portnum}: dpc host port to connect to (default:" << DPC_PORT << ")" << std::endl;

    std::cout << std::endl;
    std::cout << std::endl;

    std::cout << "******Set of commands******" << std::endl;
    std::cout << "bpf (attach | detach)  KEY:VALUE" << std::endl;
    std::cout << "Allowed KEY:VALUE pairs" << std::endl;
    std::cout << "section:<xdp> (required for attach & detach)" << std::endl;
    std::cout << "cl_id:<client_id> (unique client id required for attach & detach)" << std::endl;
    std::cout << "tx_id:<tx_id> (attach & detach)" << std::endl;
    std::cout << "bpf:<location to bpf object byte code> (attach only)" << std::endl;
    std::cout << "qid: <QID> (attach only if section == xdp)" << std::endl;
    std::cout << "order: <order_num> (attachment ordering for this bpf code, lower number gets executed first)" << std::endl;

    std::cout << std::endl;
    std::cout << std::endl;
}


void process_cmd(cli_mgr& s, const char* buf) {
    auto vec = tokenize(buf);
    if (vec[0] == "help") {
        help();
    } else if(vec[0] == "bpf") {
	vec.pop_front();
	if (!s.process(ModuleID::BPF, vec)) {
            std::cout << "Incorrect command!" << std::endl;
	}
    } else {
        std::cout << "Not supported" << std::endl;
    }

}
/*
 * Entry point. dpcsh in tcp proxy mode must
 * already be running
 */

int main(int argc, char** argv)
{

    int opt_char;

    const char* hostname{"localhost"};
    uint16_t port_num{DPC_PORT};

    struct option long_opts[] = {
        { "help", no_argument, nullptr, 'h'},
        { "dpc_host", optional_argument, nullptr, 'S'},
        { "dpc_port", optional_argument, nullptr, 'p'},
        {nullptr, 0, nullptr, 0},
    };

    while ((opt_char = getopt_long(argc, argv, "hS:p:", long_opts, NULL)) != -1) {
        switch(opt_char) {
            case 'h':
                help();
                exit(0);
            case 'S':
                if (optarg) {
		    hostname = optarg;
		}
                break;
            case 'p':
		if (optarg) port_num = atoi(optarg);
		break;
	    default:
		assert(false);

	}
    }

    cli_mgr s(hostname, port_num);
    char* buf;
    rl_bind_key('\t', rl_insert);

    while((buf = readline("cmd>> ")) != nullptr) {
	if (buf[0] == '\0') continue;
        if (strlen(buf) > 0) add_history(buf);
        if(!strcmp(buf, "quit")) break;
        if(!strcmp(buf, "exit")) break;
        process_cmd(s, buf);
        free(buf);
    }
    return 0;
}
