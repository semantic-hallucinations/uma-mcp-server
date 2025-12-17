class RedisKeys:
    """
    Централизованное хранилище форматов ключей Redis.
    Соответствует контракту с ETL-сервисом.
    """
    
    SYSTEM_CURRENT_WEEK = "system:current_week"

    @staticmethod
    def schedule(entity_type: str, identifier: str) -> str:
        """
        Возвращает ключ для расписания.
        :param entity_type: 'group' или 'employee'
        :param identifier: номер группы или url_id сотрудника
        """
        return f"schedule:{entity_type}:{identifier}"