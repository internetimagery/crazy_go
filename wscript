from waflib.Logs import info

def options(opt):
    pass


def configure(conf):
    conf.find_program("npm")


def build(bld):
    bld(
        "Installing NodeJS Modules",
        rule="${NPM} install -g --prefix ${TGT} ..",
        source="package.json",
        target="vendor_nodejs",
    )
