from waflib.Logs import info

def options(opt):
    pass


def configure(conf):
    conf.find_program("npm")


def _cp(bld, name):
    return bld(
        features="subst",
        source=name,
        target=name,
        is_copy=True,
    )


def build(bld):

    _cp(bld, "package.json"),
    bld(
        "nodejs",
        rule="${NPM} install --no-fund --no-audit --include=dev ",
        source="package.json",
        target="node_modules",
    )
    # node_modules added as dependency to force packs to build first
    bld(
        "bundle",
        rule="npm exec webpack build -- --entry ${SRC[2]} --config ${SRC[1]} --stats-error-details -o . --output-filename ${TGT} --mode production",
        source=["node_modules", "webpack.config.js", "js/main.js"],
        target="bundle/dist.js",
    )

