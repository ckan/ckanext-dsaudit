from ckan.plugins.toolkit import chained_action

@chained_action
def datastore_create(original_action, context, data_dict):
    return original_action(context, data_dict)

@chained_action
def datastore_upsert(original_action, context, data_dict):
    return original_action(context, data_dict)

@chained_action
def datastore_delete(original_action, context, data_dict):
    return original_action(context, data_dict)
