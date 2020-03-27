import os

__TWCC_CLI_MAJOR__ = "0"
__TWCC_CLI_MINOR__ = "5"
__TWCC_CLI_BATCH__ = "3"
if "CI_COMMIT_REF_NAME" in os.environ and os.environ['CI_COMMIT_REF_NAME']=='master':
    __version__ = "{}.{}.{}.{}".format(
        __TWCC_CLI_MAJOR__, __TWCC_CLI_MINOR__, __TWCC_CLI_BATCH__, __TWCC_CLI_STAGE__)
else:
    __version__ = "{}.{}.{}".format(
        __TWCC_CLI_MAJOR__, __TWCC_CLI_MINOR__, __TWCC_CLI_BATCH__)
