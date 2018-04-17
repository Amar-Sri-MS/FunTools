
/*
 *  frontend.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#ifdef __cplusplus 
extern "C" {
#endif	
/* C header files */

#include <getopt.h>

#ifdef __cplusplus
}
#endif

#include "csrsh.h"


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
std::vector<std::string> tokenize(const char* buf) {
    std::string s{buf};
    std::istringstream iss{s};
    std::vector<std::string> sub_str;
    do {
        std::string sub;
        iss >> sub;
        sub_str.emplace_back(sub);

    } while(iss);
    return sub_str;
}

void help(void) {
    std::cout << std::endl;	
    std::cout << std::endl;	
    std::cout << "****Invocation arguments********" << std::endl;
    std::cout << "-h: This help" << std::endl;
    std::cout << "-S {hostname} | --dpc_host={hostname}: remote dpc host to connect to (default: localhost)" << std::endl;
    std::cout << "-p {portnum}  | --dpc_port={portnum}: dpc host port to connect to (default:" << DPC_PORT << ")" << std::endl;

    std::cout << std::endl;	
    std::cout << std::endl;	

    std::cout << "***Set of commands******" << std::endl;
    std::cout << "set <csr_name> : Set a particular CSR. Will present with list of fields" << std::endl;
    std::cout << "set_raw <csr_name> : Set a particular CSR with a hex value" << std::endl;
    std::cout << "show: Shows all current CSRs in buffer with hex values" << std::endl;

    std::cout << "flush <csr_name> <instance_num> <entry number>: Write csr# csr_num to hw {instance_num, entry_num}" << std::endl;

    std::cout << "fetch <csr_name> <instance#> <entry#>: Read csr_entry from hw." << std::endl;
    std::cout << "rfetch <ring_name.interior_node(s).csr_nam> <instance#> <entry#>: Read csr_entry from hw" << std::endl;

    std::cout << "info <csr_name> : Gets all the field level info for csr_name" << std::endl;
    std::cout << "rinfo <ring_name.interior_node(s)>: Get info on all csrs below this node" << std::endl;
    std::cout << std::endl;	
    std::cout << std::endl;	
}


void process_cmd(CsrSh& s, const char* buf) {
    auto vec = tokenize(buf);
    if (vec[0] == "help") {
        help();
    } else if(vec[0] == "info") {
	s.dump_csr(vec[1]);
    } else if(vec[0] == "set") {
	s.set_csr(vec[1]);
    } else if(vec[0] == "set_raw") {
	s.set_raw(vec[1]);
    } else if(vec[0] == "show") {
	s.show_buffer();
    } else if(vec[0] == "flush") {
	assert(vec.size() >= 4);
	s.flush(vec[1], std::stoi(vec[2]), std::stoul(vec[3]));
    } else if(vec[0] == "fetch") {
	assert(vec.size() >= 4);
	s.fetch(vec[1], std::stoi(vec[2]), std::stoul(vec[3]));
    } else if(vec[0] == "rfetch") {
        std::cout << "Not implemented" << std::endl;
    } else if(vec[0] == "rinfo") {
        std::cout << "Not implemented" << std::endl;
    } else {
        std::cout << "Not supported" << std::endl;
    }

}

static struct option long_opts[] = {
    { "help", no_argument, NULL, 'h'},
    { "dpc_host", optional_argument, NULL, 'S'},
    { "dpc_port", optional_argument, NULL, 'p'},
    {NULL, 0, NULL, 0},


};

int main(int argc, char** argv)
{

    int opt_char;

    std::string hostname;
    uint16_t port_num{DPC_PORT};

    while ((opt_char = getopt_long(argc, argv, "hS::p::", long_opts, NULL)) != -1) {
        switch(opt_char) {
            case 'h': 
                help();
                exit(0);		
            case 'S':
                if (optarg) {
		    hostname = optarg;
		} else {
                    hostname = "localhost";
		}
                break;
            case 'p':
		if (optarg) port_num = atoi(optarg);
		break;
	    default:
		assert(false);
 		
	}
    }
    
    CsrSh s(hostname, port_num);
    char* buf;
    rl_bind_key('\t', rl_insert);
    
    while((buf = readline("csrsh>> ")) != nullptr) {
        if (strlen(buf) > 0) add_history(buf);
        if(!strcmp(buf, "quit")) break;
        if(!strcmp(buf, "exit")) break;
        process_cmd(s, buf);
        free(buf);
    }
    return 0;
}
