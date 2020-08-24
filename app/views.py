import asyncio

import log
from sanic import Sanic, response

from app import api, helpers, models, settings, utils

app = Sanic(name="memegen")

app.config.SERVER_NAME = settings.SERVER_NAME
app.config.API_SCHEMES = settings.API_SCHEMES
app.config.API_VERSION = "6.0a1"
app.config.API_TITLE = "Memes API"


app.blueprint(api.images.blueprint)
app.blueprint(api.templates.blueprint)
app.blueprint(api.docs.blueprint)


@app.get("/")
@api.docs.exclude
async def index(request):
    return response.redirect("/docs")


@app.get("/samples")
@api.docs.exclude
async def samples(request):
    loop = asyncio.get_event_loop()
    samples = await loop.run_in_executor(None, helpers.get_sample_images, request)
    urls = [sample[0] for sample in samples]
    refresh = "debug" in request.args and settings.DEBUG
    content = utils.html.gallery(urls, refresh=refresh)
    return response.html(content)


@app.get("/test")
@api.docs.exclude
async def test(request):
    if not settings.DEBUG:
        return response.redirect("/")
    loop = asyncio.get_event_loop()
    urls = await loop.run_in_executor(None, helpers.get_test_images, request)
    content = utils.html.gallery(urls, refresh=True)
    return response.html(content)


@app.get("/test/<template_key>/<text_paths:path>")
@api.docs.exclude
async def test_image(request, template_key, text_paths):
    if not settings.DEBUG:
        return response.redirect("/")
    template = models.Template.objects.get_or_create(template_key)
    template.datafile.save()
    url = f"/images/{template_key}/{text_paths}.png"
    content = utils.html.gallery([url], refresh=True, rate=1.0)
    return response.html(content)


if __name__ == "__main__":
    log.silence("asyncio", "datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
        access_log=False,
    )
