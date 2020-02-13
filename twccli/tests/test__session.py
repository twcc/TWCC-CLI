from twcc import Session2
import pytest

@pytest.mark.first
def test_init_twcc_session():
    import shutil
    import os
    shutil.rmtree( os.path.dirname(Session2._getSessionFile()) )
    assert Session2._getApiKey() == os.environ.get('TWCC_API_KEY')

    mySession = Session2()
    assert mySession.getApiKey() == Session2._getApiKey()

