from subprocess import Popen, PIPE
import sys
import os

import socket
print(socket.gethostname())

from LoggerAndArchiver import logger

logger = logger.build_logger(name='tester', level='DEBUG')


print 'hey'
try:
    local = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(local, 'Test/scratch.py')
    # file_path = os.path.join(local, 'ebaychecker.py')

    communicator = Popen(['python', file_path, logger], stdout=PIPE, stderr=PIPE)
    stdout, stderr = communicator.communicate()

    print 'Our output: {}'.format(stdout)
    print 'our error: {}'.format(stderr)

    logger.info('Our output: {}'.format(stdout))
    logger.info('our error: {}'.format(stderr))


    # logger.info(os.system(file_path))


    print 'it worked...'


except Exception, e:
    'print it out {}'.format(e)
