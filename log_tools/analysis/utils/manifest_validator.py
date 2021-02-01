#!/usr/bin/env python3

#
# Manifest file validations.
#

import argparse

import manifest_parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Manifest file directory')

    args = parser.parse_args()

    is_valid = validate(args.dir)

    if is_valid:
        print(f'VALIDATION STATUS: SUCCESS')
    else:
        print(f'VALIDATION STATUS: FAILED')


def validate(path):
    """ Validates a manifest file """
    manifest = manifest_parser.parse(path)
    is_valid = True

    # Check if the manifest is empty
    if not manifest:
        print('ERROR: Manifest file is empty')
        return False        

    # Check if the manifest file contains contents
    contents = manifest.get('contents')
    if not contents:
        print('ERROR: Manifest file does not contain contents')
        is_valid = False

    # Check the contents of the manifest file
    for index, content in enumerate(contents, start=1):
        try:
            frn_info = manifest_parser.parse_FRN(content)
            if not content.startswith('frn'):
                print(f'WARNING: Manifest content string at line #{index} does not start with frn')

            # Check if required fields are present
            if not frn_info.get('resource_type'):
                print(f'ERROR: Manifest content at line #{index} does not contain value for resource_type')
                is_valid = False

            if not frn_info.get('prefix_path') and not frn_info.get('sub_path'):
                print(f'ERROR: Manifest content at line #{index} does not contain value for prefix_path and sub_path')
                is_valid = False

            for key, value in frn_info.items():
                if not value:
                    print(f'WARNING: Manifest content at line #{index} does not contain value for {key}')

        except:
            print(f'ERROR: Manifest content string at line #{index} is not in a correct format')
            is_valid = False

    return is_valid


if __name__ == "__main__":
    main()