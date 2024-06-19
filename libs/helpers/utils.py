import sys
import json


def data_to_json(data) -> str:
  return json.dumps(data)

def json_to_data(json_str):
  return json.loads(json_str)


def int_to_bytes(num: int):
  return num.to_bytes(2, 'little')

def bytes_to_int(byte_arr: bytes):
  return int.from_bytes(byte_arr, 'little')


def save_json(data, path):
  with open(path, 'w') as file:
    json.dump(data, file)

def read_json(path):
  with open(path) as file:
    return json.load(file)
