from twcc import _TWCC_SESSION_, Session2
import pytest
from click.testing import CliRunner

def test_init_twcc_session():
    import shutil
    import os
    shutil.rmtree( os.path.dirname(Session2._getSessionFile()) )
    assert Session2._getApiKey() == os.environ.get('TWCC_API_KEY')

    mySession = Session2()
    assert mySession.getApiKey() == Session2._getApiKey()

#def test_list_cntr():
#    print(_TWCC_SESSION_)
#    mySession = Session2()
#    runner = CliRunner()
#    result = runner.invoke(cli, ['ls', '-c'])
#    print (">"*10, result.output)
#    print (">"*10, result.exception)
#    assert result.exit_code == 0


#def test_list_cos():
#    from examples.twccli import cli
#
#    runner = CliRunner()
#    result = runner.invoke(cli, ['ls', '-o'])
#    print (">"*10, result)
#    assert result.exit_code == 0

