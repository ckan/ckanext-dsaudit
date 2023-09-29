from ckan.plugins.toolkit import (
    chained_action,
    fresh_context,
    get_action,
    get_validator,
)

from ckanext.activity.logic.schema import default_create_activity_schema

@chained_action
def datastore_create(original_action, context, data_dict):
    return original_action(context, data_dict)

@chained_action
def datastore_upsert(original_action, context, data_dict):
    rval = original_action(context, data_dict)
    acontext = dict(
        fresh_context(context),
        ignore_auth=True,
        schema=dsaudit_create_activity_schema(),
    )
    get_action('activity_create')(acontext, {
        'user_id': context['model'].User.get(context['user']).id,
        'object_id': rval['resource_id'],
        'activity_type': 'changed datastore',
        'data': {
            'records': rval['records'],
        },
    })
    return rval

@chained_action
def datastore_delete(original_action, context, data_dict):
    return original_action(context, data_dict)


def dsaudit_create_activity_schema():
    '''
    remove checks on object_id and activity_type since we create
    new activity types
    '''
    sch = default_create_activity_schema()
    del sch['object_id'][-1]
    del sch['activity_type'][-1]
    return sch
