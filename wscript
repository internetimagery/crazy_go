from waflib.Logs import info

def options(opt):
    pass


def configure(conf):
    conf.find_program("npm")


def build(bld):

    bld(
        features="subst",
        source="package.json",
        target="package.json",
        is_copy=True,
    )
    bld(
        "nodejs",
        rule="${NPM} install --no-fund --no-audit --include=dev ",
        source="package.json",
        target="node_modules",
    )
    bld(
        "bundle",
        rule="npm exec webpack build -- --entry ${SRC[1]} --config ${SRC[0]} --stats-error-details -o . --output-filename ${TGT} --mode development",
        source=["webpack.config.js", "js/main.js", "style/main.css"],
        target="bundle/dist.js",
    )
    bld(
        features="subst",
        source="index.html",
        target="bundle/index.html",
        is_copy=True,
    )
    bld(
        features="subst",
        source="img/icon.ico",
        target="bundle/icon.ico",
        is_copy=True,
    )

