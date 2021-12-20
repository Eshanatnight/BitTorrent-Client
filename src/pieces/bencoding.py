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

    def _consume(self) -> bytes:
        """
        Read and then consume the next character from the data
        """
        self._index += 1

    def _read(self, length: int) -> bytes:
        """
        :return: Read the 'length' number of bytes from the data and return the result
        """
        # TODO
        pass

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