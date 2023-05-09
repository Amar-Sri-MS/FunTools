#!/usr/bin/env python3
"""Running code summarization


    Preconditions
    -------------
    function bodies are extracted from the source code and stored in a file

    Examples
    --------
    >>> python3 ./code_summarization_runner.py --test # test run
    >>> python3 ./code_summarization_runner.py --input_file func_bodies.txt --output_file func_summaries.txt


    Checks
    ------
    static check:
    >>> mypy ./code_summarization_runner.py
    >>> pylint ./code_summarization_runner.py

    format:
    >>> black ./code_summarization_runner.py
"""

# it seems that extracting script seems to grab documented fuction, such as bam.c:56 bam_alloc()
# bam_alloc() is inside of undocumented_api block in the json file...TO CHECK

# missing json file output by 129 (zero base)
# this file is used after the line 130, extracted_undoc_split.txt
# this file is generated upto line 129, extracted_undoc_summary_2023-05-01-18-01.txt

# issues in the splitting filename and code
# this file is post 129 line, extracted_undoc_split_summary_2023-05-01-18-24.txt
# extracted_undoc_split_summary_2023-05-01-18-24.json

import argparse
import os
import sys
import re
import datetime

import pandas as pd
import numpy as np
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity
from redlines import Redlines
from IPython.display import display, Markdown, Latex, HTML, JSON
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple

import openai

# setup openai
import os
import openai
from dotenv import load_dotenv


# examples used in code summary
examples = [
    """
/**
 * fun_heap_add - Add 1 item to a heap
 *	NULL is not a valid item
 *	Note that if the same item is given, it will also get added to the heap
 *	O(LOG(N)) but very fast

 * @fun_heap: fun_heap
 * @item: item to add
 * 
 * Return: false if needed to allocate and could not
 */
bool fun_heap_add(struct fun_heap *, uintptr_t)
{
	assert(item != heap->outsider);
	if (heap->count + 1 > heap->capacity) {
		size_t new_capa = 2 * heap->capacity + 1;
		if (!fun_heap_set_capacity(heap, new_capa)) {
			return false;
		}
	}
	bubble_up(heap, item);
	heap->count++;
	return true;
}
"""
]


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--test", type=bool, help="Test run with sample code", default=False
    )

    parser.add_argument(
        "--debug", type=bool, help="Debug run", default=False
    )

    parser.add_argument(
        "--input_file", type=str, help="Input file containing function bodies"
    )

    parser.add_argument(
        "--output_file", type=str, default="output_file", help="Output summarization file"
    )

    parser.add_argument(
        "--model", type=str, help="model_name, ex> text-davinci-003, gpt-3.5-turbo (chatgpt)", default="text-davinci-003"
    )

    args = parser.parse_args()

    return args

def get_completion(prompt, model='text-davinci-003', temperature=0): 
    messages = [{"role": "user", "content": prompt}]
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=1000,
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0,
        # stop=stop_sequence,
        model=model,
    )
    # return response.choices[0].message["content"]
    return response["choices"][0]["text"]

def get_completion_chatgpt(prompt, model="gpt-3.5-turbo", temperature=0):
    """Get text completion with OpenAI's API, with chatgpt engine."""
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        engine="chatgpt",
        # model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


def code_summary_chatgpt(code: str, examples: List[str], model: str, debug: bool = False) -> str:
    """Generate code summary based on examples using chatgpt
    Parameters
    ----------
    code : str
        Code snippet
    examples : list
        List of examples

    Returns
    -------
    str
        Generated code summary
    """

    def prepare_prompt(code, examples, debug=debug):
        # prompt = f"proofread and correct the following text: ```{text}```"

        prompt = """
        You are a skilled developer. You have been asked to review a function deliminated by thriple backticks. Please review the function and provide maximum two lines of clear, helpful, and short documentation comment for the function follow the format of the example:\n
        """

        examples_str = "\n".join(examples)

        prompt += f"\n{examples_str}\n"

        prompt += f"""```{code}```"""
        if debug:
            print("-" * 50)
            print("Prompt:")
            print(prompt)
            print("-" * 50)
            print("\n")
        return prompt

    prompt = prepare_prompt(code, examples)
    if debug:
        print("Prompt:")
        print(prompt)
        print("-" * 50)

    if model == "gpt-3.5-turbo": # chatgpt
        response = get_completion_chatgpt(prompt, model=model)
    elif model == "text-davinci-003":
        response = get_completion(prompt, model=model)
    else:
        assert False, "model not supported"

    return response


