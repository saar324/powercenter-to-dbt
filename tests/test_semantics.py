from datetime import datetime
from decimal import Decimal as D

import duckdb
import pytest

from pwc_to_dbt.expressions import Expr, convert, parse, translate
from pwc_to_dbt.mapping import ConversionError, DataType, Port


def output(name='value', datatype='decimal', precision=12, scale=2, default='NULL'):
    return Port(name, DataType(datatype, precision, scale), 'OUTPUT', default=default)


@pytest.mark.boundary
@pytest.mark.parametrize('expression,expected', [
    ('IIF(NULL = 1, 1, 0)', 0), ('IIF(ISNULL(NULL), 7, 2)', 7),
    ('1 + 2 * 3', 7), ('(1 + 2) * 3', 9), ("IIF('it''s' = 'it''s', -1, 0)", -1),
    ("IIF(NULL = 'Y' OR NULL = '1', 1, 0)", 0),
    ("UPPER(LTRIM(RTRIM(' jaffle ')))", 'JAFFLE'),
])
def test_structural_expression_results(expression, expected):
    sql = translate(expression, {})
    with duckdb.connect() as db:
        assert db.execute('SELECT ' + sql).fetchone() == (expected,)


@pytest.mark.negative
@pytest.mark.parametrize('expression', ['FOO(1)', 'IIF(1, 2)', "x; DROP TABLE a", 'missing + 1', 'COUNT(x)', 'a || b', 'IIF(1=1, 1, )'])
def test_unknown_expressions_are_rejected(expression):
    with pytest.raises(ConversionError):
        translate(expression, {'x': '1'})


@pytest.mark.boundary
@pytest.mark.parametrize('value,context,expected', [
    ('1998-01-02 17:45:46', '2003-01-01', datetime(2098, 1, 2)),
    ('1998-01-02 17:45:46', '1999-01-01', datetime(1998, 1, 2)),
    ('1998-01-02 17:45:46', '2100-01-01', datetime(2198, 1, 2)),
    ('2000-02-29 22:15:01', '2099-12-31', datetime(2000, 2, 29)),
    ('2000-02-29 22:15:01', '2100-01-01', None),
    (None, '2026-01-01', None),
])
def test_current_century_midnight_leap_day_and_null_default(value, context, expected):
    expression = translate("TO_DATE(TO_CHAR(ORDERED_AT, 'DD-MM-YY'), 'DD-MM-YY')", {'ORDERED_AT': 'stamp'}, runtime_date=f"DATE '{context}'")
    converted = convert(expression, output(datatype='date/time', precision=29, scale=9), output_default=True)
    with duckdb.connect() as db:
        assert db.execute(f'SELECT {converted} FROM (SELECT CAST(? AS TIMESTAMP) AS stamp)', [value]).fetchone() == (expected,)


@pytest.mark.boundary
def test_production_dates_use_runtime_clock():
    sql = translate("TO_DATE(TO_CHAR(stamp, 'DD-MM-YY'), 'DD-MM-YY')", {'stamp': 'stamp'})
    assert 'CURRENT_DATE' in sql
    assert '2026' not in sql


@pytest.mark.boundary
@pytest.mark.parametrize('datatype', ['decimal', 'double', 'number'])
@pytest.mark.parametrize('default,expected', [('NULL', None), ('0', D('0.00'))])
def test_error_defaults_do_not_replace_legitimate_null(default, expected, datatype):
    port = output(default=default, datatype=datatype)
    division = translate('x / y', {'x': 'x', 'y': 'y'})
    sql = convert(division, port, output_default=True)
    with duckdb.connect() as db:
        assert db.execute(f'SELECT {sql} FROM (VALUES (NULL,1),(1,0),(2,1)) t(x,y)').fetchall() == [(None,), (expected,), (D('2.00'),)]


@pytest.mark.boundary
def test_error_default_fails_visibly():
    port = output(default="ERROR('transformation error')")
    sql = convert(translate('1 / zero', {'zero': 'zero'}), port, output_default=True)
    with duckdb.connect() as db:
        with pytest.raises(duckdb.Error, match='division by zero'):
            db.execute(f'SELECT {sql} FROM (VALUES (0)) t(zero)').fetchall()


@pytest.mark.boundary
@pytest.mark.parametrize('text,source,expected', [('', True, None), ('', False, ''), ('   ', True, '   '), (None, True, None)])
def test_oracle_storage_and_intermediate_empty_strings(text, source, expected):
    sql = convert('x', output(datatype='string', precision=20, scale=0), oracle_storage=source)
    with duckdb.connect() as db:
        assert db.execute(f'SELECT {sql} FROM (SELECT ?::VARCHAR AS x)', [text]).fetchone() == (expected,)


@pytest.mark.boundary
def test_trim_empty_survives_intermediate_but_target_normalizes():
    value = translate("LTRIM(RTRIM(x))", {'x': 'x'})
    intermediate = convert(value, output(datatype='string', precision=20, scale=0))
    target = convert('intermediate', output(datatype='varchar2', precision=20, scale=0), oracle_storage=True)
    with duckdb.connect() as db:
        assert db.execute(f"SELECT intermediate, {target} FROM (SELECT {intermediate} AS intermediate FROM (VALUES ('   ')) t(x))").fetchone() == ('', None)


@pytest.mark.boundary
@pytest.mark.parametrize('value,expected', [('0.005', D('0.01')), ('-0.005', D('-0.01')), ('9.994', D('9.99')), ('9.995', None), (None, None)])
def test_declared_decimal_rounding_and_precision_limit(value, expected):
    sql = convert('x', output(precision=3, scale=2), output_default=True)
    with duckdb.connect() as db:
        assert db.execute(f'SELECT {sql} FROM (SELECT ?::DECIMAL(8,4) AS x)', [value]).fetchone() == (expected,)


