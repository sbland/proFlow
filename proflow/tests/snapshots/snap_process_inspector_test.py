# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_inspect_process_inputs process_inputs'] = {
    'additional_inputs': (
        "10, as_='z'"
    ,),
    'config_inputs': (
        "config.a, as_='x'"
    ,),
    'parameter_inputs': (
        "state.a, as_='y'"
    ,),
    'state_inputs': (
        "state.a, as_='y'"
    ,)
}

snapshots['test_inspect_process_inputs_empty process_inputs'] = {
    'additional_inputs': None,
    'config_inputs': None,
    'parameter_inputs': None,
    'state_inputs': None
}
