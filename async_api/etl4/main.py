import logging.config
import time

from config import settings
from logger_conf import LOGGING_CONFIG
from my_elastic import check_or_create_es_index, load_to_es
from pg_loader import FromMoviesLoader
from statesaver import JsonFileStorage, State

movies_ids = set()
states = {}
storage = State(JsonFileStorage(settings.PATH_TO_STATE))

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("my_logger")


def download_upload():
    postgres_loader = FromMoviesLoader()

    for table in ["film_work", "person", "genre"]:
        logger.info("Check %s", table)
        date = (
            storage.get_state(table)
            if storage.get_state(table)
            else settings.DEFAULT_DATE
        )
        logger.info("Date for %s from state: %s", table, date)

        offset = 0
        ids_dates_for_update = []

        while True:
            ids_dates = postgres_loader.check_update(table, date, offset)
            ids_dates_for_update += ids_dates
            offset += postgres_loader.page_size
            if not ids_dates:
                break

        if not ids_dates_for_update:
            logger.info("No updates for %s table", table)
            continue

        # Сохраняем в словарь дату последнего объекта
        states[table] = str(ids_dates_for_update[-1]["updated_at"])

        # Формируем список id объектов имеющих обновление
        ids_list = tuple([record["id"] for record in ids_dates_for_update])

        if table == "film_work":
            movies_ids.update(
                ids_list
            )  # Если обновление найдено в фильмах, то просто добавляем его id

        else:
            # За одно получим и загрузим пачками в es сами объекты для новых индексов genre или person
            if table == "person":
                offset = 0
                persons = []
                while True:
                    persons = postgres_loader.load_persons(ids_list, offset)
                    if persons:
                        load_to_es(persons, index="person")
                        offset += postgres_loader.page_size
                    else:
                        break

            if table == "genre":
                offset = 0
                genres = []
                while True:
                    genres = postgres_loader.load_genres(ids_list, offset)
                    if genres:
                        load_to_es(genres, index="genre")
                        offset += postgres_loader.page_size
                    else:
                        break

            # И для es movies ищем связанные с таблицей фильмы пачками через offset

            offset = 0
            while True:
                movies_ids_for_update = postgres_loader.load_ids_movies_for_update(
                    table, ids_list, offset
                )
                if not movies_ids_for_update:
                    break
                ids = [movie["id"] for movie in movies_ids_for_update]
                movies_ids.update(ids)
                offset += postgres_loader.page_size

        if movies_ids:
            # Грузим фильмы пачками через offset по найденным id
            offset = 0
            esinfo = []
            while True:
                movies = postgres_loader.load_movies_from_pg(tuple(movies_ids), offset)
                offset += postgres_loader.page_size
                if not movies:
                    break
                esinfo = load_to_es(movies)

            # Сохраняем даты если от эластика нет ошибок
            elastic_err = esinfo[1]
            if not elastic_err:
                for key, value in states.items():
                    storage.set_state(key, value)


check_or_create_es_index()

while True:
    download_upload()
    time.sleep(60)
