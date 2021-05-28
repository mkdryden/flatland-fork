from flatland import (
    Array,
    Dict,
    Integer,
    MultiValue,
    String,
    )

from tests._util import eq_, assert_raises


def test_set_flat_pruned():
    sub = String.named('s')
    pairs = [('s', 'val0'), ('s', ''), ('s', 'val1'), ('s', '')]
    wanted = ['val0', 'val1']

    for schema in Array.of(sub), Array.of(sub).using(prune_empty=True):
        el = schema.from_flat(pairs)

        eq_(len(el), len(wanted))
        eq_(el.value, wanted)


def _assert_array_set_flat(schema, pairs, bogus=[]):
    el = schema.from_flat(pairs + bogus)
    eq_(len(el), len(pairs))
    eq_(el.value, list(pair[1] for pair in pairs))
    eq_(el.flatten(), pairs)


def test_set_flat_unpruned():
    pairs = [('s', 'val0'), ('s', ''), ('s', 'val1'), ('s', '')]
    schema = Array.of(String).named('s').using(prune_empty=False)

    _assert_array_set_flat(schema, pairs)


def test_set_flat_like_named():
    pairs = [('s_s', 'abc'), ('s_s', 'def')]
    bogus = [('s', 'xxx')]
    schema = Array.named('s').of(String.named('s'))

    _assert_array_set_flat(schema, pairs, bogus)


def test_set_flat_unnamed_child():
    pairs = [('s', 'abc'), ('s', 'def')]
    bogus = [('', 'xxx')]
    schema = Array.named('s').of(String)

    _assert_array_set_flat(schema, pairs, bogus)


def test_set_flat_anonymous_array():
    schema = Array.of(String.named('s'))
    pairs = [('s', 'abc'), ('s', 'def')]
    bogus = [('', 'xxx')]

    _assert_array_set_flat(schema, pairs, bogus)


def test_set_flat_fully_anonymous_array():
    schema = Array.of(String)
    pairs = [('', 'abc'), ('', 'def')]

    _assert_array_set_flat(schema, pairs)


def test_set_flat_anonymous_dict():
    schema = Array.of(Dict.of(String.named('x')))
    pairs = [('x', 'abc'), ('x', 'def')]
    assert_raises(AssertionError, schema.from_flat, pairs)


def test_set():
    schema = Array.of(Integer)
    el = schema()
    assert not el

    el = schema()
    assert not el.set(1)
    assert not el.value

    el = schema()
    assert el.set([])
    assert not el.value

    el = schema()
    assert el.set([1])
    assert el[0].u == '1'
    assert el.value == [1]
    assert el[0].parent is el

    el = schema()
    assert el.set([1, 2, 3])
    assert el[0].u == '1'
    assert el[0].value == 1
    assert el.value == [1, 2, 3]


def test_set_default():
    schema = Array.of(String).using(default=['x', 'y'])
    el = schema()

    eq_(el.value, [])
    el.set_default()
    eq_(el.value, ['x', 'y'])

    el.append('z')
    eq_(el.value, ['x', 'y', 'z'])
    el.set_default()
    eq_(el.value, ['x', 'y'])

    defaulted_child = String.using(default='not triggered')
    schema = Array.of(defaulted_child).using(default=['x'])

    el = schema.from_defaults()
    eq_(el.value, ['x'])

    schema = Array.of(String.using(default='x'))
    el = schema.from_defaults()
    eq_(el.value, [])


def test_mutation():
    schema = Array.of(String)
    el = schema()
    assert not el

    el.set(['b'])
    assert el[0].u == 'b'
    assert el.value == ['b']

    el.append('x')
    assert el[1].u == 'x'
    assert el.value == ['b', 'x']
    assert el[1].parent is el

    el[1] = 'a'
    assert el[1].u == 'a'
    assert el.value == ['b', 'a']
    assert el[1].parent is el

    el.remove('b')
    assert el.value == ['a']

    el.extend('bcdefg')

    eq_(el.value[0:4], ['a', 'b', 'c', 'd'])
    assert el[2].parent is el

    del el[0]
    eq_(el.value[0:4], ['b', 'c', 'd', 'e'])

    del el[0:4]
    eq_(el.value, ['f', 'g'])

    el.pop()
    eq_(el.value, ['f'])
    eq_(el[0].u, 'f')
    eq_(el.u.encode('ascii'), repr(['f']))

    del el[:]
    eq_(list(el), [])
    eq_(el.value, [])
    eq_(el.u, '[]')

    el[:] = 'abc'
    eq_(el.value, ['a', 'b', 'c'])
    assert el[1].parent is el

    el.insert(1, 'z')
    eq_(el.value, ['a', 'z', 'b', 'c'])
    assert el[1].parent is el

    def assign():
        el.u = 'z'
    assert_raises(AttributeError, assign)
    eq_(el.value, ['a', 'z', 'b', 'c'])

    def assign2():
        el.value = 'abc'
    del el[:]
    assert_raises(AttributeError, assign2)
    eq_(el.value, [])


