

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

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
    std::cout << "***Set of commands******" << std::endl;
    std::cout << "set <csr_name.fld_name>" << std::endl;
    std::cout << "list [<ring_name.interior_node>] : Gets all the hierarchy under the node" << std::endl;
    std::cout << "num_inst <csr_name> : Gets the number of instances for csr_name" << std::endl;
    std::cout << "num_entries <csr_name> <instance_num> : Gets the number of entries" << std::endl;
    std::cout << "get <csr_name> <instance_num> : Gets the number of entries" << std::endl;
    std::cout << "flush <instance_num> <entry number>: Write current csr_entry value to hw" << std::endl;
    
    std::cout << "fetch <csr_name> <instance#> <entry#>: Read csr_entry from hw." << std::endl;
    std::cout << "fetch <ring_name.interior_node(s).csr_name.instance> <entry#>: Read csr_entry from hw" << std::endl;
    
    std::cout << "info <csr_name> : Gets all the field level info for csr_name" << std::endl;
    std::cout << "info <ring_name.interior_node(s)>: Get info on all csrs below this node" << std::endl;
}


void process_cmd(const char* buf) {
    auto vec = tokenize(buf);
    if (vec[0] == "help") {
        help();
    } else {
        std::cout << "Not implemented" << std::endl;
    }

}


int main()
{
    char* buf;
    rl_bind_key('\t', rl_insert);

    while((buf = readline("csrsh>> ")) != nullptr) {
        if (strlen(buf) > 0) add_history(buf);
        if(!strcmp(buf, "quit")) break;
        if(!strcmp(buf, "exit")) break;
        process_cmd(buf);
        free(buf);
    }
    return 0;
}
