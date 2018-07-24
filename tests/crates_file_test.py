import pytest
import yaml

from hipaacrates import crate

def test_crate_creation_minimal():
    name = "mycrate"
    version = "0.0.1"

    actual = crate.new(name=name, version=version)
    assert isinstance(actual, crate.Crate)
    
    assert actual.name == name
    assert actual.version == version
    assert actual.bundles == []
    assert actual.author == ""

def test_crate_creation_with_bundles():
    name = "mycrate"
    version = "0.0.1"
    bundles = ["mybundle", "foobundle"]

    actual = crate.new(name=name, version=version, bundles=bundles)
    assert isinstance(actual, crate.Crate)

    assert actual.name == name
    assert actual.version == version
    assert actual.bundles == bundles
    assert actual.author == ""

def test_crate_creation_with_author():
    name = "mycrate"
    version = "0.0.1"
    author = "me"

    actual = crate.new(name=name, version=version, author=author)
    assert isinstance(actual, crate.Crate)

    assert actual.name == name
    assert actual.version == version
    assert actual.bundles == []
    assert actual.author == author

def test_crate_to_yaml():
    name = "mycrate"
    version = "0.0.1"
    author = "me"
    bundles = ["mybundle", "foobundle"]

    c = crate.new(name=name, version=version, author=author, bundles=bundles)
    actual = c.to_yaml()

    items = [s.strip() for s in actual.splitlines()]
    assert "name: {}".format(name) in items
    assert "version: {}".format(version) in items
    assert "author: {}".format(author) in items
    assert "bundles:" in items
    assert "- mybundle" in items
    assert "- foobundle" in items

@pytest.fixture
def cratetext():
    return """
    name: mycrate
    version: 0.0.1
    author: me
    bundles:
        - mybundle
        - foobundle
    """

def test_crate_parse(cratetext):
    c = crate.parse(cratetext)
    assert isinstance(c, crate.Crate)

    assert c.name == "mycrate"
    assert c.version == "0.0.1"
    assert c.author == "me"
    assert c.bundles == ["mybundle", "foobundle"]

def test_read_yaml(tmpdir, cratetext):
    p = tmpdir.join("example.yaml")
    p.write(cratetext)

    c = crate.read_yaml(str(p))
    assert c.name == "mycrate"
    assert c.version == "0.0.1"
    assert c.author == "me"
    assert c.bundles == ["mybundle", "foobundle"]
