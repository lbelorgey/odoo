# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import unittest

import odoo
from odoo.sql_db import TestCursor
from odoo.tests import common
from odoo.tools.misc import mute_logger

ADMIN_USER_ID = common.ADMIN_USER_ID

def registry():
    return odoo.registry(common.get_db_name())


class TestExecute(unittest.TestCase):
    """ Try cr.execute with wrong parameters """

    @mute_logger('odoo.sql_db')
    def test_execute_bad_params(self):
        """
        Try to use iterable but non-list or int params in query parameters.
        """
        with registry().cursor() as cr:
            with self.assertRaises(ValueError):
                cr.execute("SELECT id FROM res_users WHERE login=%s", 'admin')
            with self.assertRaises(ValueError):
                cr.execute("SELECT id FROM res_users WHERE id=%s", 1)
            with self.assertRaises(ValueError):
                cr.execute("SELECT id FROM res_users WHERE id=%s", '1')


class TestTestCursor(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestTestCursor, cls).setUpClass()
        registry().enter_test_mode()

    @classmethod
    def tearDownClass(cls):
        registry().leave_test_mode()
        super(TestTestCursor, cls).tearDownClass()

    def setUp(self):
        super(TestTestCursor, self).setUp()
        self.record = self.env['res.partner'].create({'name': 'Foo'})

    def write(self, record, value):
            record.ref = value

    def check(self, record, value):
            self.assertEqual(record.read(['ref'])[0]['ref'], value)

    def test_single_cursor(self):
        """ Check the behavior of a single test cursor. """
        self.assertIsInstance(self.cr, TestCursor)
        self.write(self.record, 'A')
        self.cr.commit()

        self.write(self.record, 'B')
        self.cr.rollback()
        self.check(self.record, 'A')

        self.write(self.record, 'C')
        self.cr.rollback()
        self.check(self.record, 'A')

    def test_sub_commit(self):
        """ Check the behavior of a subcursor that commits. """
        self.assertIsInstance(self.cr, TestCursor)
        self.write(self.record, 'A')
        self.cr.commit()

        self.write(self.record, 'B')

        # check behavior of a "sub-cursor" that commits
        with self.registry.cursor() as cr:
            self.assertIsInstance(cr, TestCursor)
            record = self.record.with_env(self.env(cr=cr))
            self.check(record, 'B')
            self.write(record, 'C')

        self.check(self.record, 'C')

        self.cr.rollback()
        self.check(self.record, 'A')

    def test_sub_rollback(self):
        """ Check the behavior of a subcursor that rollbacks. """
        self.assertIsInstance(self.cr, TestCursor)
        self.write(self.record, 'A')
        self.cr.commit()

        self.write(self.record, 'B')

        # check behavior of a "sub-cursor" that rollbacks
        with self.assertRaises(ValueError):
            with self.registry.cursor() as cr:
                self.assertIsInstance(cr, TestCursor)
                record = self.record.with_env(self.env(cr=cr))
                self.check(record, 'B')
                self.write(record, 'C')
                raise ValueError(42)

        self.check(self.record, 'B')

        self.cr.rollback()
        self.check(self.record, 'A')


class TestCursorHooks(common.TransactionCase):
    def test_hooks(self):
        log = []

        def make_hook(msg):
            def hook():
                log.append(msg)
            return hook

        cr = self.registry.cursor()

        # check hook on commit()
        cr.after('commit', make_hook('C1'))
        cr.after('rollback', make_hook('R1'))
        self.assertEqual(log, [])
        cr.commit()
        self.assertEqual(log, ['C1'])

        # check hook on rollback()
        cr.after('commit', make_hook('C2'))
        cr.after('rollback', make_hook('R2'))
        self.assertEqual(log, ['C1'])
        cr.rollback()
        self.assertEqual(log, ['C1', 'R2'])

        # check hook on close()
        cr.after('commit', make_hook('C3'))
        cr.after('rollback', make_hook('R3'))
        self.assertEqual(log, ['C1', 'R2'])
        cr.close()
        self.assertEqual(log, ['C1', 'R2', 'R3'])
