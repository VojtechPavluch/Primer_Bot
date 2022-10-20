class Primer:

    def __init__(self, name, direction, sequence, length, tm, pcr_len, organism):
        self.name = name
        self.direction = direction
        self.sequence = sequence
        self.length = length
        self.tm = tm
        self.pcr_len = pcr_len
        self.organism = organism
        self.abr = self.organism[0].lower()

    def print_primer(self):
        return f"{self.abr}-{self.name}-{self.sequence}-{self.pcr_len}-{self.direction}"





