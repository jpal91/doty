
class CustomList:

    def __init__(self) -> None:
        self.__list = []
    
    def __iadd__(self, other) -> None:
        self.__list.append(other)

    def __isub__(self, other) -> None:
        self.__list.remove(other)
    
    def __contains__(self, other) -> bool:
        return other in self.__list

class ShortReport:

    def __init__(self) -> None:
        pass