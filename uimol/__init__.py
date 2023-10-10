"""
 :author: vic on 2023-10-07
"""
import random


def _randhexbyte():
    return hex(random.randint(0, 256))[2:].zfill(2)


def generate_swatch(colors: int = 1):
    """
    To generate an array of colors at random
    :param colors: number of colors to generate
    :return: an array of colors at random in hex string
    """
    return ['#' + _randhexbyte() + _randhexbyte() + _randhexbyte() for i in range(colors)]
