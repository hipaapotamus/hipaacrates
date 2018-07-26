import pytest

from hipaacrates import crate, dockerfile

@pytest.fixture
def crate_obj():
    return crate.new(
        "mycrate",
        "0.0.1",
        author="me",
        build_steps=[
            "make",
            "make install",
        ],
        bundles=["python"],
        includes=["myapp/", "tests/"],
        run_command="/bin/sh",
    )

def test_make_dockerfile_header(crate_obj):
    header = dockerfile.make_header(crate_obj)

    assert header == "FROM {}\nLABEL maintainer \"{}\"\nLABEL version \"{}\"\nWORKDIR {}".format(
        dockerfile.DEFAULT_BASE_IMAGE, crate_obj.author,
        crate_obj.version, "/opt/services/{}".format(crate_obj.name)
    )

def test_make_run_statement(crate_obj):
    for step in crate_obj.build_steps:
        statement = dockerfile.make_run_statement(step)
        assert statement == "RUN {}".format(step)

def test_make_run_statement_empty_string():
    assert dockerfile.make_run_statement("") == ""

def test_convert_build_steps(crate_obj):
    steps = dockerfile.convert_build_steps(crate_obj)
    assert steps == "RUN {}\nRUN {}".format(
        crate_obj.build_steps[0], crate_obj.build_steps[1]
    )

def test_copy_statement(crate_obj):
    dest = "/opt/services/{}/".format(crate_obj.name)
    for include in crate_obj.includes:
        statement = dockerfile.make_copy_statement(include, dest)
        assert statement == "COPY {} {}".format(include, dest)

def test_include_files(crate_obj):
    dest = "/opt/services/{}/".format(crate_obj.name)
    statement = dockerfile.include_files(crate_obj)
    assert statement == "COPY {} {} {}".format(
        crate_obj.includes[0], crate_obj.includes[1], dest,
    )

def test_empty_includes(crate_obj):
    crate_obj.includes = []
    statement = dockerfile.include_files(crate_obj)
    assert statement == ""

def test_make_service_definition(crate_obj):
    definition = dockerfile.make_service_definition(crate_obj)
    assert definition == "COPY .hipaacrates/{}.sh /etc/service/{}/run\nRUN chmod a+x /etc/service/{}/run".format(
        crate_obj.name, crate_obj.name, crate_obj.name,
    )

def test_make_service_definition_no_run_command(crate_obj):
    crate_obj.run_command = ""
    assert dockerfile.make_service_definition(crate_obj) == ""
