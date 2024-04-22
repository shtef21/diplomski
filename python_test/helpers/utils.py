import json


def generate_mock(params):
  pass


def save_json(data, path):
  with open(path, 'w') as file:
    json.dump(data, file)


# TODO: make a function that generates mocks (and add it to .gitignore)
