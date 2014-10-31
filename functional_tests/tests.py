from django.test import LiveServerTestCase
from selenium import webdriver


class WikiDocsTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test1(self):
        print "hello"
        print self.live_server_url
        self.browser.get(self.live_server_url)
