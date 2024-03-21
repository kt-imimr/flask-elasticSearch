
class Check_file_type:
    def is_pdf(self, file_path):
        """
        Check if a file is a pdf
        """
        with open(file_path, 'rb') as f:
            return f.read(4) == b'%PDF'