
from enum import Enum
from .protoc_out import user_pb2


class Dipl_GenderPb2_Wrapper(Enum):
  MALE = 0
  FEMALE = 1

class Dipl_UserPb2_Wrapper:
  def __init__(self, u: user_pb2):
    self.id = u.id
    self.username = u.username
    self.email = u.email
    self.joined = u.joined
    self.gender: Dipl_GenderPb2_Wrapper = Dipl_GenderPb2_Wrapper(u.gender)
    self.location = u.location
    self.birthday = u.birthday

class Dipl_UserListPb2_Wrapper:
  def __init__(self, user_list: user_pb2.UserList):
    self.users: list[Dipl_UserPb2_Wrapper] = user_list
