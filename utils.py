# -*- coding: utf-8 -*-
"""
Utilities.

For now: a logger, that prints to stdout.
See: http://stackoverflow.com/questions/2302315/how-can-info-and-debug-logging-message-be-sent-to-stdout-and-higher-level-messag#answer-9323805
"""

import sys
import logging

logger = logging.getLogger('Радуга')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler( sys.__stdout__ )
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

