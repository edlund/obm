# OBM - Object-Bit Mapper
# Copyright (c) 2020, Erik Edlund <erik.edlund@32767.se>
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of Erik Edlund, nor the names of its contributors may
#   be used to endorse or promote products derived from this software without
#   specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from obm import BitFieldPartition, Int64BitField

# Practical example: A J1939 CEFF CAN data frame
class ExtendedJoystickMessage(Int64BitField):
    a1NeutralPositionStatus = BitFieldPartition(0, 0, 2)
    a1NegativePositionStatus = BitFieldPartition(0, 2, 2)
    a1PositivePositionStatus = BitFieldPartition(0, 4, 2)
    a1Position = BitFieldPartition(0, 6, 10)
    a2NeutralPositionStatus = BitFieldPartition(2, 0, 2)
    a2NegativePositionStatus = BitFieldPartition(2, 2, 2)
    a2PositivePositionStatus = BitFieldPartition(2, 4, 2)
    a2Position = BitFieldPartition(2, 6, 10)
    a3NeutralPositionStatus = BitFieldPartition(4, 0, 2)
    a3NegativePositionStatus = BitFieldPartition(4, 2, 2)
    a3PositivePositionStatus = BitFieldPartition(4, 4, 2)
    a3Position = BitFieldPartition(4, 6, 10)
    axisPadding = BitFieldPartition(6, 0, 2)
    a3DetentPositionStatus = BitFieldPartition(6, 2, 2)
    a2DetentPositionStatus = BitFieldPartition(6, 4, 2)
    a1DetentPositionStatus = BitFieldPartition(6, 6, 2)
    b4 = BitFieldPartition(7, 0, 2)
    b3 = BitFieldPartition(7, 2, 2)
    b2 = BitFieldPartition(7, 4, 2)
    b1 = BitFieldPartition(7, 6, 2)

    def __init__(self) -> None:
        super(ExtendedJoystickMessage, self).__init__(self.__class__.__name__)

class BitFieldPartitionTestCase(unittest.TestCase):
    def testProperties(self) -> None:
        partition = BitFieldPartition(2, 6, 10)
        self.assertEqual(0x3FF, partition.mask)
        self.assertEqual(22, partition.shift)
        partition.value = 0x3FE
        self.assertEqual(0x3FE, partition.masked_value)
    
    def testOverflow(self) -> None:
        partition = BitFieldPartition(0, 4, 2)
        partition.name = "b1"
        partition.value = 0x0
        partition.value = 0x1
        partition.value = 0x2
        partition.value = 0x3
        with self.assertRaises(OverflowError) as context:
            partition.value = 0x4
        self.assertEqual(str(context.exception), "b1: More than 2 bits of data (0x04)")

class BitFieldTestCase(unittest.TestCase):
    def testData(self) -> None:
        ejm = ExtendedJoystickMessage()
        ejm.a1NeutralPositionStatus.value = 0x1
        ejm.a1NegativePositionStatus.value = 0x0
        ejm.a1PositivePositionStatus.value = 0x0
        ejm.a1Position.value = 0x2AA
        ejm.a2NeutralPositionStatus.value = 0x3
        ejm.a2NegativePositionStatus.value = 0x3
        ejm.a2PositivePositionStatus.value = 0x3
        ejm.a2Position.value = 0x3FF
        ejm.a3NeutralPositionStatus.value = 0x3
        ejm.a3NegativePositionStatus.value = 0x3
        ejm.a3PositivePositionStatus.value = 0x3
        ejm.a3Position.value = 0x3FF
        ejm.axisPadding.value = 0x3
        ejm.a3DetentPositionStatus.value = 0x3
        ejm.a2DetentPositionStatus.value = 0x3
        ejm.a1DetentPositionStatus.value = 0x3
        ejm.b4.value = 0x3
        ejm.b3.value = 0x1
        ejm.b2.value = 0x0
        ejm.b1.value = 0x1
        self.assertEqual(ejm.data_int, 0x47FF_FFFF_FFFF_AA81)
        self.assertEqual(ejm.data_ints, [0x81, 0xAA, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x47])
        for name, value in ejm.partition_map().items():
            self.assertEqual(value, ejm.partition(name).masked_value)
    
    def testParseData(self) -> None:
        ejm = ExtendedJoystickMessage()
        ejm.parse_data_int(0x47FF_FFFF_FFFF_AA81)
        self.assertEqual(ejm.data_int, 0x47FF_FFFF_FFFF_AA81)

if __name__ == "__main__":
    unittest.main()
