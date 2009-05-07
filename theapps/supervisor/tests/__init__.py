#from basic import BASIC_TESTS
from middleware import DeviceTest
from cookie import CookieTest

__test__ = {
    #'BASIC_TESTS': BASIC_TESTS,
    'COOKIE_TESTS': CookieTest,
    'DEVICE_TESTS': DeviceTest,
}