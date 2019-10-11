/*
*  bpf_module.h
*
*  Created by Hariharan Thantry on 2019-04-01
*
*  Class for  of the dpc communicating module for bpf
*  Subclasses cli_module
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*
*/


#pragma once

#include <string>
#include <unordered_map>
#include <utility>
#include "cli_module.h"
#include "json_factory.h"

class bpf_module: public cli_module {

    public:
       bpf_module(void);

       virtual std::pair<uint8_t*, size_t> create_bin_request(
		       std::unordered_map<std::string,std::string>& params);
       virtual void* create_js_req(std::unordered_map<std::string,
		                   std::string>& params);

       virtual ~bpf_module(void);
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

       bool __validate(std::unordered_map<std::string, std::string>& params);
       void* __create_request(std::unordered_map<std::string, std::string>& params);


};



