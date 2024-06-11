
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
