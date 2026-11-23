from importlib.metadata import version

import pii_scan_br


def test_versao_do_pacote_igual_ao_metadata():
    assert pii_scan_br.__version__ == version("pii-scan-br")
