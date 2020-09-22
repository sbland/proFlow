# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_inspect_process_empty process_inputs'] = {
    'additional_inputs': {
    },
    'config_inputs': {
    },
    'parameter_inputs': {
    },
    'state_inputs': {
    },
    'state_outputs': {
        '_result': 'state.x'
    }
}

snapshots['test_inspect_process process_inputs'] = {
    'additional_inputs': {
        '10': 'z'
    },
    'config_inputs': {
        'config.a': 'x'
    },
    'parameter_inputs': {
        'state.a': 'y'
    },
    'state_inputs': {
        'state.a': 'y'
    },
    'state_outputs': {
        '_result': 'state.x'
    }
}
