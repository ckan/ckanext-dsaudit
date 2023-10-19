import ckan.plugins as p

from ckanext.dsaudit import views, helpers, actions, auth
from ckan.lib.plugins import DefaultDatasetForm, DefaultTranslation

class DSAuditPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.ITranslation)

    def update_config(self, config):
        if not p.toolkit.check_ckan_version('2.10'):
            p.toolkit.add_template_directory(config, '2.9_templates')
        p.toolkit.add_template_directory(config, 'templates')

    def get_blueprint(self):
        return views.dsaudit

    def get_actions(self):
        return {
            'resource_activity_list': actions.resource_activity_list,
            'datastore_create': actions.datastore_create,
            'datastore_upsert': actions.datastore_upsert,
            'datastore_delete': actions.datastore_delete,
        }

    def get_auth_functions(self):
        return {
            'resource_activity_list': auth.resource_activity_list,
        }

    def get_helpers(self):
        return {
            'dsaudit_resource_url': helpers.dsaudit_resource_url,
            'dsaudit_data_columns': helpers.dsaudit_data_columns,
            'dsaudit_preview_records': helpers.dsaudit_preview_records,
        }
