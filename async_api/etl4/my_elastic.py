import json
import logging.config

import backoff
import elasticsearch
import requests
from config import settings
from elasticsearch import Elasticsearch, helpers
from logger_conf import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("my_logger")

es_url = settings.ES_URL


def prepare_for_es(pg_row: dict, index) -> dict:
    # Подготовка словарей для эластика

    if index == "movies":
        actors_names = []
        writers_names = []
        actors = []
        writers = []
        director = []
        for person in pg_row["persons"]:
            match person["role"]:
                case "director":
                    director = person["name"]
                case "actor":
                    actors_names.append(person["name"])
                    actors.append({"id": person["id"], "name": person["name"]})
                case "writer":
                    writers_names.append(person["name"])
                    writers.append({"id": person["id"], "name": person["name"]})

        prepared_movie = {
            "id": pg_row["id"],
            "imdb_rating": pg_row["rating"],
            "title": pg_row["title"],
            "description": pg_row["description"],
            "director": director,
            "actors_names": actors_names,
            "writers_names": writers_names,
            "genre": pg_row["genres"],
            "actors": actors,
            "writers": writers,
        }
        return prepared_movie

    if index == "person":
        prepared_person = {
            "id": pg_row["id"],
            "full_name": pg_row["full_name"],
        }
        return prepared_person

    if index == "genre":
        prepared_genre = {
            "id": pg_row["id"],
            "name": pg_row["name"],
            "description": pg_row["description"],
        }
        return prepared_genre


def gen_for_esbulk(data: list, index) -> dict:
    # Генератор для es bulk. Для каждой страницы данных подготавливает doc

    for row in data:
        es_prepared_dict = prepare_for_es(dict(row), index)
        doc = {
            "_index": index,
            "_id": es_prepared_dict["id"],
            "_source": es_prepared_dict,
        }
        yield doc


@backoff.on_exception(backoff.expo, requests.exceptions.ConnectionError)
def check_or_create_es_index() -> None:
    # Проверяет существование индекса, пробует создать если его нет
    logger.info("Trying check es index")
    es_resp = dict(requests.get(es_url + "/movies/" + "_search").json())
    logger.info("ES resp:", es_resp)
    if "error" in es_resp:
        # Если ES возвращает словарь с ошибкой, то создаём индекс
        for scheme in ["movies", "genre", "person"]:
            schema_file = "scheme_{0}.json".format(scheme)
            logger.info("Trying to create an index %s", scheme)
            with open(schema_file, "r") as read_file:
                scheme_json = json.load(read_file)
                requests.put(
                    es_url + "/{0}/".format(scheme),
                    headers={"Content-Type": "application/json"},
                    json=scheme_json,
                )
                logger.info("Created schema for %s", scheme)


es = Elasticsearch(settings.ES_URL)


@backoff.on_exception(backoff.expo, elasticsearch.exceptions.ConnectionError)
def load_to_es(data, index="movies"):
    esinfo = helpers.bulk(es, gen_for_esbulk(data, index))
    logger.info("Loaded %s objects in %s", esinfo[0], index)
    return esinfo
