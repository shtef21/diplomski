import os
import random
from datetime import datetime, timedelta
from tqdm import tqdm

from .proj_config import mocked_data_dir
from .utils import save_json as dipl_save_json, read_json as dipl_read_json
from ..models.mocked_user import Dipl_MockedUser


DIPL_GENDER_MALE = 0
DIPL_GENDER_FEMALE = 1


class Dipl_MockGenerator:

  def __init__(self, overwrite_prev=False, show_logs=False):
    users = get_mocks(
      overwrite_prev=overwrite_prev,
      show_logs=show_logs
    )
    self.user_iterator = self.__get_user_iterator(users)

  def get_users(self, count) -> list[Dipl_MockedUser]:
    return [next(self.user_iterator) for _ in range(count)]

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

  users_path = f'{mocked_data_dir}/users.json'
  user_mocks: list[Dipl_MockedUser] = []

  if os.path.isdir(mocked_data_dir) == False:
    os.mkdir(mocked_data_dir)

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
