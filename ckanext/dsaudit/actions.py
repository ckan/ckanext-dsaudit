from ckan.plugins.toolkit import (
    chained_action,
    get_action,
    h,
)

try:
    from ckan.plugins.toolkit import fresh_context
except ImportError:
    def fresh_context(context):
        return {
            k: context[k] for k in (
                'model', 'session', 'user', 'auth_user_obj',
                'ignore_auth', 'defer_commit',
            ) if k in context
        }

try:
    from ckanext.activity.logic.schema import (
        default_create_activity_schema,
    )
except ImportError:
    from ckan.logic.schema import (
        default_create_activity_schema,
    )


def _is_system_user(context):
    """
    Checks if the current contextual user is the system/site user,
    or if there is no current user: Anonymous or other plugins that
    pass a blank or None user in the context like Xloader.

    Generally, Anonymous users will not have permissions to Datastore
    actions. However, pluginx like Xloader may pass ignore_auth with
    an empty user in the context.
    """
    site_user = get_action("get_site_user")({"ignore_auth": True}, {})
    if site_user["name"] == context.get('user') or not context.get('user'):
        return True
    return False


@chained_action
def datastore_create(original_action, context, data_dict):
    rval = original_action(context, data_dict)
    res = context['model'].Resource.get(rval['resource_id'])
    # we want to record activity for `upload` type Data Dcitionary saving
    if res.url_type not in h.datastore_rw_resource_url_types() and _is_system_user(context):
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
        'object_id': res.package_id,
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
            'object_id': res.package_id,
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
    if rval.get('dry_run'):
        return rval

    scontext = dict(
        fresh_context(context),
        ignore_auth=True,
    )
    srval = get_action('datastore_search')(scontext, {
        'resource_id': data_dict['resource_id'],
        'limit': 0,
        'include_total': False,
    })
    activity_data = {
        'fields': [
            f for f in srval['fields']
            if any(f['id'] in r for r in rval['records'])
        ],
        'records': rval['records'],
        'method': rval.get('method', 'upsert'),
        'resource_id': res.id,
    }
    get_action('activity_create')(acontext, {
        'user_id': context['model'].User.get(context['user']).id,
        'object_id': res.package_id,
        'activity_type': 'changed datastore',
        'data': activity_data,
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
            'fields': srval['fields'],
            'records': srval['records'],
            'total': srval['total'],
        }

    rval = original_action(context, data_dict)

    acontext = dict(
        fresh_context(context),
        ignore_auth=True,
        schema=dsaudit_create_activity_schema(),
    )
    # datastore_delete schema does not require filters,
    # only datastore_records_delete does.
    activity_data['filters'] = rval.get('filters')
    activity_data['resource_id'] = res.id
    get_action('activity_create')(acontext, {
        'user_id': context['model'].User.get(context['user']).id,
        'object_id': res.package_id,
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
