import backoff
import psycopg2
from config import settings
from psycopg2.extras import DictCursor


class FromMoviesLoader:
    """
    Класс с методами проверки обновлений в таблицах,
    получения фильмов по ID и загрузки из Postgress
    """

    def __init__(self):
        self.dsn = {
            "dbname": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "host": settings.POSTGRES_SERVER,
            "port": settings.POSTGRES_PORT,
            "options": "-c search_path=content",
        }
        self.page_size = settings.PAGE_SIZE

    @backoff.on_exception(backoff.expo, psycopg2.OperationalError)
    def pg_execute(self, query, param):
        with psycopg2.connect(**self.dsn, cursor_factory=DictCursor) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (param,))
                return cursor.fetchall()

    def check_update(self, table_name: str, date: str, offset: int) -> list:
        """
        Метод проверки обновлений в таблице
        table - таблица для проверки, например 'pesrons'
        date - дата выше которой проверять
        Возвращает список id и updated_at
        """
        query = """
                SELECT id, updated_at
                FROM content.{table}
                WHERE updated_at > %s
                ORDER BY updated_at
                LIMIT {limit} OFFSET {offset};
                """.format(
            table=table_name, limit=self.page_size, offset=offset
        )

        return self.pg_execute(query, date)

    def load_persons(self, ids: list, offset: int) -> list:
        query = """
                SELECT id, full_name
                FROM content.person
                WHERE id in %s
                ORDER BY updated_at
                LIMIT {limit} OFFSET {offset};
                """.format(
            limit=self.page_size, offset=offset
        )

        return self.pg_execute(query, ids)

    def load_genres(self, ids: list, offset: int) -> list:
        query = """
                SELECT id, name, description
                FROM content.genre
                WHERE id in %s
                ORDER BY updated_at
                LIMIT {limit} OFFSET {offset};
                """.format(
            limit=self.page_size, offset=offset
        )

        return self.pg_execute(query, ids)

    def load_movies_from_pg(self, ids: tuple, offset: int) -> list:
        """
        Метод получения фильмов с сопутствующей информацией
        Возвращает список фильмов по id из ids смещаясь на offset для загрузки пачками
        """

        query = """
            SELECT
                fw.id, 
                fw.title, 
                fw.description, 
                fw.rating, 
                fw.type, 
                fw.created_at, 
                fw.updated_at, 
                json_agg(
                    distinct jsonb_build_object(
                        'name', p.full_name, 'role', pfw.role, 'id', p.id
                    )
                ) as persons,
                array_agg(distinct(g.name)) as genres
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id 
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN %s
            GROUP BY fw.id
            LIMIT {limit} OFFSET {offset};
        """.format(
            limit=self.page_size, offset=offset
        )

        return self.pg_execute(query, ids)

    def load_ids_movies_for_update(
        self, table_name: str, ids: tuple, offset: int
    ) -> list:
        """
        Метод получения id фильмов из связанных таблиц
        table_name - таблица для которой смотрим связь с фильмами
        ids - id Pesron или Genre для которых ищем свзяь
        offset - для пачки
        Возвращает список id фильмов, которые связаны с Pesron или Genre
        """

        if table_name == "person":
            m2m_table = "person_film_work"
        else:
            m2m_table = "genre_film_work"

        query = """
            SELECT fw.id, fw.updated_at
            FROM content.film_work fw
            LEFT JOIN content.{m2m_table} m2m_fw ON m2m_fw.film_work_id = fw.id
            WHERE m2m_fw.{table}_id IN %s
            ORDER BY fw.updated_at
            LIMIT {limit} OFFSET {offset};
        """.format(
            m2m_table=m2m_table, table=table_name, limit=self.page_size, offset=offset
        )

        return self.pg_execute(query, ids)
