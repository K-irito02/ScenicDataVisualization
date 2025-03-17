class DatabaseRouter:
    """
    数据库路由，管理多数据库连接
    """
    
    def db_for_read(self, model, **hints):
        """
        根据模型确定用于读取的数据库
        """
        # 景区等级与门票价格关系表在hierarchy_TicketAnalysis数据库中
        if model._meta.app_label == 'scenic_data' and getattr(model._meta, 'db_table', '').endswith('_level_price'):
            return 'hierarchy_database'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        根据模型确定用于写入的数据库
        """
        # 景区等级与门票价格关系表在hierarchy_TicketAnalysis数据库中
        if model._meta.app_label == 'scenic_data' and getattr(model._meta, 'db_table', '').endswith('_level_price'):
            return 'hierarchy_database'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        确定模型对象之间是否允许关系
        """
        # 只允许同一数据库中的模型建立关系
        db1 = 'hierarchy_database' if obj1._meta.app_label == 'scenic_data' and getattr(obj1._meta, 'db_table', '').endswith('_level_price') else 'default'
        db2 = 'hierarchy_database' if obj2._meta.app_label == 'scenic_data' and getattr(obj2._meta, 'db_table', '').endswith('_level_price') else 'default'
        return db1 == db2
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        确定是否允许数据库迁移操作
        """
        # 只允许在default数据库上进行迁移操作
        if db == 'hierarchy_database':
            return False
        return True 