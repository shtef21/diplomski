from enum import Enum
import os
import random
from datetime import datetime, timedelta
from tqdm import tqdm

from .utils import save_json as dipl_save_json, read_json as dipl_read_json


DIPL_GENDER_MALE = 0
DIPL_GENDER_FEMALE = 1

# User wrapper that improves linting
class Dipl_MockedUser:
  def __init__(self, **kwargs):
    self.id: int = kwargs['id']
    self.username: str = kwargs['username']
    self.email: str = kwargs['email']
    self.joined: str = kwargs['joined']
    self.gender: int = kwargs['gender']
    self.location: str = kwargs['location']
    self.birth_date: str = kwargs['birth_date']



class Dipl_MockGenerator:

  def __init__(self, overwrite_prev=False, show_logs=False):
    users = get_mocks(
      overwrite_prev=overwrite_prev,
      show_logs=show_logs
    )
    self.user_iterator = self.__get_user_iterator(users)

  def get_users(self, count) -> list[Dipl_MockedUser]:
    return [next(self.user_iterator) for _ in range(count)]
  
  def show_some_data(self):
    print('Example user:')
    print('\t', self.get_users(1)[0])
    print('Getting 1 million users...', end='')
    print(
      ' Done fetching',
      len(self.get_users(1_000_000)),
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


def get_mocks(**kwargs) -> list[Dipl_MockedUser]:
  """
  Sets up and return mocks (generate and save to JSON if they do not already exist).
  
  kwargs:
    - overwrite_prev (bool) - choose if new mocks should be created if old ones exist
    - show_logs (bool)
  """

  save_dir = './libs/mocks'
  users_path = f'{save_dir}/users.json'
  user_mocks: list[Dipl_MockedUser] = []

  if os.path.isdir(save_dir) == False:
    os.mkdir(save_dir)

  if kwargs.get('overwrite_prev', False) \
    or not os.path.exists(users_path):

    user_mocks = generate_mock_data()
    print('Saving users...')
    dipl_save_json(
      [user.__dict__ for user in user_mocks],
      users_path
    )

  else:
    user_dict_arr = dipl_read_json(users_path)
    user_mocks = [
      Dipl_MockedUser(**user_dict)
      for user_dict in user_dict_arr
    ]

  if kwargs.get('show_logs', False):
    users_size_mb = os.path.getsize(users_path) / 1024 / 1024
    print(f'Read file "{users_path}": {round(users_size_mb, 2)} MB ({len(user_mocks)} rows)')

  return user_mocks


# Generates mock data (without saving it)
def generate_mock_data():
  user_mocks: list[Dipl_MockedUser] = []
  user_num = 100_000
  datetime_limit = datetime(1940, 1, 1)

  def rand_datetime(start, end):
    delta = end - start
    random_days = random.randint(1, delta.days)
    new_date = start + timedelta(days=random_days)
    return new_date

  print('Generating users...')
  for user_id in tqdm(range(1, user_num + 1)):
    birth_date = rand_datetime(datetime_limit, datetime.now())
    joined_date = datetime.now() + timedelta(days=random.randint(-1000, -3))
    location = f'Location_{random.randint(1, 100)}'
    user_gender = DIPL_GENDER_MALE if user_id % 2 == 0 else DIPL_GENDER_FEMALE

    social_media_user_mock = Dipl_MockedUser(
      id=user_id,
      username=f'user_{user_id}',
      email=f'user_{user_id}@example.com',
      joined=joined_date.strftime('%Y-%m-%d'),
      gender=user_gender,
      location=location,
      birth_date=birth_date.strftime('%Y-%m-%d')
    )
    user_mocks.append(social_media_user_mock)

  return user_mocks

