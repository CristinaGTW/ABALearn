class TopRuleNotFoundException(Exception):
    pass

class InvalidRuleBodyException(Exception):
    pass

class CredulousSemanticsException(Exception):
    print("Goal achieved under credulous semantics!")
    pass