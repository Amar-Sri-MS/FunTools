#pragma once

#include <string>
#include <unordered_map>

#include "cli_module.h"
#include "json_factory.h"

class bpf_module: public cli_module {

    public:
       bpf_module(void);
       virtual void* create_request(
		       std::unordered_map<std::string,std::string>& params);
       ~bpf_module(void);
    private:
       /*
	* Attach keys are
	*
	* sec: xdp
	* cl_id: client_id, int64_t
	* tx_id: tx_id, int64_t
	* bpf: location of bpf code
	* qid: QID to attach to
	* order: Order for invocation.
	*/

       static const unsigned int _ATTACH_NKEYS{6};
       static const unsigned int _DETACH_NKEYS{3};
       static const char _KV_TOKEN{':'}; 
       json_factory __f;
       bool __validate(std::unordered_map<std::string, std::string>& params);



};



