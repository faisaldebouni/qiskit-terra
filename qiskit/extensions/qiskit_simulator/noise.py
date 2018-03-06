# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

# Copyright 2017 IBM RESEARCH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""
local_qiskit_simulator command to toggle noise off or on.
"""
from qiskit import CompositeGate
from qiskit import Gate
from qiskit import QuantumCircuit
from qiskit._instructionset import InstructionSet
from qiskit._quantumregister import QuantumRegister


class NoiseGate(Gate):
    """Simulator save operation."""

    def __init__(self, m, qubit, circ=None):
        """Create new save gate."""
        super().__init__("noise", [m], [qubit], circ)

    def qasm(self):
        """Return OPENQASM string."""
        qubit = self.arg[0]
        m = self.param[0]
        return self._qasmif("noise(%d) %s[%d];" % (m,
                                                   qubit[0].name,
                                                   qubit[1]))

    def inverse(self):
        """Invert this gate."""
        return self  # self-inverse

    def reapply(self, circ):
        """Reapply this gate to corresponding qubits in circ."""
        self._modifiers(circ.noise(self.param[0], self.arg[0]))


def noise(self, m, q):
    """Cache the quantum state of locla_qiskit_simulator."""
    if isinstance(q, QuantumRegister):
        gs = InstructionSet()
        for j in range(q.size):
            gs.add(self.noise(m, (q, j)))
        return gs
    self._check_qubit(q)
    return self._attach(NoiseGate(m, q, self))


# Add to QuantumCircuit and CompositeGate classes
QuantumCircuit.noise = noise
CompositeGate.noise = noise

# Add to QASM header for parsing
QuantumCircuit.header += "\ngate noise(m) a {}" + \
    "  // (local_qiskit_simulator) switch noise off (0) or on (1)"
