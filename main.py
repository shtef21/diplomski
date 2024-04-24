# pip install confluent-kafka

import python_test.helpers.utils as dipl_utils
import sys
import time

users, posts = dipl_utils.get_mocks(show_logs=True)

# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
