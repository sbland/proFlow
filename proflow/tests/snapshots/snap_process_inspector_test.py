# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_inspect_process_empty process_inputs'] = (
    {
    },
    {
    },
    {
    },
    {
    },
    {
        '_result': 'state.x'
    }
)

snapshots['test_inspect_process process_inputs'] = (
    {
        'config.a': 'x'
    },
    {
        'state.a': 'y'
    },
    {
        'state.a': 'y'
    },
    {
        '10': 'z'
    },
    {
        '_result': 'state.x'
    }
)

snapshots['test_inspect_process_to_interfaces process_inputs'] = (
    GenericRepr('<generator object parse_inputs_to_interface.<locals>.<genexpr> at 0x100000000>'),
    GenericRepr('<generator object parse_inputs_to_interface.<locals>.<genexpr> at 0x100000000>'),
    GenericRepr('<generator object parse_inputs_to_interface.<locals>.<genexpr> at 0x100000000>'),
    GenericRepr('<generator object parse_inputs_to_interface.<locals>.<genexpr> at 0x100000000>'),
    [
        GenericRepr('I(from_="_result" as_="x")')
    ]
)
