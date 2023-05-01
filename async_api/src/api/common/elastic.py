from typing import Dict


def get_pagination(page_size_, page_number_):
    return (page_number_ - 1) * page_size_


def get_body(
    query_: str, from_: int, size_: int, sort_by_: str | None, sort_order_: str | None
) -> Dict:
    result = {
        "query": {"bool": {"must": [{"multi_match": {"query": query_}}]}},
        "from": from_,
        "size": size_,
    }

    if all([sort_by_, sort_order_]):
        result["sort"] = [{sort_by_: {"order": sort_order_}}]

    return result
