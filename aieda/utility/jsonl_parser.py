#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : jsonl_parser.py
@Author : Yihang Qiu
@Desc : jsonl parser 
'''

import json
import gzip
import os
import logging


class JsonlParser:
    """basic jsonl parser"""

    def __init__(self, jsonl_path: str):
        self.jsonl_path = jsonl_path
        self.jsonl_data = []

    def set_jsonl_data(self, value: list):
        self.jsonl_data = value

    def get_jsonl_data(self):
        ''' access to jsonl data '''
        return self.jsonl_data

    def get_value(self, node_json, key):
        if key in node_json:
            return node_json[key]
        else:
            return None

    def read(self):
        ''' Jsonl reader '''
        if not os.path.exists(self.jsonl_path):
            logging.info("error : jsonl file not exist. path = %s",
                         self.jsonl_path)
            return False
        else:
            logging.info("info : start parsing file : %s", self.jsonl_path)

        try:
            # compressed
            if self.jsonl_path.endswith(".gz"):
                with gzip.open(self.jsonl_path, 'rt', encoding='utf-8') as f:
                    self.jsonl_data = [json.loads(line.strip()) for line in f if line.strip()]
            else:
                with open(self.jsonl_path, 'r', encoding='utf-8') as f_reader:
                    self.jsonl_data = [json.loads(line.strip()) for line in f_reader if line.strip()]
            
            logging.info("info : parsing file success")
            return True
        except json.JSONDecodeError:
            logging.info(
                "error : jsonl file format error. path = %s", self.jsonl_path)
            return False

    def read_create(self):
        if not os.path.exists(self.jsonl_path):
            # create file
            self.jsonl_data = []
            self.write()

        return self.read()

    def write(self, list_value: list = None):
        if list_value is not None:
            self.jsonl_data = list_value

        ''' Jsonl writer '''
        if self.jsonl_path.endswith(".gz"):
            with gzip.open(self.jsonl_path, 'wt', encoding='utf-8') as f:
                for item in self.jsonl_data:
                    f.write(json.dumps(item) + '\n')
        else:
            with open(self.jsonl_path, 'w', encoding='utf-8') as f_writer:
                for item in self.jsonl_data:
                    f_writer.write(json.dumps(item) + '\n')

        logging.info("info : write file success")
        return True

    def get_value(self, dict_node, key):
        if isinstance(key, str) and key in dict_node:
            return dict_node[key]

        if isinstance(key, list):
            dict_word = dict_node
            for word in key:
                if word in dict_word:
                    dict_word = dict_word[word]
                else:
                    return None

            return dict_word

        return None
