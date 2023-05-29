from varstore import storage

class TestStorage:
    def test_create_storage(self):
        store = storage.Storage()

    def test_get_variable(self):
        store = storage.Storage()
        var = store.get_variable("foo")
        assert var.name == "foo"

    def test_get_variable_with_subpath(self):
        store = storage.Storage()
        var = store.get_variable("foo.bar")
        assert var.name == "bar"
        var.value = 2
        var = store.get_variable("foo.baz")
        assert var.name == "baz"
        var.value = 3
        var = store.get_variable("foo.bar")
        assert var.value == 2
        var = store.get_variable("foo.baz")
        assert var.value == 3
        
        #assert store.get_path(var) == "foo.bar"
