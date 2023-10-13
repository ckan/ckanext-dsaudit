from ckan.plugins.toolkit import (
    chained_action,
    fresh_context,
    get_action,
    get_validator,
    h,
    check_access,
    ValidationError,
    ObjectNotFound,
)

from ckanext.activity.logic.schema import default_create_activity_schema
from ckanext.activity.model import activity as model_activity


def resource_activity_list(context, data_dict):
    include_hidden_activity = data_dict.get("include_hidden_activity", False)
    activity_types = data_dict.pop("activity_types", None)
    exclude_activity_types = data_dict.pop("exclude_activity_types", None)

    if activity_types is not None and exclude_activity_types is not None:
        raise ValidationError(
            {
                "activity_types": [
                    "Cannot be used together with `exclude_activity_types"
                ]
            }
        )

    check_access("resource_activity_list", context, data_dict)

    model = context["model"]

    resource_id = data_dict.get("id")

    offset = int(data_dict.get("offset", 0))
    limit = data_dict["limit"]  # defaulted, limited & made an int by schema
    after = data_dict.get("after")
    before = data_dict.get("before")

    activity_objects = model_activity.package_activity_list(
        resource_id,
        limit=limit,
        offset=offset,
        after=after,
        before=before,
        include_hidden_activity=include_hidden_activity,
        activity_types=activity_types,
        exclude_activity_types=exclude_activity_types,
    )

    return model_activity.activity_list_dictize(activity_objects, context)



@chained_action
def datastore_create(original_action, context, data_dict):
    rval = original_action(context, data_dict)
    res = context['model'].Resource.get(rval['resource_id'])
    if res.url_type not in h.datastore_rw_resource_url_types():
        return res

    acontext = dict(
        fresh_context(context),
        ignore_auth=True,
        schema=dsaudit_create_activity_schema(),
    )

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
    res = context['model'].Resource.get(rval['resource_id'])
    if res.url_type not in h.datastore_rw_resource_url_types():
        return res

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
    res = context['model'].Resource.get(data_dict.get('resource_id'))
    if not res or res.url_type not in h.datastore_rw_resource_url_types():
        return original_action(context, data_dict)

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
