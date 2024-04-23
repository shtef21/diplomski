# pip install confluent-kafka

import python_test.helpers.utils as dipl_utils
import sys

users, posts = dipl_utils.get_mocks(overwrite_prev=True)

print(f"""
  Generated {len(users)} users and {len(posts)} posts.
""")



# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
