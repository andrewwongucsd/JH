#!/usr/bin/env python
from globalvar import *
from selenium import webdriver

def getBrowser(service_args):
    return webdriver.PhantomJS(service_args = service_args)