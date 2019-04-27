# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name
"""
One-pulse single-qubit gate.
"""
import numpy
from qiskit.circuit import CompositeGate
from qiskit.circuit import Gate
from qiskit.circuit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.decorators import _op_expand, _to_bits
from qiskit.qasm import pi
from qiskit.extensions.standard.u3 import U3Gate


class U2Gate(Gate):
    """One-pulse single-qubit gate."""

    def __init__(self, phi, lam, label=None):
        """Create new one-pulse single-qubit gate."""
        super().__init__("u2", 1, [phi, lam], label=label)

    def _define(self):
        definition = []
        q = QuantumRegister(1, "q")
        rule = [(U3Gate(pi / 2, self.params[0], self.params[1]), [q[0]], [])]
        for inst in rule:
            definition.append(inst)
        self.definition = definition

    def inverse(self):
        """Invert this gate.

        u2(phi,lamb)^dagger = u2(-lamb-pi,-phi+pi)
        """
        return U2Gate(-self.params[1] - pi, -self.params[0] + pi)

    def to_matrix(self):
        """Return a Numpy.array for the U3 gate."""
        isqrt2 = 1 / numpy.sqrt(2)
        phi, lam = self.params
        return numpy.array([[isqrt2, -numpy.exp(1j * lam) * isqrt2],
                            [
                                numpy.exp(1j * phi) * isqrt2,
                                numpy.exp(1j * (phi + lam)) * isqrt2
                            ]],
                           dtype=complex)


@_to_bits(1)
@_op_expand(1)
def u2(self, phi, lam, q):
    """Apply u2 to q."""
    return self.append(U2Gate(phi, lam), [q], [])


QuantumCircuit.u2 = u2
CompositeGate.u2 = u2
