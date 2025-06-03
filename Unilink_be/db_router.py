class ChatRouter:
    """
    Routes chat models to the default Postgres DB.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'chat':
            return 'default'  # PostgreSQL
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'chat':
            return 'default'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'chat':
            return db == 'default'
        return None
