#include <cassert>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>


#include "bpf_module.h"
#include "cli_module.h"
#include "json_factory.h"

bpf_module::bpf_module(void) {}
bpf_module::~bpf_module(){}

bool bpf_module::__validate(std::unordered_map<std::string, std::string>& params) {
   std::string err_key{"cmd"};
   auto it = params.find(err_key);
   bool rval = (it != params.end());
   if (!rval) goto exit;

   if (it->second == "attach") {
       for (auto& key :{"bpf_file", 
		       "cl_id", 
		       "tx_id",
		       "sec",
		       "order",
		       "qid"}) {
          it = params.find(key);
	  rval &= (it != params.end());
          if (!rval) {
	    err_key = key;
	    goto exit;
	  }

       }


   } else if (it->second == "detach") {
       for (auto &key : { "cl_id", 
		    "tx_id",
		    "sec" }) {
          it = params.find(key);
	  rval &= (it != params.end());
          if (!rval) {
	    err_key = key;
	    goto exit;
	  }


       }
   }
   return rval;
exit:
   std::cerr << "Error: " << err_key << " not found " << std::endl;
   return rval;



}



void* bpf_module::create_request(std::unordered_map<std::string,
		std::string>& params) {
   /*
    * First create the dictionary for all int64_t
    */
   std::unordered_map<std::string, int64_t> int_vals;
   int64_t val;
   void* root = NULL;
   if (!__validate(params)) return root;

   if(params["cmd"] == "attach") {
       
       //str_vals.emplace("sec", params["sec"]);

       auto f_name = params["bpf_file"];
       std::ifstream fp(f_name, std::ios::in | std::ios::binary);
       fp.seekg(0, std::ios::end);
       auto len = fp.tellg();
       assert(len != 0);
       fp.seekg(0, std::ios::beg);
       auto buf = new char[len];
       fp.read(buf, len);
       fp.close();

       int_vals.emplace("bpf_len", len);
       val = strtoll(params["cl_id"].c_str(), NULL, 10);
       int_vals.emplace("cl_id", val);
       val = strtoll(params["tx_id"].c_str(), NULL, 10);
       int_vals.emplace("tx_id", val);
       val = strtoll(params["order"].c_str(), NULL, 10);
       int_vals.emplace("order", val);
       val = strtoll(params["qid"].c_str(), NULL, 10);
       int_vals.emplace("qid", val);
       
       root = __f.start("ebpf");
       auto sub_root = __f.create_dict(int_vals);

       assert(__f.add_bin_to_dict(sub_root, "bpf_code", (uint8_t *)(buf), len));
       assert(__f.add_key_to_dict(root, "arguments", sub_root));
       delete[] buf;
       __f.print(root);
   }
   return root;   
}

