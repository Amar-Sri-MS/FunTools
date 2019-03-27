    return json_root;

}

void* json_factory::start(const std::string& verb, int64_t tid) {
   return (void *)(__tmpl(verb, tid));
}


void* json_factory::create_dict(const std::unordered_map<std::string, std::string>& mp) {
    struct fun_json* json_root = fun_json_create_empty_dict();

    for(auto &val: mp) {
        fun_json_dict_add_string(json_root, 
		    val.first.c_str(), 
		    fun_json_no_copy_no_own,
		    val.second.c_str(),
	            fun_json_no_copy_no_own,
		    true);
    }
	
    return (void *)json_root;
}

void* json_factory::create_dict(const std::unordered_map<std::string, int64_t>& mp) {
    struct fun_json* json_root = fun_json_create_empty_dict();

    for(auto &val: mp) {
        fun_json_dict_add_int64(json_root, 
		    val.first.c_str(), 
		    fun_json_no_copy_no_own,
		    val.second,
	            true);
    }
	
    return (void *)json_root;
}

bool json_factory::add_bin_to_dict(void* root, const std::string& key,
		uint8_t* val, const uint16_t sz) {
    struct fun_json* bin_json = fun_json_create_from_parsing_binary(val, sz);
    return fun_json_dict_add((struct fun_json *)root, 
		    key.c_str(),
		    fun_json_copy,
		    bin_json,
		    true);

}
bool json_factory::add_key_to_dict(void* root, const std::string& key,
		void* val) {

    return fun_json_dict_add((struct fun_json *)root,
		    key.c_str(),
		    fun_json_no_copy_no_own,
		    (struct fun_json *)val,
		    true);


}
void json_factory::print(void* root) {
    size_t allc_sz;
    auto str = fun_json_pretty_print(
		    (const struct fun_json *)(root),
		    1,
		    "   ",
		    100,
		    (FUN_JSON_PRETTY_PRINT_CONVERT_ERRORS_TO_STRING | FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS),
		    &allc_sz);
    std::cout << str << std::endl;
    free(str);




}
