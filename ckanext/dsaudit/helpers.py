from ckan import model
from ckan.plugins.toolkit import h, config

def dsaudit_resource_url(resource_id):
    package_id = model.Resource.get(resource_id).package_id
    pkg = model.Package.get(package_id)
    return h.url_for(
        pkg.type + '_resource.read',
        id=pkg.name,
        resource_id=resource_id,
    )

def dsaudit_data_columns(records):
    if records:
        return records[0].keys()
    return []

def dsaudit_preview_records():
    return int(config.get('ckanext.dsaudit.preview_records', 12))
