import os

def options(opt):
    pass


def configure(conf):

    conf.find_program("pip")
    conf.find_program("python3")
    conf.find_program("npm")

    conf.env.env = {
        "PYTHONPATH": os.pathsep.join(("python_modules", "node_modules")),
        "PATH": os.pathsep.join(("python_modules/bin", os.environ["PATH"])),
    }


def build(bld):
    # Install Python modules
    bld(
        name="install_python",
        rule="${PIP} install --target python_modules -r ${SRC}",
        source="requirements.txt",
    )

    # Install Node modules
    bld(
        name="copy_package",
        features="subst",
        source="package.json",
        target="package.json",
        is_copy=True,
    )
    bld(
        name="install_node",
        rule="${NPM} install --no-fund --no-audit --include=dev ",
        source="package.json",
        after="copy_package",
    )

    # Bundle javascript and css
    bld(
        name="webpack_bundle",
        rule="npm exec webpack build -- --entry ${SRC[-1]} --config ${SRC[-2]} --stats-error-details -o . --output-filename ${TGT} --mode development",
        source=bld.path.ant_glob("py/*.py") + bld.path.ant_glob("css/*.css") + ["webpack.config.js", "py/main.py"],
        target="bundle/dist.js",
        after=["install_node"],
    )

    # Copy across static files
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

