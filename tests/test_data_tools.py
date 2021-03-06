# -*- coding: utf-8 -*-

from dmutils.data_tools import ValidationError, normalise_abn, normalise_acn, parse_money

import decimal


class TestNormaliseAcn(object):

    def test_basic_normalisation(self):
        assert normalise_acn(' 004085616 ') == '004 085 616'

    def test_good_acn_formats(self):
        golden = '004 085 616'
        cases = [
            '004 085 616',
            '004-085-616',
            '004085616',
            ' 00    4085616 ',
            ' 004085616',
            ' 0 0 4 0 8 5 6 1 6 ',
            ' 0-0  4-0 856 1 6 ',
        ]
        for case in cases:
            assert normalise_acn(case) == golden

    def test_bad_acn_formats(self):
        cases = [
            'no',
            'foo@example.com',
            '',
            '1234',
            '1234567',
            '1?',
            'one two three',
        ]
        for case in cases:
            try:
                normalise_acn(case)
            except ValidationError as e:
                assert 'Invalid ACN' in e.message
            else:
                raise Exception('Test failed for case: {}'.format(case))

    def test_bad_acn_checksums(self):
        cases = [
            '704085616',
            '074085616',
            '007085616',
            '004785616',
            '004075616',
            '004087616',
            '004085716',
            '004085676',
            '004085617',
        ]
        for case in cases:
            try:
                normalise_acn(case)
            except ValidationError as e:
                assert 'Checksum failure' in e.message
            else:
                raise Exception('Test failed for case: {}'.format(case))


class TestNormaliseAbn(object):

    def test_basic_normalisation(self):
        assert normalise_abn(' 51824 753556   ') == '51 824 753 556'

    def test_good_abn_formats(self):
        golden = '28 799 046 203'
        cases = [
            '28 799 046 203',
            '28-799-046-203',
            '28799046203',
            '28799 046 203',
            '  28 799 046203',
            '28 799046203           ',
            '28-799046-203',
            '2 8 7 9 9 0 4 6 2 0 3 ',
        ]
        for case in cases:
            assert normalise_abn(case) == golden

    def test_bad_abn_formats(self):
        cases = [
            'no',
            'foo@example.com',
            '',
            '1234',
            '1234567890',
            '1?',
            'one two three',
            '08 799 046 203'
        ]
        for case in cases:
            try:
                normalise_abn(case)
            except ValidationError as e:
                assert 'Invalid ABN' in e.message
            else:
                raise Exception('Test failed for case: {}'.format(case))

    def test_bad_abn_checksums(self):
        cases = [
            '98799046203',
            '29799046203',
            '28999046203',
            '28709046203',
            '28790046203',
            '28799946203',
            '28799096203',
            '28799049203',
            '28799046903',
            '28799046293',
            '28799046209',
        ]
        for case in cases:
            try:
                normalise_abn(case)
            except ValidationError as e:
                assert 'Checksum failure' in e.message
            else:
                raise Exception('Test failed for case: {}'.format(case))


class TestParseMoney(object):

    def test_good_formats(self):
        assert parse_money('1') == decimal.Decimal('1')
        assert parse_money('0') == decimal.Decimal('0')
        assert parse_money('1,000.20') == decimal.Decimal('1000.2')
        assert parse_money('$1,000.20') == decimal.Decimal('1000.2')
        assert parse_money('$1000.30') == decimal.Decimal('1000.3')

    def test_bad_formats(self):
        cases = [
            'no',
            'free',
            '$',
            '$$0',
            '1 2',
            '1..2',
            '+61 00 1234 5678',
        ]
        for case in cases:
            try:
                parse_money(case)
            except ValidationError:
                pass
            else:
                raise Exception('Test failed for case: {}'.format(case))
