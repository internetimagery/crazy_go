from waflib.Logs import info

def options(opt):
    pass


def configure(conf):
    conf.find_program("npm")


def build(bld):
    bld(
        "nodejs",
        rule="cp ${SRC} . && ${NPM} install --include=dev ",
        source="package.json",
    )

    bld(
        "Bundle",
        rule="npx webpack --entry ${SRC} -o . --output-filename ${TGT} --mode production",
        source="js/adjustments.js",
        target="bundle/dist.js",
        depends_on="nodejs",
    )
