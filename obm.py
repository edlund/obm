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

from typing import Any, Dict, List, cast

import copy
import json

class Config(object):
    error_check_overflow = True

class BitFieldPartition(object):
    """A partition of a bit field spanning 1 or more bits.
    """

    def __init__(self, start_byte: int, start_bit: int, length: int, value: int=0x0) -> None:
        self.name = ""
        self.start_byte = start_byte
        self.start_bit = start_bit
        self.length = length
        self._value = value

    @property
    def mask(self) -> int:
        return (1 << self.length) - 1
    
    @property
    def shift(self) -> int:
        return (self.start_byte * 8) + self.start_bit

    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, value: int) -> None:
        if Config.error_check_overflow and (value >> self.length) > 0:
            raise OverflowError("{name}: More than {length} bits of data (0x{value:02X})".format(
                name=self.name,
                length=self.length,
                value=value
            ))
        self._value = value

    @property
    def masked_value(self) -> int:
        return self.value & self.mask
    
    @property
    def prefixed_name(self) -> str:
        return "{}.{}:{} {}".format(self.start_byte, self.start_bit, self.length, self.name)

    def parse(self, data: int) -> None:
        self._value = (data >> self.shift) & self.mask

class BitField(object):
    """A N byte sized bit field data structure consisting
    of partitions, which union form the bit field.
    """

    def __init__(self, name: str, nbytes: int) -> None:
        if self.__class__ == BitField.__class__:
            raise NotImplementedError()
        self.name = name
        self.nbytes = nbytes
        self.partitions: List[BitFieldPartition] = []
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, BitFieldPartition):
                partition = copy.deepcopy(cast(BitFieldPartition, value))
                partition.name = name
                self.partitions.append(partition)
                setattr(self, name, partition)

    @property
    def mask(self) -> int:
        return (1 << self.nbits) - 1
    
    @property
    def nbits(self) -> int:
        return self.nbytes * 8
    
    @property
    def data_int(self) -> int:
        """Get the data as an int, truncated to nbytes.
        """
        data = 0x0
        for partition in self.partitions:
            data = data | (partition.masked_value << partition.shift)
        if Config.error_check_overflow and (data >> self.nbits) > 0:
            raise OverflowError("{name}: More than {length} bits of data".format(
                name=self.name,
                length=self.nbits
            ))
        return data & self.mask

    @property
    def data_ints(self) -> List[int]:
        """Get the data as a List of ints.
        """
        data = self.data_int
        return [(data >> (i * 8)) & 0xFF for i in range(0, self.nbytes)]
    
    @property
    def data_bytes(self) -> bytes:
        """Get the data as bytes.
        """
        return bytes(self.data_ints)
    
    def parse_data_int(self, data: int) -> None:
        """Parse a data int to partitions.
        """
        for partition in self.partitions:
            partition.parse(data)

    def partition(self, name: str) -> BitFieldPartition:
        """Get a partition by name.
        """
        for partition in self.partitions:
            if partition.name == name:
                return partition
        raise ValueError("Partition {name} not found".format(name=name))
    
    def partition_map(self, prefix: bool=False) -> Dict[str, int]:
        """Get a map of the partition names to their values, calculated
        from the data.
        """
        data = self.data_int
        field = "prefixed_name" if prefix else "name"
        return {
            getattr(partition, field): ((data >> partition.shift) & partition.mask)
            for partition in self.partitions
        }
    
    def printable_partition_map(self) -> str:
        """Get a partition map in pretty-printable format.
        """
        return json.dumps({
            k: "0x{:02X}".format(v)
            for k, v in self.partition_map(True).items()
        }, indent=2, sort_keys=True)

class Int8BitField(BitField):
    def __init__(self, name: str) -> None:
        if self.__class__ == Int8BitField.__class__:
            raise NotImplementedError()
        super(Int8BitField, self).__init__(name, 1)

class Int16BitField(BitField):
    def __init__(self, name: str) -> None:
        if self.__class__ == Int16BitField.__class__:
            raise NotImplementedError()
        super(Int16BitField, self).__init__(name, 2)

class Int32BitField(BitField):
    def __init__(self, name: str) -> None:
        if self.__class__ == Int32BitField.__class__:
            raise NotImplementedError()
        super(Int32BitField, self).__init__(name, 4)

class Int64BitField(BitField):
    def __init__(self, name: str) -> None:
        if self.__class__ == Int64BitField.__class__:
            raise NotImplementedError()
        super(Int64BitField, self).__init__(name, 8)

class Int128BitField(BitField):
    def __init__(self, name: str) -> None:
        if self.__class__ == Int128BitField.__class__:
            raise NotImplementedError()
        super(Int128BitField, self).__init__(name, 16)
