import datetime
import decimal

from flatland import (
    Boolean,
    Date,
    DateTime,
    Decimal,
    Float,
    Integer,
    Long,
    Scalar,
    String,
    Time,
    Unset,
    )

from tests._util import eq_, assert_raises, requires_unicode_coercion


def test_scalar_abstract():
    el = Scalar()
    assert_raises(NotImplementedError, el.set, 'blagga')


def test_scalar_assignments_are_independent():
    element = Scalar()

    assert not element.u
    assert not element.value
    element.u = 'abc'
    assert element.value is None

    element = Scalar()
    assert not element.u
    assert not element.value
    element.value = 'abc'
    eq_(element.u, '')
    eq_(element.value, 'abc')


def test_scalar_set_flat():
    # Scalars take on the first value if duplicates are present.
    class SimpleScalar(Scalar):

        def adapt(self, value):
            return value

    data = (('a', '1'),
            ('b', '2'),
            ('a', '3'))

    def element_for(name):
        element = SimpleScalar(name=name)
        element.set_flat(data)
        return element

    eq_(element_for('a').value, '1')
    eq_(element_for('a').raw, '1')
    eq_(element_for('b').value, '2')
    eq_(element_for('b').raw, '2')
    eq_(element_for('c').value, None)
    eq_(element_for('c').raw, Unset)


@requires_unicode_coercion
def test_string():
    for value, expected in (('abc', 'abc'), ('abc', 'abc'), (123, '123'),
                            ('abc ', 'abc'), (' abc ', 'abc')):
        for element in String(), String(strip=True):
            element.set(value)
            eq_(element.u, expected)
            eq_(str(element), expected)
            eq_(element.value, expected)

    for value, expected in (('abc ', 'abc '), (' abc ', ' abc ')):
        element = String(value, strip=False)
        eq_(element.u, expected)
        eq_(str(element), expected)
        eq_(element.value, expected)

    for value, expected_value, expected_unicode in (('', '', ''),
                                                    (None, None, '')):
        element = String(value)
        eq_(element.u, expected_unicode)
        eq_(str(element), expected_unicode)
        eq_(element.value, expected_value)


def test_string_is_empty():
    element = String('')
    assert element.is_empty

    element = String('foo')
    assert not element.is_empty


def validate_element_set(type_, raw, value, uni, schema_opts={},
                         set_return=None):
    if set_return is None:
        set_return = value is not None
    element = type_(**schema_opts)
    eq_(element.set(raw), set_return)
    eq_(element.value, value)
    eq_(element.u, uni)
    eq_(str(element), uni)
    eq_(element.__nonzero__(), bool(uni and value))


coerced_validate_element_set = requires_unicode_coercion(validate_element_set)


def test_scalar_set():
    # a variety of scalar set() failure cases, shoved through Integer
    for spec in (
        (None,       None, '', {}, True),
        ):
        yield (validate_element_set, Integer) + spec

    for spec in (
        ([],         None, '[]'),
        ('\xef\xf0', None, r'\ufffd\ufffd'),
        ):
        yield (coerced_validate_element_set, Integer) + spec


def test_integer():
    for spec in (('123',    123,  '123'),
                 (' 123 ',  123,  '123'),
                 ('xyz',    None, 'xyz'),
                 ('xyz123', None, 'xyz123'),
                 ('123xyz', None, '123xyz'),
                 ('123.0',  None, '123.0'),
                 ('+123',   123,  '123'),
                 ('-123',   -123, '-123'),
                 (' +123 ', 123,  '123'),
                 (' -123 ', -123, '-123'),
                 ('+123',   123,  '123', dict(signed=False)),
                 ('-123',   None, '-123', dict(signed=False)),
                 (123,       123,  '123'),
                 (None,      None, '', {}, True)):
        yield (validate_element_set, Integer) + spec

    for spec in ((-123,      None, '-123', dict(signed=False)),):
        yield (coerced_validate_element_set, Integer) + spec


def test_long():
    for spec in (('123',    123,  '123'),
                 (' 123 ',  123,  '123'),
                 ('xyz',    None,  'xyz'),
                 ('xyz123', None,  'xyz123'),
                 ('123xyz', None,  '123xyz'),
                 ('123.0',  None,  '123.0'),
                 ('+123',   123,  '123'),
                 ('-123',   -123, '-123'),
                 (' +123 ', 123,  '123'),
                 (' -123 ', -123, '-123'),
                 ('+123',   123,  '123', dict(signed=False)),
                 ('-123',   None,  '-123', dict(signed=False)),
                 (None,      None,  '', {}, True)):
        yield (validate_element_set, Long) + spec


