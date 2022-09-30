import statistics

class Overlay():

    # constructor (can be derived by subclasses)
    def __init__(self, feature):
        self.feature = feature

        self.elements = []

        self.average_change = 0
        self.median_change = 0

    def addElement(self, element):
        self.elements.append(element)

    def calculateAverage(self):
        if len(self.elements) > 0:
            temp_list = []
            for element in self.elements:
                temp_list.append(100 * (element.compare - element.base) / element.base)
            self.average_change = statistics.mean(temp_list)
        else:
            self.average_change = 0

    def calculateMedian(self):
        if len(self.elements) > 0:
            temp_list = []
            for element in self.elements:
                temp_list.append(100 * (element.compare - element.base) / element.base)
            self.median_change = statistics.median(temp_list)
        else:
            self.average_change = 0

class OverlayElement():

    def __init__(self, id, geometry, base = 0, compare = 0):
        self.id = id
        self.geometry = geometry
        self.base = base
        self.compare = compare