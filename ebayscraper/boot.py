from subprocess import Popen, PIPE
import os

import ebaychecker


print 'hey'
try:
    local = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(local, 'ebaychecker.py')
    print file_path
    print 'let\'s try this'

    os.system(file_path)
    # process = Popen(file_path, stdout=PIPE, stderr=PIPE)
    # stdout, stderr = process.communicate()
    #
    #
    #
    print 'it worked...'
    #
    # print stdout
    # print stderr

except Exception, e:
    'print it out {}'.format(e)
