import sys
import os
import json
import random
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from tqdm import tqdm


# Sets up and return mocks (generate and save to JSON if they do not already exist)
def get_mocks(overwrite_prev=False):
  save_dir = './python_test/mocks'
  users_path = f'{save_dir}/users.json'
  posts_path = f'{save_dir}/posts.json'
  user_mocks = []
  post_mocks = []

  if os.path.isdir(save_dir) == False:
    os.mkdir(save_dir)

  if overwrite_prev or not os.path.exists(users_path) or not os.path.exists(posts_path):
    if os.path.exists(users_path):
      os.remove(users_path)
    if os.path.exists(posts_path):
      os.remove(posts_path)

    user_mocks, post_mocks = generate_mock_data()
    print('Saving users...')
    save_json(user_mocks, users_path)
    print('Saving posts...')
    save_json(post_mocks, posts_path)

  else:
    user_mocks = read_json(users_path)
    post_mocks = read_json(posts_path)

  return user_mocks, post_mocks


# Generates mock data (without saving it)
def generate_mock_data():
  user_mocks = []
  post_mocks = []
  user_num = 1000000
  post_num = user_num // 2
  datetime_limit = datetime(1940, 1, 1)

  def rand_datetime(start, end):
    delta = end - start
    random_days = random.randint(1, delta.days)
    new_date = start + timedelta(days=random_days)
    return new_date

  print('Generating users...')
  for user_id in tqdm(range(1, user_num + 1)):
    birthday = rand_datetime(datetime_limit, datetime.now())
    joined_date = datetime.now() + timedelta(days=random.randint(-1000, -3))
    location = f'Location_{random.randint(1, 100)}'

    social_media_user_mock = {
      'id': user_id,
      'username': f'user_{user_id}',
      'email': f'user_{user_id}@example.com',
      'joined': joined_date.strftime('%Y-%m-%d'),
      'location': location,
      'birthday': birthday.strftime('%Y-%m-%d')
    }
    user_mocks.append(social_media_user_mock)

  print('Generating posts...')
  for post_id in tqdm(range(1, post_num + 1)):
    author = user_mocks[random.randint(0, len(user_mocks) - 1)]
    content = 'This is some random post content'
    timestamp = rand_datetime(parse_date(author['joined']), datetime.now())
    likes = random.randint(0, 250)
    comments = random.randint(0, 25)

    social_media_post_mock = {
      'id': post_id,
      'author_id': author['id'],
      'content': content,
      'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
      'likes': likes,
      'comments': comments
    }
    post_mocks.append(social_media_post_mock)

  return user_mocks, post_mocks


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
