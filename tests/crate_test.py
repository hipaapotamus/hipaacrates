import pytest
import yaml

from hipaacrates import crate

def test_crate_creation_minimal():
    name = "mycrate"
    version = "0.0.1"

    actual = crate.new(name, version)
    assert isinstance(actual, crate.Crate)
    
    assert actual.name == name
    assert actual.version == version
    assert actual.author == ""
    assert actual.build_steps == []
    assert actual.bundles == []
    assert actual.includes == []
    assert actual.run_command == ""

def test_crate_creation_with_bundles():
    name = "mycrate"
    version = "0.0.1"
    bundles = ["mybundle", "foobundle"]

    actual = crate.new(name, version, bundles=bundles)
    assert isinstance(actual, crate.Crate)

    assert actual.bundles == bundles
    assert actual.name == name
    assert actual.version == version
    assert actual.author == ""
    assert actual.build_steps == []
    assert actual.includes == []
    assert actual.run_command == ""

def test_crate_creation_with_author():
    name = "mycrate"
    version = "0.0.1"
    author = "me"

    actual = crate.new(name, version, author=author)
    assert isinstance(actual, crate.Crate)

    assert actual.author == author
    assert actual.name == name
    assert actual.version == version
    assert actual.build_steps == []
    assert actual.bundles == []
    assert actual.includes == []
    assert actual.run_command == ""

def test_crate_creation_with_build_steps():
    name = "mycrate"
    version = "0.0.1"
    build_steps = [
        "apt install python"
        "apt install foo"
    ]

    actual = crate.new(name, version, build_steps=build_steps)

    assert actual.build_steps == build_steps
    assert actual.name == name
    assert actual.version == version
    assert actual.author == ""
    assert actual.bundles == []
    assert actual.includes == []
    assert actual.run_command == ""

def test_crate_creation_with_includes():
    name = "mycrate"
    version = "0.0.1"
    includes = [
        "src/",
        "tests/"
    ]

    actual = crate.new(name, version, includes=includes)

    assert actual.includes == includes
    assert actual.name == name
    assert actual.version == version
    assert actual.author == ""
    assert actual.build_steps == []
    assert actual.bundles == []
    assert actual.run_command == ""

def test_crate_creation_with_run_command():
    name = "mycrate"
    version = "0.0.1"
    run_command = "/bin/sh"

    actual = crate.new(name, version, run_command=run_command)

    assert actual.name == name
    assert actual.run_command == run_command
    assert actual.version == version
    assert actual.author == ""
    assert actual.build_steps == []
    assert actual.bundles == []
    assert actual.includes == []

def test_crate_to_yaml():
    name = "mycrate"
    version = "0.0.1"
    author = "me"
    build_steps = ["apt install foo", "apt install bar"]
    bundles = ["mybundle", "foobundle"]
    includes = ["src/", "tests/"]
    run_command = "/bin/sh"

    c = crate.new(name, version, author=author, build_steps=build_steps, bundles=bundles,
                  includes=includes, run_command=run_command)
    actual = c.to_yaml()

    items = [s.strip() for s in actual.splitlines()]
    assert "name: {}".format(name) in items
    assert "version: {}".format(version) in items
    assert "author: {}".format(author) in items
    assert "build_steps:" in items
    assert "- apt install foo" in items
    assert "- apt install bar" in items
    assert "bundles:" in items
    assert "- mybundle" in items
    assert "- foobundle" in items
    assert "includes:" in items
    assert "- src/" in items
    assert "- tests/" in items
    assert "run_command: {}".format(run_command) in items

@pytest.fixture
def cratetext():
    return """
    name: mycrate
    version: 0.0.1
    author: me
    build_steps:
        - |
            apt install foo \\
            && rm -rf hmm
        - apt install hi
    bundles:
        - mybundle
        - foobundle
    includes:
        - src/
        - tests/
    run_command: /bin/sh
    """

def test_crate_parse(cratetext):
    c = crate.parse(cratetext)
    assert isinstance(c, crate.Crate)

    assert c.name == "mycrate"
    assert c.version == "0.0.1"
    assert c.author == "me"
    assert c.build_steps == ["apt install foo \\\n&& rm -rf hmm\n", "apt install hi"]
    assert c.bundles == ["mybundle", "foobundle"]
    assert c.includes == ["src/", "tests/"]
    assert c.run_command == "/bin/sh"

def test_read_yaml(tmpdir, cratetext):
    p = tmpdir.join("example.yaml")
    p.write(cratetext)

    c = crate.read_yaml(str(p))
    assert c.name == "mycrate"
    assert c.version == "0.0.1"
    assert c.author == "me"
    assert c.build_steps == ["apt install foo \\\n&& rm -rf hmm\n", "apt install hi"]
    assert c.bundles == ["mybundle", "foobundle"]
    assert c.includes == ["src/", "tests/"]
    assert c.run_command == "/bin/sh"
