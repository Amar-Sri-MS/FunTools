/*
 *  json_util.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#pragma once
#include <string>
#ifdef __cplusplus
extern "C" {
#endif	
#include <utils/threaded/fun_json.h>
#ifdef __cplusplus
}
#endif	
/*
 * Keeps all the JSON interfacing code here
 */

class json_util {
  public:	
    json_util(){}

    fun_json* peek(const uint64_t& addr, 
		    const uint16_t& n_bytes);

    fun_json* poke(const uint64_t& addr,
		    const uint8_t* b_arr,
		    const uint16_t& sz);
    uint8_t* peek_rsp(const std::string& json_str);
    bool poke_rsp(const std::string& json_str);
    std::string stringify(struct fun_json* json);
  private:
    fun_json* __tmpl(void);

};
