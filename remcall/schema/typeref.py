class TypeRef:
    '''Represents temporary type references by an integer; to be resolved
       to actual types later
    '''
    def __init__(self, type_ref: int):
        self.type_ref = type_ref

    def __hash__(self):
        return hash(self.type_ref)

    def __eq__(self, other):
        return isinstance(other, TypeRef) and self.type_ref == other.type_ref

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.type_ref)
