# see http://stackoverflow.com/a/9051055

def memory_backed_tempfile():
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
    return StringIO()

def file_backed_tempfile():
    import tempfile
    return tempfile.NamedTemporaryFile(mode="r+b")

class ReseekFile:
    """wrap a file handle to allow seeks back to the beginning

    Takes a file handle in the constructor.
    
    See the module docstring for more documentation.
    """
    def __init__(self, file, tempfile_factory = memory_backed_tempfile):
        self.file = file
        self.buffer_file = tempfile_factory()
        self.at_beginning = 1
        try:
            self.beginning = file.tell()
        except (IOError, AttributeError):
            self.beginning = 0
        self._use_buffer = 1
        self._buffer_size = 0
        
    def seek(self, offset, whence = 0):
        """offset, whence = 0

        Seek to a given byte position.  Only supports whence == 0
        and offset == the initial value of ReseekFile.tell() (which
        is usually 0, but not always.)
        """
        if whence != 0:
            raise TypeError("Unexpected whence value of %s; expecting 0" % \
                            (whence,))
        if offset != self.beginning:
            raise TypeError("Unexpected offset value of %r; expecting '%s'" % \
                             (offset, self.beginning))
        self.buffer_file.seek(0)
        self.at_beginning = 1
        
    def tell(self):
        """the current position of the file

        The initial position may not be 0 if the underlying input
        file supports tell and it not at position 0.
        """
        if not self.at_beginning:
            raise TypeError("ReseekFile cannot tell except at the beginning of file")
        return self.beginning

    def _read(self, size):
        if size < 0:
            y = self.file.read()
            z = self.buffer_file.read() + y
            if self._use_buffer:
                self.buffer_file.write(y)
                self._buffer_size += len(y)
            return z
        if size == 0:
            return ""
        x = self.buffer_file.read(size)
        if len(x) < size:
            y = self.file.read(size - len(x))
            if self._use_buffer:
                self.buffer_file.write(y)
                self._buffer_size += len(y)
            return x + y
        return x
        
    def read(self, size = -1):
        """read up to 'size' bytes from the file

        Default is -1, which means to read to end of file.
        """
        x = self._read(size)
        if self.at_beginning and x:
            self.at_beginning = 0
        self._check_no_buffer()
        return x

    def readline(self):
        """read a line from the file"""

        # Can we get it out of the buffer_file?
        s = self.buffer_file.readline()
        if s[-1:] == "\n":
            return s
        # No, so now we read a line from the input file
        t = self.file.readline()

        # Append the new data to the buffer, if still buffering
        if self._use_buffer:
            self.buffer_file.write(t)
            self._buffer_size += len(t)        
        self._check_no_buffer()

        return s + t

    def readlines(self):
        """read all remaining lines from the file"""
        s = self.read()
        lines = []
        i, j = 0, s.find("\n")
        while j > -1:
            lines.append(s[i:j+1])
            i = j+1
            j = s.find("\n", i)
        if i < len(s):
            # Only get here if the last line doesn't have a newline
            lines.append(s[i:])
        return lines

    def _check_no_buffer(self):
        # If 'nobuffer' called and finished with the buffer file
        # then get rid of the buffer and redirect everything to
        # the original input file.
        if (self._use_buffer == 0 and 
            (self.buffer_file.tell() == self._buffer_size)):
            # I'm doing this for the slightly better performance
            self.seek = getattr(self.file, "seek", None)
            self.tell = getattr(self.file, "tell", None)
            self.read = self.file.read
            self.readline = self.file.readline
            self.readlines = self.file.readlines
            del self.buffer_file

    def nobuffer(self):
        """tell the ReseekFile to stop using the buffer once it's exhausted"""
        self._use_buffer = 0
