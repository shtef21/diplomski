# pip install confluent-kafka

import python_test.helpers.utils as dipl_utils
from python_test.helpers.mock_generator import MockGenerator

mocks = MockGenerator(show_logs=True)

print('Example user:')
print(mocks.get_user())

print('Example post:')
print(mocks.get_post())

# print('Getting 1 million posts.')
# _1m_users = mocks.get_many_users(1000000)
# print('Done')



# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
