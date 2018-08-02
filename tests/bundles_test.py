import os

import pytest
import requests
import responses

from hipaacrates import bundles, crate

HERE = os.path.abspath(os.path.dirname(__file__))

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

def test_fs_bundle_loader():
    fs_loader = bundles.FSBundleLoader(os.path.join(HERE, "fixtures"))
    c = fs_loader.load("foo")
    assert c.name == "foo"
    assert c.version == "0.0.1"
    assert c.author == "me"
    assert c.includes == ["myapp/"]
    assert c.build_steps == ["make", "make install"]
    assert c.bundles == ["bar", "baz"]

def test_fs_bundle_loader_no_file():
    fs_loader = bundles.FSBundleLoader(os.path.join(HERE, "fixtures"))
    with pytest.raises(FileNotFoundError):
        fs_loader.load("nonexistant.bundle")

@responses.activate
def test_http_bundle_loader(crate_obj):
    host = "http://github.com/hipaapotamus/hipaadrome"
    responses.add(responses.GET, "{}/bundles/{}".format(host, crate_obj.name), body=crate_obj.to_yaml())

    http_loader = bundles.HTTPBundleLoader(host)
    c = http_loader.load(crate_obj.name)
    assert c == crate_obj

@responses.activate
def test_http_bundle_loader_404(crate_obj):
    host = "http://github.com/hipaapotamus/hipaadrome"
    responses.add(responses.GET, "{}/bundles/{}".format(host, crate_obj.name),
                  body="Not Found", status=404)

    http_loader = bundles.HTTPBundleLoader(host)
    with pytest.raises(requests.exceptions.HTTPError):
        http_loader.load(crate_obj.name)

@responses.activate
def test_caching_bundle_loader_on_disk():
    host = "http://github.com/hipaapotamus/hipaadrome"

    loader = bundles.CachingBundleLoader(host, cache_dir=os.path.join(HERE, "fixtures"))
    c = loader.load("foo")
    assert c.name == "foo"
    assert c.version == "0.0.1"
    assert c.author == "me"
    assert c.includes == ["myapp/"]
    assert c.build_steps == ["make", "make install"]
    assert c.bundles == ["bar", "baz"]

@responses.activate
def test_caching_bundle_loader_miss(crate_obj):
    host = "http://github.com/hipaapotamus/hipaadrome"
    responses.add(responses.GET, "{}/bundles/{}".format(host, crate_obj.name), body=crate_obj.to_yaml())

    loader = bundles.CachingBundleLoader(host, cache_dir=os.path.join(HERE, "fixtures"))
    c = loader.load(crate_obj.name)
    try:
        assert c == crate_obj
        assert os.path.isfile(os.path.join(HERE, "fixtures", crate_obj.name))
    finally:
        os.remove(os.path.join(HERE, "fixtures", crate_obj.name))
    

@responses.activate
def test_caching_bundle_loader_404(crate_obj):
    host = "http://github.com/hipaapotamus/hipaadrome"
    responses.add(responses.GET, "{}/bundles/{}".format(host, crate_obj.name), body="Not Found", status=404)

    loader = bundles.CachingBundleLoader(host, cache_dir=os.path.join(HERE, "fixtures"))
    with pytest.raises(requests.exceptions.HTTPError):
        loader.load(crate_obj.name)
