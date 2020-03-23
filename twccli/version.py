__TWCC_CLI_MAJOR__ = "0"
__TWCC_CLI_MINOR__ = "5"
__TWCC_CLI_BATCH__ = "3"
__TWCC_CLI_STAGE__ = "a"
if len(__TWCC_CLI_STAGE__)==0:
    __version__ = "{}.{}.{}".format(
        __TWCC_CLI_MAJOR__, __TWCC_CLI_MINOR__, __TWCC_CLI_BATCH__)
else:
    __version__ = "{}.{}.{}.{}".format(
        __TWCC_CLI_MAJOR__, __TWCC_CLI_MINOR__, __TWCC_CLI_BATCH__, __TWCC_CLI_STAGE__)
