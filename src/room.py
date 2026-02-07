class Room:
    def __init__(self, id: int):
        self.id = id
        self.name = None
        self.chairs = {"W": 0, "P": 0, "S": 0, "C": 0}
        self.merged_into = None

    def merge_with(self, other: "Room") -> "Room":
        """Merge other room into this one. Returns self."""
        for chair_type in self.chairs:
            self.chairs[chair_type] += other.chairs[chair_type]
        if other.name and not self.name:
            self.name = other.name
        other.merged_into = self  # Forward pointer
        return self

    def final(self) -> "Room":
        """Follow the merge chain to the final room (with path compression to avoid long recursions)."""
        if self.merged_into is None:
            return self
        self.merged_into = self.merged_into.final()  # Compress path
        return self.merged_into
