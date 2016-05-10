# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

import main
import views
import utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekend(self):
        """
        Test mean time weekend
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertIsInstance(data, list)

    def test_presence_weekday_view(self):
        """
        Test presence weekday
        """
        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertIsInstance(data, list)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test group by weekend
        """
        sample_date = datetime.date(2013, 9, 12)
        d = {sample_date: {'end': datetime.time(23, 23, 51),
                           'start': datetime.time(10, 48, 46)}}
        data = utils.group_by_weekday(d)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 7)
        self.assertTrue(datetime.datetime.strptime(
            str(sample_date), '%Y-%m-%d'))
        self.assertLess(d[sample_date]['end'].hour, 24)
        self.assertLess(d[sample_date]['end'].minute, 60)
        self.assertLess(d[sample_date]['end'].second, 60)
        self.assertLess(d[sample_date]['start'].hour, 24)
        self.assertLess(d[sample_date]['start'].minute, 60)
        self.assertLess(d[sample_date]['start'].second, 60)

    def test_seconds_since_midnight(self):
        sample_date = datetime.time(23, 59, 59)
        date = utils.seconds_since_midnight(sample_date)
        self.assertIsInstance(sample_date.hour, int)
        self.assertIsInstance(sample_date.minute, int)
        self.assertIsInstance(sample_date.second, int)
        self.assertLess(sample_date.hour, 24)
        self.assertGreater(sample_date.hour, -1)
        self.assertLess(sample_date.minute, 60)
        self.assertGreater(sample_date.minute, -1)
        self.assertLess(sample_date.second, 60)
        self.assertGreater(sample_date.second, -1)

    def test_interval(self):
        start_date = datetime.time(10, 10, 10)
        end_date = datetime.time(12, 10, 10)
        date = utils.interval(start_date, end_date)
        self.assertLess(start_date, end_date)

    def test_mean(self):
        lista = [-33031, 32113, 32113, 32113, 54154, 32112, 31123]
        date = utils.mean(lista)
        self.assertIsInstance(date, float)
        self.assertNotEqual(lista, [])
        self.assertGreater(date, -1)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
