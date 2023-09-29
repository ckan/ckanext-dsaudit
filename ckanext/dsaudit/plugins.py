import ckan.plugins as p

from ckanext.dsaudit.actions import (
    datastore_create, datastore_upsert, datastore_delete
)

class DSAuditPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.IActions)
    p.implements(p.ITemplateHelpers, inherit=True)

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