def setup_api(model):
    load_dotenv()
    openai.api_type = os.getenv("OPENAI_API_TYPE")
    openai.api_base = os.getenv("OPENAI_API_BASE")
    if model == "gpt-3.5-turbo": # "chatgpt"
        openai.api_version = os.getenv("OPENAI_API_CHAT_VERSION")  # chatgpt
    elif model == "text-davinci-003":
        openai.api_version = os.getenv("OPENAI_API_VERSION") # davinci
    else:
        assert False, "model not supported"

    openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_code_summary(filename: str, output_file: str, examples: List[str], model, debug:bool=False):
    """Generate code summary for a file containing function bodies
    Parameters
    ----------
    filename : str
        Input file containing function bodies
    output_file : str
        Output file containing code summaries without extension
    """

    # read filename
    txt_file = output_file + ".txt"
    json_file = output_file + ".json"

    with open(filename, "r") as f:
        lines = f.readlines()

    def extract_filename_line_no(line: str) -> str:
        return re.search(r"^.+:\d+:", line).group()

    def extract_function_body(line: str) -> str:
        return re.sub(r"^[^:]+:\d{1,}:", "", line)
        # return re.sub(r"^[^:]+:.*:", "", line)

    def extract_function_name(code):
        # matches = re.findall(r"\b\w+\b(?=\s*\()", code)
        matches = re.findall(r"\s*(\w+)\s*\(", code)
        return matches[0] if matches else "NOT_FOUND"

    def remove_double_slash(string):
        return string.replace("\\n", "\n")

    # write to file on-the-fly, which is helping to slow down the process
    # so that we don't hit the rate limit
    # not efficient, but this helps to deal with API
    with open(txt_file, "w") as f:
        # generate code summaries
        outputs = []
        # code_summaries = []
        for i, line in enumerate(lines):
            output = {}

            filename_line_no = extract_filename_line_no(line)
            code = extract_function_body(line)
            func_name = extract_function_name(code)

            if func_name == "NOT_FOUND":
                print("func_name not found")
                assert False
            if debug:
                print("-" * 50)
                print("filename_line_no:", filename_line_no)
                print("func_name:", func_name)
                print("code:", code)
                code_summary = "code_summary"
            
            else:
                code_summary = code_summary_chatgpt(code, examples, model, debug=debug)

            # code_summaries.append(code_summary)
            output["filename"] = filename_line_no
            output["func_name"] = func_name
            output["code"] = code
            output["code_summary"] = code_summary
            outputs.append(output)
            code = remove_double_slash(code)

            print("-" * 50)
            print(i)
            print(filename_line_no)
            print(func_name)
            print(code_summary)
            print(code)

            f.write(f"# {filename_line_no}\n")
            f.write(f"# {func_name}\n")
            f.write(f"\n{code_summary}\n")
            f.write(f"\n{code}\n\n")

    # save outputs in json file
    if outputs:
        df = pd.DataFrame(outputs)
        df.to_json(json_file, orient="records")


# def test_code_summary_chatgpt():
#     """Test code"""
#     code =
#     """ec_operate_push(\n	struct channel *channel,\n	struct ec_operate *params)\n{\n	struct flow *f = erasure_to_flow();\n\n	channel_push(channel, ec_operate, flow_dest(f), f, params);\n	erasure_get_matrix_or_push(channel, f, params);\n}
#     """

#     print("Code to generate summary:\n")
#     print("-" * 50)
#     print(code)
#     print("-" * 50)
#     response = code_summary_chatgpt(code, examples, debug=True)

#     print("Generated summary:\n")
#     print("-" * 50)
#     print(response)


def test_code_summary_chatgpt():
    """Test code with fixed code snippet"""

    test_code_snippets = [
    """
static inline uint16_t erp_prv_template_set_l3(uint16_t prv_tmpl, uint8_t value)
{
                prv_tmpl &= ~(0x3 << 4);
                return prv_tmpl | ((value & 0x3) << 4);
}
    """,
    """ec_operate_push(\n	struct channel *channel,\n	struct ec_operate *params)\n{\n	struct flow *f = erasure_to_flow();\n\n	channel_push(channel, ec_operate, flow_dest(f), f, params);\n	erasure_get_matrix_or_push(channel, f, params);\n}
    """
    ]
    for code in test_code_snippets:
        # code_summary = code_summary_chatgpt(code, examples, debug=True)
        print("# Function to document (summary generation):\n")
        print("-" * 50)
        print(code)
        print("-" * 50)
        response = code_summary_chatgpt(code, examples, debug=True)
        print()

        print("# Generated summary:\n")
        print("-" * 50)
        print(response)
        print()

def main() -> None:
    """Main function"""

    # test_code_summary_chatgpt()
    args = _get_args()

    setup_api(args.model)

    if args.test:
        test_code_summary_chatgpt()
        return

    # generate data time string

    dt_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_file = args.output_file + "_" + dt_string

    generate_code_summary(args.input_file, output_file, examples, args.model, args.debug)

if __name__ == "__main__":
    main()
