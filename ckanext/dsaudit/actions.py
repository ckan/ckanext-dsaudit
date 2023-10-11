from ckan.plugins.toolkit import (
    chained_action,
    fresh_context,
    get_action,
    get_validator,
)

from ckanext.activity.logic.schema import default_create_activity_schema

@chained_action
def datastore_create(original_action, context, data_dict):
    rval = original_action(context, data_dict)
    acontext = dict(
        fresh_context(context),
        ignore_auth=True,
        schema=dsaudit_create_activity_schema(),
    )

    res = context['model'].Resource.get(rval['resource_id'])
    create_data = {
        k: v for k, v in rval.items() if k not in ['records', 'method']
    }
    create_data['existing'] = res.extras.get('datastore_active', False)
    get_action('activity_create')(acontext, {
        'user_id': context['model'].User.get(context['user']).id,
        'object_id': rval['resource_id'],
        'activity_type': 'created datastore',
        'data': create_data,
    })

    if rval.get('records'):
        change_data = {
            k:v for k, v in rval.items() if k in [
                'resource_id', 'records', 'method']
        }
        get_action('activity_create')(acontext, {
            'user_id': context['model'].User.get(context['user']).id,
            'object_id': rval['resource_id'],
            'activity_type': 'changed datastore',
            'data': change_data,
        })
    return rval


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
        'data': rval,
    })
    return rval


@chained_action
def datastore_delete(original_action, context, data_dict):
    activity_data = {}
    if 'filters' in data_dict:
        scontext = dict(
            fresh_context(context),
            ignore_auth=True,
        )
        srval = get_action('datastore_search')(scontext, {
            'resource_id': data_dict['resource_id'],
            'filters': data_dict['filters'],
        })
        activity_data = {
            'records': srval['records'],
            'total': srval['total'],
        }

    rval = original_action(context, data_dict)

    acontext = dict(
        fresh_context(context),
        ignore_auth=True,
        schema=dsaudit_create_activity_schema(),
    )
    activity_data['filters'] = rval['filters']
    get_action('activity_create')(acontext, {
        'user_id': context['model'].User.get(context['user']).id,
        'object_id': rval['resource_id'],
        'activity_type': 'deleted datastore',
        'data': activity_data,
    })
    return rval


def dsaudit_create_activity_schema():
    '''
    remove checks on object_id and activity_type since we create
    new activity types
    '''
    sch = default_create_activity_schema()
    del sch['object_id'][-1]
    del sch['activity_type'][-1]
    return sch
