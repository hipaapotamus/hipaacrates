import pytest

from hipaacrates import crate, services

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

def test_make_scripts(crate_obj):
    scripts = services.make_scripts(crate_obj)

    assert crate_obj.name in scripts
    assert scripts[crate_obj.name] == "#!/bin/sh\n\n{}".format(crate_obj.run_command)

def test_make_scripts_empty_run_command(crate_obj):
    crate_obj.run_command = ""
    
    scripts = services.make_scripts(crate_obj)
    assert crate_obj.name not in scripts
