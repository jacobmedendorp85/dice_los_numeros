
class DieD6(object):
    def __init__(self, die_type, face1, face2, face3, face4, face5, face6):
        self.die_type = die_type
        self.faces = {
            'face1': {
                'number': face1[0],
                'pips': face1[1]
            },
            'face2': {
                'number': face2[0],
                'pips': face2[1]
            },
            'face3': {
                'number': face3[0],
                'pips': face3[1]
            },
            'face4': {
                'number': face4[0],
                'pips': face4[1]
            },
            'face5': {
                'number': face5[0],
                'pips': face5[1]
            },
            'face6': {
                'number': face6[0],
                'pips': face6[1]
            },
        }
        self.active_face = None

    def set_active_face(self, face):
        self.active_face = self.faces[face]


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