from ckan import authz

def resource_activity_list(context, data_dict):
    return authz.is_authorized(
        'resource_show', context, {'id': data_dict['id']}
    )
