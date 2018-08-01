import pytest

from hipaacrates import bundles, crate

class MockBundleLoader(bundles.BundleLoader):
    def load(self, name):
        if name == "foo":
            return crate.new(
                "foo",
                "0.0.1",
                bundles=["baz"]
            )
        elif name == "bar":
            return crate.new(
                "bar",
                "0.0.1",
                bundles=[]
            )
        elif name == "baz":
            return crate.new(
                "baz",
                "0.0.1",
                bundles=[]
            )

class MockCircularBundleLoader(bundles.BundleLoader):
    def load(self, name):
        if name == "foo":
            return crate.new(
                "foo",
                "0.0.1",
                bundles=["baz"]
            )
        elif name == "bar":
            return crate.new(
                "bar",
                "0.0.1",
                bundles=[]
            )
        elif name == "baz":
            return crate.new(
                "baz",
                "0.0.1",
                bundles=["foo"]
            )

@pytest.fixture
def crate_obj():
    return crate.new(
        "mycrate",
        "0.0.1",
        bundles=[
            "foo",
            "bar",
        ]
    )

def test_load_dependencies(crate_obj):
    dependencies = bundles.load_dependencies(crate_obj, MockBundleLoader())
    assert len(dependencies) == 3

    names = [d.name for d in dependencies]
    assert "foo" in names
    assert "bar" in names
    assert "baz" in names

def test_resolve_dependencies(crate_obj):
    loader = MockBundleLoader()
    deps = [loader.load(n) for n in ["foo", "bar", "baz"]]
    deps.append(crate_obj)

    resolved = bundles.resolve_dependencies(deps)
    assert len(resolved) == 4

    assert resolved[0].name == "bar"
    assert resolved[1].name == "baz"
    assert resolved[2].name == "foo"
    assert resolved[3].name == "mycrate"

def test_resolve_dependencies_circular(crate_obj):
    loader = MockCircularBundleLoader()
    deps = [loader.load(n) for n in ["foo", "bar", "baz"]]
    deps.append(crate_obj)

    with pytest.raises(ValueError):
        bundles.resolve_dependencies(deps)
