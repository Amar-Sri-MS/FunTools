#!/usr/bin/env python3
import timeit
import binary_json

TEST_DATA_LOCATION = '.'

def time_decode_function(file_name):
    with open(TEST_DATA_LOCATION + '/' + file_name + '.bjson', 'rb') as f:
        binary_source = bytes(f.read())

    # Define a wrapper function to time the decode function
    def decode_wrapper():
        j = binary_json.decode(binary_source)
        binary_json.encode(j)

    # Time the decode function
    time_taken = timeit.timeit(decode_wrapper, number=1)
    print(f"Time taken to decode {file_name}: {time_taken} seconds")

# Example usage:
time_decode_function('big')