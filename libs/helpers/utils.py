import sys
import json
#from dateutil.parser import parse as parse_date


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
  

# Check if cmd argument such as "--testing" is sent.
def cmd_arg_exists(argname):
  if len(sys.argv) < 2:
    return False
  
  for el in sys.argv[1:]:
    if el.lower() == argname.lower():
      return True
  return False