@pytest.mark.boundary
def test_double_scale_zero_keeps_fraction_and_decimal_cents_rounds_separately():
    double = convert('x', output(datatype='double', precision=15, scale=0))
    cents = convert('x', output(precision=12, scale=0))
    with duckdb.connect() as db:
        assert db.execute(f'SELECT {double}, {cents} FROM (VALUES (1.5),(-1.5)) t(x)').fetchall() == [(1.5, D('2')), (-1.5, D('-2'))]


@pytest.mark.boundary
@pytest.mark.parametrize('value', [float('inf'), float('-inf'), float('nan')])
def test_nonfinite_numbers_fail_visibly_at_storage(value):
    sql = convert('x', output(datatype='number', precision=15, scale=0), oracle_storage=True)
    with duckdb.connect() as db:
        with pytest.raises(duckdb.Error, match='nonfinite numeric'):
            db.execute(f'SELECT {sql} FROM (SELECT ?::DOUBLE AS x)', [value]).fetchall()


@pytest.mark.boundary
def test_output_string_error_default_preserves_null_and_handles_overlength():
    sql = convert('x', output(datatype='string', precision=3, scale=0), output_default=True)
    with duckdb.connect() as db:
        assert db.execute(f"SELECT {sql} FROM (VALUES ('abc'),('abcd'),(NULL),('')) t(x)").fetchall() == [('abc',), (None,), (None,), ('',)]


@pytest.mark.negative
@pytest.mark.parametrize('datatype', ['binary', 'xml', 'unknown'])
def test_unsupported_types_do_not_emit(datatype):
    with pytest.raises(ConversionError, match='Unsupported datatype'):
        convert('x', output(datatype=datatype))


@pytest.mark.negative
@pytest.mark.parametrize('text', ["'{{ run_query(\"select 1\") }}'", "'{% for x in y %}'", "'{# hidden #}'"])
def test_imported_literals_cannot_inject_dbt_templates(text):
    with pytest.raises(ConversionError, match='template delimiters'):
        translate(text, {})


@pytest.mark.boundary
@pytest.mark.parametrize('datatype,lower,upper,duck_type', [
    ('small integer', -32768, 32767, 'SMALLINT'),
    ('integer', -2147483648, 2147483647, 'INTEGER'),
    ('bigint', -9223372036854775808, 9223372036854775807, 'BIGINT'),
])
@pytest.mark.parametrize('default', ['NULL', '0', "ERROR('transformation error')"])
def test_integer_ranges_and_output_error_defaults(datatype, lower, upper, duck_type, default):
    port = output(datatype=datatype, precision=19, scale=0, default=default)
    sql = convert('x', port, output_default=True)
    with duckdb.connect() as db:
        cursor = db.execute(f'SELECT {sql} FROM (SELECT ?::DECIMAL(38,0) x UNION ALL SELECT ?::DECIMAL(38,0) UNION ALL SELECT NULL)', [str(lower), str(upper)])
        assert str(cursor.description[0][1]) == duck_type
        assert cursor.fetchall() == [(lower,), (upper,), (None,)]
        for invalid in (lower - 1, upper + 1):
            if default.startswith('ERROR'):
                with pytest.raises(duckdb.Error):
                    db.execute(f'SELECT {sql} FROM (SELECT ?::DECIMAL(38,0) x)', [str(invalid)]).fetchall()
            else:
                expected = None if default == 'NULL' else 0
                assert db.execute(f'SELECT {sql} FROM (SELECT ?::DECIMAL(38,0) x)', [str(invalid)]).fetchone() == (expected,)
        strict = convert('x', port)
        with pytest.raises(duckdb.Error):
            db.execute(f'SELECT {strict} FROM (SELECT ?::DECIMAL(38,0) x)', [str(upper + 1)]).fetchall()


@pytest.mark.negative
@pytest.mark.parametrize('expression', ['UPPER(' * 2000 + "'x'" + ')' * 2000, '+'.join(['1'] * 2000)])
def test_expression_complexity_is_a_conversion_error(expression):
    with pytest.raises(ConversionError, match='complexity'):
        translate(expression, {})


@pytest.mark.boundary
@pytest.mark.parametrize('datatype', ['decimal', 'double', 'number'])
@pytest.mark.parametrize('default', ['NULL', '0', "ERROR('transformation error')"])
def test_division_propagates_operand_null_before_zero_error(datatype, default):
    port = output(datatype=datatype, default=default)
    sql = convert(translate('x / y', {'x': 'x', 'y': 'y'}), port, output_default=True)
    with duckdb.connect() as db:
        # NULL/0 is legitimate NULL arithmetic, independently of the output's
        # error default. Either null operand propagates; ordinary division stays.
        rows = db.execute(f'SELECT {sql} FROM (VALUES (NULL::DOUBLE,0::DOUBLE),(NULL,1),(2,NULL),(NULL,NULL),(2,1),(0,2),(5,2)) t(x,y)').fetchall()
        assert rows == [(None,), (None,), (None,), (None,), (D('2.00'),), (D('0.00'),), (D('2.50'),)]
        # A non-null numerator with a zero denominator remains an error/default.
        zero_query = f'SELECT {sql} FROM (VALUES (1::DOUBLE,0::DOUBLE)) t(x,y)'
        if default.startswith('ERROR'):
            with pytest.raises(duckdb.Error, match='division by zero'):
                db.execute(zero_query).fetchall()
        else:
            expected = None if default == 'NULL' else 0
            assert db.execute(zero_query).fetchone() == (expected,)
