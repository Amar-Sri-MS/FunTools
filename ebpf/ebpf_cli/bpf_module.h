#pragma once

#include <deque>
#include <string>

#include "cli_module.h"
#include "json_factory.h"

class bpf_module: public cli_module {

    public:
       bpf_module(void);
       virtual bool execute(std::deque<std::string>& params);
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
	* order: Order for attach
	*
	*
	*
	*/

       static const unsigned int _ATTACH_NKEYS{6};
       static const unsigned int _DETACH_NKEYS{3};
       static const char _KV_TOKEN{':'}; 

       bool __process(std::deque<std::string>& params);
       bool __verify(std::deque<std::string>& params);
       std::deque<std::string> __tokenize(const std::string& str);

       json_factory __f;



};



