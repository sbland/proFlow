import pytest
from .Switch import switch, __s__


def test_switch():
    process_a = "process_a"
    process_b = "process_b"
    process_to_run = switch(
        gate="this_one",
        this_one=process_a,
        not_this_one=process_b,
    )
    assert process_to_run == process_a


def test_switch_short_name():
    process_a = "process_a"
    process_b = "process_b"
    process_to_run = __s__(
        gate="this_one",
        this_one=process_a,
        not_this_one=process_b,
    )
    assert process_to_run == process_a


def test_switch_with_defined_options():
    process_a = "process_a"
    process_b = "process_b"
    process_to_run = switch(
        gate="this one",
        options={
            "this one": process_a,
            "not this one": process_b,
        }

    )
    assert process_to_run == process_a


def test_switch_missing_option():
    with pytest.raises(KeyError) as e:
        switch(comment="missing gate", gate="other option", options={})
    assert "\"other option\" is not an option in \"missing gate\" switch" in str(e)
