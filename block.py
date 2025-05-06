class Block:
    def __init__(self, coords):
        self.coords = coords
        self.w = max(c[0] for c in self.coords) - min(c[0] for c in self.coords) + 1
        self.h = max(c[1] for c in self.coords) - min(c[1] for c in self.coords) + 1

    def __repr__(self):
        return f"<Block w={self.w} h={self.h} coords={self.coords}>"
    
    @classmethod
    def from_raw_coords(cls, coords, s):
        new_coords = [[x,y] for x, y in coords]
        random_coord = coords[0]

        # Normalize everything to random coord
        for i in range(len(new_coords)):
            new_coords[i][0] -= random_coord[0]
            new_coords[i][1] -= random_coord[1]
        
        # Normalize in terms of 1x1s
        for i in range(len(new_coords)):
            new_coords[i][0] /= s
            new_coords[i][1] /= s
        
        # Round to nearest int
        for i in range(len(new_coords)):
            new_coords[i][0] = int(round(new_coords[i][0]))
            new_coords[i][1] = int(round(new_coords[i][1]))
        
        # Make the lowest 0,0
        lowest_x = min(c[0] for c in new_coords)
        lowest_y = min(c[1] for c in new_coords)

        for i in range(len(new_coords)):
            new_coords[i][0] -= lowest_x
            new_coords[i][1] -= lowest_y
        
        return cls(new_coords)
