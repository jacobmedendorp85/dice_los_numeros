

class D6Die(object):
    def __init__(self, name, values, pips) -> None:

        self.name = name
        self.active_face = None

        self.faces = {}
        for i in range(0, 6):
            face_str = "face%s" % i
            self.faces[face_str] = {
                'number': values[i],
                'pips': pips[i]
            }

    def set_active_face(self, face):
        self.active_face = self.faces[face]