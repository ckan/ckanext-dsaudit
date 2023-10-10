import ckan.plugins as p

from ckanext.dsaudit import blueprint, helpers
from ckanext.dsaudit.actions import (
    datastore_create, datastore_upsert, datastore_delete
)
from ckan.lib.plugins import DefaultDatasetForm, DefaultTranslation

class DSAuditPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.IActions)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.ITranslation)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')

    def get_blueprint(self):
        return blueprint.dsaudit

    def get_actions(self):
        return {
            'datastore_create': datastore_create,
            'datastore_upsert': datastore_upsert,
            'datastore_delete': datastore_delete,
        }

    def get_helpers(self):
        return {
            'dsaudit_resource_url': helpers.dsaudit_resource_url,
            'dsaudit_data_columns': helpers.dsaudit_data_columns,
        }
