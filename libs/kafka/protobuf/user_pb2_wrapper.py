
from protoc_out import user_pb2

class Dipl_UserPb2_Wrapper:
  pass   # TODO, finish this

class Dipl_UserListPb2_Wrapper:
  def __init__(self, u: user_pb2):
    self.users = 
    self.id = u.id
    self.username = u.username
    self.email = u.email
    self.joined = u.joined
    self.gender = u.gender
    self.location = u.location
    self.birthday = u.birthday
