#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json_parser.py
@Author : yell
@Desc : json parser 
'''

import json
import gzip
import os
from .log import Logger

class JsonParser:
    """basic json parser"""

    def __init__(self, json_path: str, logger : Logger):
        self.json_path = json_path
        self.logger : Logger= logger
        self.json_data = None

    def set_json_data(self, value: dict):
        self.json_data = value

    def get_json_data(self):
        ''' access to json data '''
        return self.json_data

    def get_value(self, node_json, key):
        if key in node_json:
            return node_json[key]
        else:
            return None

    def read(self):
        ''' Json reader '''
        if not os.path.exists(self.json_path):
            self.logger.error("json file not exist. path = %s", self.json_path)
            return False

        try:
            # compressed
            if self.json_path.endswith(".gz"):
                with gzip.open(self.json_path, 'r') as f:
                    unzip_data = f.read().decode('utf-8')
                    self.json_data = json.loads(unzip_data)
            else:
                with open(self.json_path, 'r', encoding='utf-8') as f_reader:
                    self.json_data = json.load(f_reader)

            return True
        except json.JSONDecodeError:
            self.logger.error(
                "json file format error. path = %s", self.json_path)
            return False

    def read_create(self):
        if not os.path.exists(self.json_path):
            # create file
            self.json_data = {}
            self.write()

        return self.read()

    def write(self, dict_value: dict = None):
        if dict_value != None:
            self.json_data = dict_value

        ''' Json writer '''
        if self.json_path.endswith(".gz"):
            with gzip.open(self.json_path, 'wb') as f:
                zip_data = json.dumps(self.json_data, indent=4)
                f.write(zip_data.encode('utf-8'))
        else:
            with open(self.json_path, 'w', encoding='utf-8') as f_writer:
                json.dump(self.json_data, f_writer, indent=4)

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
    
    def print_json(self):
        if self.read() is True:
            self.logger.info("########################################################")
            self.logger.info("#                   parameters start                   #")
            self.logger.info("########################################################")
            self.logger.info("\n%s", json.dumps(self.json_data, indent=4))
            self.logger.info("########################################################")
            self.logger.info("#                   parameters end                     #")
            self.logger.info("########################################################\n")
        else:
            self.logger.error("json data error : %s", self.json_path)