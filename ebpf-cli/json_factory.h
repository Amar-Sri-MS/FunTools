/*
 *  json_factory.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#pragma once
#include <map>
#include <string>
#ifdef __cplusplus
extern "C" {
#endif	
#include <utils/threaded/fun_json.h>
#ifdef __cplusplus
}
#endif	
/*
 * This is meant to provide a utility interface
 * to craft JSON tree for modules.
 * 
 * Every module should embed an instance of this
 * and use its public interfaces to craft a tree.
 *
 */



class json_factory {
  public:	
    json_factory(){}

    void* start(const std::string& verb, int64_t tid = 0);
    template<typename T>
	 void* create_arr(const std::vector<T>& vec);
    template<typename T>
	 void* create_dict(const std::map<const std::string&, T>& mp);
    void* create_bin(const uint8_t* b_arr,
	       const uint16_t& sz);	    

  private:
    struct fun_json* __tmpl(const std::string& verb, int64_t tid = 0);

};
template<typename T>
void* json_factory::create_arr(const std::vector<T>& vec) {
    struct fun_json* json_root = fun_json_create_empty_array();

    if (std::is_same<T, std::string>::value) {
        for(auto &val: vec) {
            fun_json_array_append(json_root, fun_json_create_string(val.c_str(),
				    fun_json_no_copy_no_own));
	}		
    } else if(std::is_same<T, int64_t>::value) {
        for(auto &val: vec) {
            fun_json_array_append(json_root, fun_json_create_int64(val));
	}		
    
    }
    return (void *)json_root;

}
template<typename T>
void* json_factory::create_dict(const std::map<const std::string&, T>& mp) {
    struct fun_json* json_root = fun_json_create_empty_dict();

    if (std::is_same<T, std::string>::value) {
        for(auto &val: mp) {
            fun_json_dict_add(json_root, 
			    val.first.c_str(), 
			    fun_json_no_copy_no_own,
			    fun_json_create_string(val.second.c_str()),
		            fun_json_no_copy_no_own);
	}		
    } else if(std::is_same<T, int64_t>::value) {
        for(auto &val: mp) {
            fun_json_dict_add(json_root, 
			    val.first.c_str(),
			    fun_json_no_copy_no_own,
			    fun_json_create_int64(val.second),
			    fun_json_no_copy_no_own);
	}		
    
    } else {
        for (auto& val: mp) {
            fun_json_dict_add(json_root, 
			    val.first.c_str(),
			    fun_json_no_copy_no_own,
			    val.second,
			    fun_json_no_copy_no_own);
	}
    }
    return (void *)json_root;

}      
