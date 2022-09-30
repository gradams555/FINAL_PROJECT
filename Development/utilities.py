import qgis.core

def getAllFields(layer):
    fields = []
    print('layer: ' + str(layer))
    for field in layer.fields():
        print('name: ' + field.name())
        fields.append(field.name())
    return fields

def getStringFields(layer):
    fields = []
    for field in layer.fields():
        if field.typeName() == 'String':
            fields.append(field.name())
    return fields

def getNumericFields(layer):
    fields = []
    for field in layer.fields():
        if field.isNumeric():
            fields.append(field.name())
    return fields

