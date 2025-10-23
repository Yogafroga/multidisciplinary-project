import database
import logging
from backend.app.models.user import User

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        database.init_db()
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {str(e)}", exc_info=True)
    User.create_table(safe=True)
