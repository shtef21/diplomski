

class Dipl_PlotInfo:
  def __init__(self, user_count, value_amt, color):
    self.user_str = str(user_count).replace('0000', '0K').replace('000', 'K')
    self.val = value_amt
    self.color = color
