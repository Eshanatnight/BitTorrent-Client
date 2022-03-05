"""
This file deals with all the classes that are used to encode and decode
the binary encoded (bencoded) data.

class Encoder - Encodes the data given as a python object into a binary encoded string.
class Decoder - Decodes the binary encoded string into the necessary python object.
"""

from collections import OrderedDict

# Token that indicates the start of an int
TOKEN_INTEGER = b'i'

# Token that indicates the start of a list
TOKEN_LIST = b'l'

# Token that indicates the start of a Dict
TOKEN_DICT = b'd'

# Token that indicates the end of lists, dicts and integer values
TOKEN_END = b'e'

# Token that delimits the string length from string data
TOKEN_STRING_SEPARATOR = b':'

# Start of the Decoder Class


class Decoder:
    """
        Decodes the bencoded sequence of data
    """


    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise TypeError("Arg data must be of type bytes")

        self._data = data
        self._index = 0     # Sets the initial Index to 0


    def _peek(self):
        """
        :return: the next character of the bencoded data or None
        """

        if self._index + 1 >= len(self._data):
            return None

        return self._data[self._index : self._index + 1]


    def _consume(self):
        """
        Read and then consume the next character from the data
        """
        self._index += 1


    def _read(self, length: int) -> bytes:
        """
        :return: Read the 'length' number of bytes from the data and return the result
        """
        if self._index + length > len(self._data):
            raise IndexError(f"Cannot read {str(length)} bytes from the current position {str(self._index)}")

        result: bytes = self._data[self._index: self._index + length]
        self._index += length
        return result


    def _read_until(self, token: bytes) -> bytes:
        """
        Read the bencoded data until the given token is found
        :return: the characters read
        """
        try:
            occurrence = self._data.index(token, self._index)
            result = self._data[self._index: occurrence]
            self._index = occurrence + 1
            return result

        except ValueError:
            raise RuntimeError(f"Unable to find token {token}")


    def _decode_int(self) -> int:
        """
        :return: The integer value of the bencoded data
        """
        return int(self._read_until(TOKEN_END))


    def _decode_list(self) -> list:
        """
        :return Decode the bencoded list and return the matching python object
        """
        result = []

        # Recursively decode the list
        while self._data[self._index: self._index + 1] != TOKEN_END:
            result.append(self.decode())
        self._consume()    # consume the END token
        return result


    def _decode_dict(self) -> dict:
        """
        Decode the bencoded data
        :return a python dict
        """

        result = OrderedDict()
        while self._data[self._index: self._index + 1] != TOKEN_END:
            key = self.decode()
            result = self.decode()
            result[key] = result
        self._consume()    # consume the END token
        return result


    def _decode_string(self):
        bytes_to_read = int(self._read_until(TOKEN_STRING_SEPARATOR))
        data = self._read(bytes_to_read)
        return data.decode()


    def decode(self):
        """
        Decode the bencoded data and return the matching python object
        :return: A python object that represents the decoded data
        """

        c = self._peek()

        if c is None:
            raise EOFError("Unexpected End-Of-File")

        elif c == TOKEN_INTEGER:
            self._consume()     # consume the token
            return self._decode_int()

        elif c == TOKEN_LIST:
            self._consume()     # consume the token
            return self._decode_list()

        elif c == TOKEN_DICT:
            self._consume()     # consume the token
            return self._decode_dict()

        elif c == TOKEN_END:
            return None

        elif c in b"01234567899":
            return self._decode_str()

        else:
            raise RuntimeError(f"Invalid Token read at {str(self._index)}")



class Encoder:
    """
    Encodes the python object into the bencoded sequence of data

    List of supported Python Types:
        - str
        - int
        - list
        - dict
        - bytes

    """

    def __init__(self, data):
        self._data = data


    def encode(self):
        """
        Encode the python object into bencoded data
        :return the bencoded binary data
        """
        return self.encode_next(self._data)


    def encode_next(self, data):

        if type(data) == str:
            return self._encode_string(data)
        elif type(data) == int:
            return self._encode_int(data)
        elif type(data) == list:
            return self._encode_list(data)
        elif type(data) == dict:
            return self._encode_dict(data)
        elif type(data) == bytes:
            return data
        else:
            return None


    def _encode_int(self, data):
        return str.encode(f"i{str(data)}e")


    def _encode_string(self, data: str):
        return str.encode(f"{len(data)}:{data}")


    def _encode_bytes(self, data: str):
        result = bytearray()
        result += str.encode(str(len(data)))
        result += b':'
        result += data
        return result


    def _encode_list(self, data: list):
        result = bytearray('l', 'utf-8')
        result += b''.join([self.encode_next(item) for item in data])
        result += b'e'
        return result


    def _encode_dict(self, data: dict):
        result = bytearray('d', 'utf-8')
        for key, value in data.items():
            _k = self.encode_next(key)
            _v = self.encode_next(value)

            if key and value:
                result += _k
                result += _v

            else:
                raise RuntimeError(f"Bad Dict Error")

        result += b'e'
        return result