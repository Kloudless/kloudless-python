import unittest
import os
import requests
import datetime
import time

skipSeleniumTests = None
try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
except ImportError:
    skipSeleniumTests = lambda: unittest.skipTest(
        "Selenium not installed.")

import utils
import sdk

class Link(unittest.TestCase):

    def setUp(self):
        self.test_file = utils.create_test_file(self.account)
        self.link = self.account.links.create(file_id=self.test_file.id)

    def tearDown(self):
        self.link.delete()

    def test_create_link(self):
        self.assertEqual(self.link.file_id, self.test_file.id)

    def test_create_direct_link(self):
        self.link2 = self.account.links.create(file_id=self.test_file.id, direct=True)
        r = requests.get(self.link2.url)
        self.assertEqual(r.text, 'test')
        self.link2.delete()

    def test_list_links(self):
        names = [f.id for f in self.account.links.all()]
        self.assertTrue(self.link.id in names)

    def test_create_bad_link(self):
        with self.assertRaises(sdk.exceptions.APIException) as e:
            self.link = self.account.links.create(file_id='bad_file_id')

    def test_list_links_page_size(self):
        links = self.account.links.all(page_size=1)
        self.assertEqual(1, len(links))

    def test_list_active_links(self):
        links = self.account.links.all(active=True)
        for link in links:
            self.assertTrue(link.active)

    def test_create_password_link(self):
        if skipSeleniumTests:
            skipSeleniumTests()

        self.link = self.account.links.create(file_id=self.test_file.id, password='testytest')
        self.assertTrue(self.link.password)
        driver = webdriver.Firefox()
        driver.get(self.link.url)
        driver.find_element_by_id('id_password').send_keys('testytest')
        driver.find_element_by_name('form-submit').click()
        self.assertTrue('password entered is incorrect' not in driver.page_source)
        driver.close()

    def test_retrieve_link(self):
        retrieved = self.account.links.retrieve(id=self.link.id)
        self.assertEqual(self.link.id, retrieved.id)

    def test_update_password_link(self):
        if skipSeleniumTests:
            skipSeleniumTests()

        self.link.password = 'testytest'
        current_time = datetime.datetime.now().isoformat()
        self.link.save(file_id=self.test_file.id)
        link = self.account.links.retrieve(id=self.link.id)
        driver = webdriver.Firefox()
        driver.get(link.url)
        driver.find_element_by_id('id_password').send_keys('testytest')
        driver.find_element_by_name('form-submit').click()
        self.assertTrue('password entered is incorrect' not in driver.page_source)
        driver.close()

    def test_update_active_link(self):
        self.link.active = False
        self.link.save(file_id=self.test_file.id)
        r = requests.get(self.link.url)
        self.assertFalse(self.link.active)
        self.assertIn(r.status_code, [403, 404])

    def test_update_expired_link(self):
        self.link.expiration = datetime.datetime.utcnow().isoformat()
        self.link.save(file_id=self.test_file.id)
        r = requests.get(self.link.url)
        self.assertIn(r.status_code, [403, 404])

def test_cases():
    return [utils.create_test_case(acc, Link) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
