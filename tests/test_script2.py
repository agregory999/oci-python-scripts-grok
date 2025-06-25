import argparse

import pytest

from oci_python_scripts_grok.scripts.script2 import ReverseProcessor


@pytest.fixture
def processor(mocker):
    """Create a processor with mocked OCI connection and argparse."""
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            input='test',
            bg_color='white',
            verbose=False,
            config_file='~/.oci/config',
            profile='NACEOCI01',
        ),
    )
    processor = ReverseProcessor()
    mocker.patch.object(processor, 'connect_to_oci', return_value=True)
    return processor


def test_reverse_processor(processor):
    """Test reverse processing."""
    assert processor.process('hello') == 'olleh'


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


def test_tksheet_initialization(processor):
    """Test tksheet and Tkinter components."""
    assert processor.root.title() == 'Reverse Processor'
    assert processor.label.cget('text') == 'Enter text:'
    assert processor.sheet.get_sheet_data() == [['test', '']]  # Initial data
    assert processor.args.bg_color == 'white'


def test_process_and_display(processor):
    """Test processing and updating tksheet."""
    processor._process_and_display()
    assert processor.sheet.get_sheet_data() == [['test', 'tset']]
