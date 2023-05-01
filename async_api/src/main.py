import aioredis
from api.v1 import films, genre, person
from core.config import settings
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import set_span_in_context
from tracer import configure_tracer

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

FastAPIInstrumentor.instrument_app(app)


@app.on_event("startup")
async def startup():
    configure_tracer()

    redis.redis = await aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis.redis), prefix="fastapi-cache")

    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}://{settings.elastic_host}:{settings.elastic_port}"
        ]
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()


@app.middleware("http")
async def check_header(request: Request, call_next):
    if settings.enable_before_request:
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            raise HTTPException(status_code=400, detail="Request id is required")

    request.state.request_id = request_id
    if settings.enable_tracer:
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(
            "http_request", attributes={"http.request_id": request_id}
        ) as span:
            token = attach(set_span_in_context(span))
            response = await call_next(request)
            detach(token)

    response = await call_next(request)
    return response


app.include_router(films.router, prefix="/api/v1/films")
app.include_router(genre.router, prefix="/api/v1/genre")
app.include_router(person.router, prefix="/api/v1/person")
