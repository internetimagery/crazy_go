from waflib.Logs import info

def options(opt):
    pass


def configure(conf):
    conf.find_program("npm")
    modules = conf.bldnode.make_node("node_modules")
    conf.env.NODE_PATH = modules.abspath()


def _cp(bld, name):
    return bld(
        features="subst",
        source=name,
        target=name,
        is_copy=True,
    )


def build(bld):

#    tasks = [
#        _cp(bld, node)
#        for node in bld.srcnode.ant_glob("js/*.js")
#    ]
    bld(
        "nodejs",
        rule="${NPM} install --include=dev ",
        source="package.json",
        depends_on=_cp(bld, "package.json"),
    )
    bld(
        "bundle",
        rule="npx webpack --stats-error-details --entry ${SRC} -o . --output-filename ${TGT} --mode production",
        source="js/main.js",
        target="bundle/dist.js",
        depends_on="nodeks",
    )

