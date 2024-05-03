import os
import random
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from tqdm import tqdm

from .utils import save_json as dipl_save_json, read_json as dipl_read_json


class MockGenerator:

  def __init__(self, overwrite_prev=False, show_logs=False):
    users, posts = get_mocks(
      overwrite_prev=overwrite_prev,
      show_logs=show_logs
    )
    self.user_iterator = self.__get_user_iterator(users)
    self.post_iterator = self.__post_iterator(posts)

  def get_single_user(self):
    return next(self.user_iterator)
  
  def get_single_post(self):
    return next(self.post_iterator)
  
  def get_many_users(self, count):
    return [self.get_single_user() for _ in range(count)]
  
  def get_many_posts(self, count):
    return [self.get_single_post() for _ in range(count)]
  
  def show_some_data(self):
    print('Example user:')
    print('\t', self.get_single_user())
    print('Example post:')
    print('\t', self.get_single_post())
    print('Getting 1 million posts...', end='')
    print(
      ' Done fetching',
      len(self.get_many_posts(1000000)),
      'posts.'
    )


  # Internal generator function for users
  def __get_user_iterator(self, users):
    i = 0
    while i < len(users):
      if i < len(users):
        yield users[i]
        i += 1
      if i == len(users):
        i = 0

  # Internal generator function for posts
  def __post_iterator(self, posts):
    i = 0
    while i < len(posts):
      if i < len(posts):
        yield posts[i]
        i += 1
      if i == len(posts):
        i = 0


def get_mocks(**kwargs):
  """
  Sets up and return mocks (generate and save to JSON if they do not already exist).
  
  kwargs:
    - overwrite_prev (bool) - choose if new mocks should be created if old ones exist
    - show_logs (bool)
  """

  save_dir = './python_test/mocks'
  users_path = f'{save_dir}/users.json'
  posts_path = f'{save_dir}/posts.json'
  user_mocks = []
  post_mocks = []

  if os.path.isdir(save_dir) == False:
    os.mkdir(save_dir)

  if kwargs.get('overwrite_prev', False) \
    or not os.path.exists(users_path) \
    or not os.path.exists(posts_path):

    user_mocks, post_mocks = generate_mock_data()
    print('Saving users...')
    dipl_save_json(user_mocks, users_path)
    print('Saving posts...')
    dipl_save_json(post_mocks, posts_path)

  else:
    user_mocks = dipl_read_json(users_path)
    post_mocks = dipl_read_json(posts_path)

  if kwargs.get('show_logs', False):
    users_size_mb = os.path.getsize(users_path) / 1024 / 1024
    posts_size_mb = os.path.getsize(posts_path) / 1024 / 1024
    print(f'Read file "{users_path}": {round(users_size_mb, 2)} MB ({len(user_mocks)} rows)')
    print(f'Read file "{posts_path}": {round(posts_size_mb, 2)} MB ({len(post_mocks)} rows)')

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
    is_male = user_id % 2 == 0

    social_media_user_mock = {
      'id': user_id,
      'username': f'user_{user_id}',
      'email': f'user_{user_id}@example.com',
      'joined': joined_date.strftime('%Y-%m-%d'),
      'sex': is_male,
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
