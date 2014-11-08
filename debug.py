# Name: Edward Takahashi
#
# file description:
#    used to debug. Uncomment line 13 will turn on debugging statement
#    
#

import logging
import sys



#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def debug(text):
    logging.debug(text)