def test_float():
    for spec in (('123',    123.0,  '123.000000'),
                 (' 123 ',  123.0,  '123.000000'),
                 ('xyz',    None,   'xyz'),
                 ('xyz123', None,   'xyz123'),
                 ('123xyz', None,   '123xyz'),
                 ('123.0',  123.0,  '123.000000'),
                 ('+123',   123.0,  '123.000000'),
                 ('-123',   -123.0, '-123.000000'),
                 (' +123 ', 123.0,  '123.000000'),
                 (' -123 ', -123.0, '-123.000000'),
                 ('+123',   123.0,  '123.000000', dict(signed=False)),
                 ('-123',   None,   '-123', dict(signed=False)),
                 (None,      None,   '', {}, True)):
        yield (validate_element_set, Float) + spec

    class TwoDigitFloat(Float):
        format = '%0.2f'

    for spec in (('123',     123.0,   '123.00'),
                 (' 123 ',   123.0,   '123.00'),
                 ('xyz',     None,    'xyz'),
                 ('xyz123',  None,    'xyz123'),
                 ('123xyz',  None,    '123xyz'),
                 ('123.0',   123.0,   '123.00'),
                 ('123.00',  123.0,   '123.00'),
                 ('123.005', 123.005, '123.00'),
                 (None,       None,    '', {}, True)):
        yield (validate_element_set, TwoDigitFloat) + spec


def test_decimal():
    d = decimal.Decimal
    for spec in (('123',    d('123'),   '123.000000'),
                 (' 123 ',  d('123'),   '123.000000'),
                 ('xyz',    None,       'xyz'),
                 ('xyz123', None,       'xyz123'),
                 ('123xyz', None,       '123xyz'),
                 ('123.0',  d('123.0'), '123.000000'),
                 ('+123',   d('123'),   '123.000000'),
                 ('-123',   d('-123'), '-123.000000'),
                 (' +123 ', d('123'),   '123.000000'),
                 (' -123 ', d('-123'),  '-123.000000'),
                 (123,       d('123'),   '123.000000'),
                 (-123,      d('-123'),  '-123.000000'),
                 (d(123),    d('123'),   '123.000000'),
                 (d(-123),   d('-123'),  '-123.000000'),
                 ('+123',   d('123'),   '123.000000', dict(signed=False)),
                 ('-123',   None,       '-123', dict(signed=False)),
                 (None,      None,       '', {}, True)):
        yield (validate_element_set, Decimal) + spec

    TwoDigitDecimal = Decimal.using(format='%0.2f')

    for spec in (('123',     d('123.0'),   '123.00'),
                 (' 123 ',   d('123.0'),   '123.00'),
                 ('12.34',   d('12.34'),   '12.34'),
                 ('12.3456', d('12.3456'), '12.35')):
        yield (validate_element_set, TwoDigitDecimal) + spec


def test_boolean():
    for ok in Boolean.true_synonyms:
        yield validate_element_set, Boolean, ok, True, '1'
        yield (validate_element_set, Boolean, ok, True, 'baz',
               dict(true='baz'))

    for not_ok in Boolean.false_synonyms:
        yield validate_element_set, Boolean, not_ok, False, ''
        yield (validate_element_set, Boolean, not_ok, False, 'quux',
               dict(false='quux'))

    for bogus in 'abc', '1.0', '0.0', 'None':
        yield validate_element_set, Boolean, bogus, None, bogus

    for coercable in {}, 0:
        yield validate_element_set, Boolean, coercable, False, ''


def test_scalar_set_default():
    el = Integer()
    el.set_default()
    assert el.value is None

    el = Integer(default=10)
    el.set_default()
    assert el.value == 10

    el = Integer(default_factory=lambda e: 20)
    el.set_default()
    assert el.value == 20


def test_date():
    t = datetime.date
    for spec in (
        ('2009-10-10',   t(2009, 10, 10), '2009-10-10'),
        ('2010-08-02',   t(2010, 8, 2), '2010-08-02'),
        (' 2010-08-02 ', t(2010, 8, 2), '2010-08-02'),
        (' 2010-08-02 ', None, ' 2010-08-02 ', dict(strip=False)),
        ('2011-8-2',     None, '2011-8-2'),
        ('blagga',       None, 'blagga'),
        (None,            None, '', {}, True)):
        yield (validate_element_set, Date) + spec


def test_time():
    t = datetime.time
    for spec in (
        ('08:09:10', t(8, 9, 10),  '08:09:10'),
        ('23:24:25', t(23, 24, 25), '23:24:25'),
        ('24:25:26', None,          '24:25:26'),
        ('bogus',    None,          'bogus'),
        (None,        None,          '',         {}, True)):
        yield (validate_element_set, Time) + spec


def test_datetime():
    t = datetime.datetime
    for spec in (
        ('2009-10-10 08:09:10', t(2009, 10, 10, 8, 9, 10),
         '2009-10-10 08:09:10'),
        ('2010-08-02 25:26:27', None, '2010-08-02 25:26:27'),
        ('2010-13-22 09:09:09', None, '2010-13-22 09:09:09'),
        (None,                   None, '', {}, True)):
        yield (validate_element_set, DateTime) + spec
