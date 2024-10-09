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

    # Compile python
    #bld(
    #    name="compile_python",
    #    rule="${PYTHON3} -m transcrypt --map --nomin --outdir ${TGT[0].abspath()} ${SRC}",
    #    source="py/main.py",
    #    target="compiled_python",
    #    after="install_python",
    #)

    # Bundle javascript and css
    bld(
        name="webpack_bundle",
        rule="npm exec webpack build -- --entry ${SRC[1]} --config ${SRC[0]} --stats-error-details -o . --output-filename ${TGT} --mode development",
        source=["webpack.config.js", "py/main.py", "css/main.css"],
        target="bundle/dist.js",
        after=["install_node"],
        #after=["install_node", "compile_python"],
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