def test_el():
    schema = Array.of(String.named('s'))
    element = schema('abc')
    eq_(list(element.value), ['a', 'b', 'c'])

    eq_(element.el('0').value, 'a')
    eq_(element.el('2').value, 'c')
    assert_raises(KeyError, element.el, 'a')


def test_multivalue_set():
    schema = MultiValue.of(Integer)
    el = schema()

    eq_(el.value, None)
    eq_(el.u, '')
    eq_(list(el), [])
    eq_(len(el), 0)
    assert not el

    assert not el.set(0)
    assert el.value is None

    assert el.set([])
    assert not el.value

    assert el.set([0])
    eq_(el.value, 0)
    eq_(el.u, '0')
    assert len(el) == 1
    assert el

    el = schema([0, 1])
    eq_(el.value, 0)
    eq_(el.u, '0')
    assert len(el) == 2
    assert el


def test_multivalue_mutation():
    schema = MultiValue.of(Integer)
    el = schema()

    eq_(el.value, None)
    eq_(el.u, '')
    eq_(list(el), [])
    eq_(len(el), 0)
    assert not el

    el.set([1, 2])
    eq_(el.value, 1)
    eq_(el.u, '1')
    eq_(len(el), 2)
    assert el

    el.insert(0, 0)
    eq_(el.value, 0)
    eq_(el.u, '0')
    eq_(len(el), 3)

    el[0].set(9)
    eq_(el.value, 9)
    eq_(el.u, '9')
    eq_([child.value for child in el], [9, 1, 2])
    eq_(len(el), 3)


def _assert_multivalue_set_flat(schema, pairs, bogus=[]):
    el = schema.from_flat(pairs + bogus)
    eq_(len(el), len(pairs))
    eq_(el.value, pairs[0][1])
    eq_(list(e.value for e in el), list(pair[1] for pair in pairs))
    eq_(el.flatten(), pairs)


def test_multivalue_set_flat_unpruned():
    pairs = [('s', 'val0'), ('s', ''), ('s', 'val1'), ('s', '')]
    schema = MultiValue.of(String).named('s').using(prune_empty=False)

    _assert_multivalue_set_flat(schema, pairs)


def test_multivalue_set_flat_like_named():
    pairs = [('s_s', 'abc'), ('s_s', 'def')]
    bogus = [('s', 'xxx')]
    schema = MultiValue.named('s').of(String.named('s'))

    _assert_multivalue_set_flat(schema, pairs, bogus)


def test_multivalue_set_flat_unnamed_child():
    pairs = [('s', 'abc'), ('s', 'def')]
    bogus = [('', 'xxx')]
    schema = MultiValue.named('s').of(String)

    _assert_multivalue_set_flat(schema, pairs, bogus)


def test_multivalue_set_flat_anonymous_array():
    schema = MultiValue.of(String.named('s'))
    pairs = [('s', 'abc'), ('s', 'def')]
    bogus = [('', 'xxx')]

    _assert_multivalue_set_flat(schema, pairs, bogus)


def test_multivalue_set_flat_fully_anonymous_array():
    schema = MultiValue.of(String)
    pairs = [('', 'abc'), ('', 'def')]

    _assert_multivalue_set_flat(schema, pairs)


def test_multivalue_roundtrip():
    schema = MultiValue.of(String.named('s'))
    data = ['abc', 'def']
    el = schema(data)
    eq_([e.value for e in el], data)

    flat = el.flatten()
    eq_(flat, [('s', 'abc'), ('s', 'def')])
    restored = schema.from_flat(flat)
    eq_(restored.value, 'abc')
    eq_([e.value for e in restored], data)
