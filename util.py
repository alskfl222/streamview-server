def remove_objectId(doc):
    try:
        del doc['_id']
    except:
        pass
    return doc