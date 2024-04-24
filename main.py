# pip install confluent-kafka

import python_test.helpers.utils as dipl_utils

users, posts = dipl_utils.get_mocks(overwrite_prev=True, show_logs=True)

assert len(users) > 0 and len(posts) > 0, "Some or all mocked data missing"

# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
