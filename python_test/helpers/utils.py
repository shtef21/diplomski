import sys
import json
from dateutil.parser import parse as parse_date


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
