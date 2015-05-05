#-*- encoding: utf-8 -*-

from . import default_settings


def Settings(opt_name):
    return getattr(default_settings, opt_name)


if __name__ == '__main__':
    print Settings('THREADNUM')