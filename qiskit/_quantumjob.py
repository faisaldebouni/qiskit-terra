# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=missing-param-doc,missing-type-doc

"""Quantum Job class"""
import uuid

# stable modules
from ._quantumcircuit import QuantumCircuit
from .qasm import Qasm

# beta modules
from .unroll import Unroller, DagUnroller, JsonBackend
from .dagcircuit import DAGCircuit


class QuantumJob():
    """Creates a quantum circuit job."""

    # TODO We need to create more tests for checking all possible inputs.
    # TODO Make this interface clearer -- circuits could be many things!
    def __init__(self, circuits, backend,
                 circuit_config=None, seed=None,
                 resources=None,
                 shots=1024, names=None,
                 do_compile=False, preformatted=False):
        """
        Args:
            circuits (QuantumCircuit|DagCircuit | list(QuantumCircuit|DagCircuit)):
                QuantumCircuit|DagCircuit or list of QuantumCircuit|DagCircuit.
                If preformatted=True, this is a raw qobj.
            backend (BaseBackend): The backend to run the circuit on, required.
            circuit_config (dict): Circuit configuration.
            seed (int): The intial seed the simulatros use.
            resources (dict): Resource requirements of job.
            shots (int): the number of shots
            names (str or list(str)): names/ids for circuits
            do_compile (boolean): compile flag.
            preformatted (bool): the objects in circuits are already compiled
                and formatted (qasm for online, json for local). If true the
                parameters "names" and "circuit_config" must also be defined
                of the same length as "circuits".
        """
        resources = resources or {'max_credits': 10}
        if isinstance(circuits, list):
            self.circuits = circuits
        else:
            self.circuits = [circuits]
        if names is None:
            self.names = []
            for _ in range(len(self.circuits)):
                self.names.append(str(uuid.uuid4()))
        elif isinstance(names, list):
            self.names = names
        else:
            self.names = [names]

        # check whether circuits have already been compiled
        # and formatted for backend.
        if preformatted:
            # circuits is actually a qobj...validate (not ideal but convenient)
            self.qobj = circuits
        else:
            self.qobj = self._create_qobj(circuits, circuit_config, backend,
                                          seed, resources, shots, do_compile)
        self.backend = backend
        self.resources = resources
        self.seed = seed
        self.result = None

    def _create_qobj(self, circuits, circuit_config, backend, seed,
                     resources, shots, do_compile):
        # local and remote backends currently need different
        # compilied circuit formats
        formatted_circuits = []
        if do_compile:
            for circuit in circuits:
                formatted_circuits.append(None)
        else:
            # if backend in backends.local_backends():
            if backend.configuration.get('local'):
                for circuit in self.circuits:
                    basis = ['u1', 'u2', 'u3', 'cx', 'id']
                    unroller = Unroller
                    # TODO: No instanceof here! Refactor this class
                    if isinstance(circuit, DAGCircuit):
                        unroller = DagUnroller
                    elif isinstance(circuit, QuantumCircuit):
                        # TODO: We should remove this code path (it's redundant and slow)
                        circuit = Qasm(data=circuit.qasm()).parse()
                    unroller_instance = unroller(circuit, JsonBackend(basis))
                    compiled_circuit = unroller_instance.execute()
                    formatted_circuits.append(compiled_circuit)

            else:
                for circuit in self.circuits:
                    formatted_circuits.append(circuit.qasm(qeflag=True))

        # create circuit component of qobj
        circuit_records = []
        if circuit_config is None:
            config = {'coupling_map': None,
                      'basis_gates': 'u1,u2,u3,cx,id',
                      'layout': None,
                      'seed': seed}
            circuit_config = [config] * len(self.circuits)

        for circuit, fcircuit, name, config in zip(self.circuits,
                                                   formatted_circuits,
                                                   self.names,
                                                   circuit_config):
            record = {
                'name': name,
                'compiled_circuit': None if do_compile else fcircuit,
                'compiled_circuit_qasm': None if do_compile else fcircuit,
                'config': config
            }
            circuit_records.append(record)

        return {'id': str(uuid.uuid4()),
                'config': {
                    'max_credits': resources['max_credits'],
                    'shots': shots,
                    'backend_name': backend.configuration['name']
                },
                'circuits': circuit_records}
