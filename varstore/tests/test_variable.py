import pytest

from varstore import variable

class TestVariable:
    def test_set_get(self):
        var = variable.Variable("foo")
        var.value = 2
        assert var.value is 2

    def test_tostring(self):
        var = variable.Variable("foo")
        var.value = 2
        assert str(var) == "foo: 2"

    def test_subscribe(self):
        var = variable.Variable("foo")

        def handler(name, value):
            assert name is var.name
            assert value is 2

        var.subscribe(handler)
        var.value = 2

    def test_multiple_subscribtions(self):
        var = variable.Variable("foo")

        call_count = 0
        def handler(name, value):
            nonlocal call_count
            call_count += 1
            assert name is var.name
            assert value is 2

        var.subscribe(handler)
        var.subscribe(handler)
        var.value = 2
        assert call_count is 2

    def test_remove_subscription(self):
        var = variable.Variable("foo")

        has_been_called = False
        def handler(name, value):
            nonlocal has_been_called
            has_been_called = True
            
        sub_id = var.subscribe(handler)
        var.unsubscribe(sub_id)
        var.value = 2
        assert has_been_called is False

    def test_error_remove_subscription(self):
        var = variable.Variable("foo")
        with pytest.raises(variable.VariableError, match="Unknown subscription id 0"):
            var.unsubscribe(0)
        
