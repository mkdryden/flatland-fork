# -*- coding: utf-8 -*-
from flatland import String
from flatland.out.markup import Generator

from tests.markup._util import markup_test


schema = String.named('field1').using(default='val').from_defaults


@markup_test('html', schema)
def test_input_html(gen, el):
    """<input type="text" name="field1" value="val">"""
    return gen.input(type='text', bind=el)


@markup_test('xml', schema)
def test_input_xml(gen, el):
    """<input type="text" name="field1" value="val" />"""
    return gen.input(type='text', bind=el)


@markup_test('xml', schema)
def test_input_open(gen, el):
    """<input type="text" name="field1" value="val">"""
    return gen.input.open(type='text', bind=el)


def test_detached_reuse():
    gen = Generator('xml')
    el = schema()

    tag = gen.textarea
    output_a = tag.open(el)
    contents = tag.contents
    output_b = tag.open(el)

    assert contents == tag.contents
    assert output_a == output_b

    assert gen.textarea is tag
    assert gen.textarea.contents == contents
    tag.close()
    assert gen.textarea is not tag
    assert gen.textarea.contents != contents
    tag.close()
    tag.close()


@markup_test('xml', schema)
def test_input_close(gen, el):
    """</input>"""
    return gen.input.close()


@markup_test('xml', schema)
def test_textarea_escaped(gen, el):
    '''<textarea name="field1">"&lt;quoted &amp; escaped&gt;"</textarea>'''
    bind = el
    bind.set('"<quoted & escaped>"')
    return gen.textarea(bind)


@markup_test('xml', schema)
def test_textarea_contents(gen, el):
    """val"""
    gen.textarea.open(el)
    return gen.textarea.contents


@markup_test('xml', schema)
def test_textarea_escaped_contents(gen, el):
    '''"&lt;quoted &amp; escaped&gt;"'''
    bind = el
    bind.set('"<quoted & escaped>"')
    gen.textarea.open(bind)
    return gen.textarea.contents


@markup_test('xml', schema)
def test_textarea_explicit_contents(gen, el):
    """xyzzy"""
    gen.textarea.open(el, contents='xyzzy')
    return gen.textarea.contents


def test_Markup_concatenation():
    from flatland.out.generic import Markup as Markup
    implementations = [Markup]
    try:
        from jinja2 import Markup
        implementations.append(Markup)
    except ImportError:
        pass
    try:
        from markupsafe import Markup
        implementations.append(Markup)
    except ImportError:
        pass

    for impl in implementations:
        yield _generate_markup_test(impl), impl.__module__ + '.Markup'


def _generate_markup_test(impl):
    def test(gen, el):
        """<label><x></label>"""
        gen['markup_wrapper'] = impl
        return gen.label(contents=impl('<x>'))

    wrapper = lambda label: markup_test('xml', schema)(test)()
    return wrapper
