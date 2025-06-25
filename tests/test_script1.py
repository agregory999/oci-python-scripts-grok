import argparse

import pytest

from oci_python_scripts_grok.scripts.script1 import UpperCaseProcessor


@pytest.fixture
def processor(mocker):
    """Create a processor with mocked OCI connection and argparse."""
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            input='test',
            font_size=12,
            verbose=False,
            config_file='~/.oci/config',
            profile='DEFAULT',
        ),
    )
    processor = UpperCaseProcessor()
    mocker.patch.object(processor, 'connect_to_oci', return_value=True)
    return processor


def test_uppercase_processor(processor):
    """Test uppercase processing."""
    assert processor.process('hello') == 'HELLO'


def test_oci_connection(processor, mocker):
    """Test OCI connection success."""
    assert processor.connect_to_oci() is True
    processor.connect_to_oci.assert_called_once()


def test_validation(processor):
    """Test input validation."""
    assert processor.validate('test') is True
    assert processor.validate('') is False
    with pytest.raises(ValueError):
        processor.process('')


def test_run(processor, capsys):
    """Test run method outputs to console."""
    processor.run()
    captured = capsys.readouterr()
    assert captured.out.strip() == 'Result: TEST'
