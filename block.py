class Block:
    def __init__(self, coords):
        self.coords = coords
        self.w = max(c[0] for c in self.coords) + 1
        self.h = max(c[1] for c in self.coords) + 1

    def __repr__(self):
        return f"<Block w={self.w} h={self.h} coords={self.coords}>"
    
    @classmethod
    def from_raw_coords(cls, coords, s):
        min_coord = min(coords, key=lambda c: c[0] + c[1])

        # Normalize everything to topleftmost
        new_coords = [[x,y] for x, y in coords]
        for i in range(len(new_coords)):
            new_coords[i][0] -= min_coord[0]
            new_coords[i][1] -= min_coord[1]
        
        # Normalize in terms of 1x1s
        for i in range(len(new_coords)):
            new_coords[i][0] /= s
            new_coords[i][1] /= s
        
        # Round to nearest int
        for i in range(len(new_coords)):
            new_coords[i][0] = int(round(new_coords[i][0]))
            new_coords[i][1] = int(round(new_coords[i][1]))
        
        return cls(new_coords)
