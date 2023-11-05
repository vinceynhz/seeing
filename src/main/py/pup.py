import logging

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from graph import fibonacci_sphere, swatches
from taxonomy import Taxonomy

from mitre import attack

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d - %(levelname)s [%(name)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

templates = Jinja2Templates(directory='templates')


class Puppy(object):
    def __init__(self, taxonomy: Taxonomy):
        self.log = logging.getLogger("pup.py")
        self.taxonomy = taxonomy

    def start(self):
        self.log.info("Initializing taxonomy")
        self.taxonomy.start()
        self.log.info("Taxonomy started")

    async def get_organisms(self, request):
        return JSONResponse(self.taxonomy.organisms())

    async def get_domains(self, request):
        return JSONResponse(self.taxonomy.domains())

    async def get_families(self, request):
        family_id = request.path_params['family_id'] if 'family_id' in request.path_params else None
        return JSONResponse(self.taxonomy.families(family_id=family_id))

    async def get_graph(self, request):
        self.log.info(f"Building graph for organism {request.path_params['organism_id']}")
        classified_organism = self.taxonomy.classify(request.path_params['organism_id'])
        classification_colors = swatches(len(classified_organism))

        for index, classification in enumerate(classified_organism):
            orbit = (index + 1) * 5
            classification['family']['color'] = classification_colors[index]
            classification['family']['orbit'] = orbit
            points = fibonacci_sphere(len(classification['species']), scale=orbit)
            for point_index, species in enumerate(classification['species']):
                species["pos"] = points[point_index]
        return JSONResponse(classified_organism)


async def homepage(request):
    return templates.TemplateResponse(request, 'index.html')


puppy = Puppy(attack.AttackMatrix())

routes = [
    Route('/', endpoint=homepage),
    Route('/data/domains', endpoint=puppy.get_domains),
    Route('/data/organisms', endpoint=puppy.get_organisms),
    Route('/data/families', endpoint=puppy.get_families),
    Route('/data/families/{family_id:str}', endpoint=puppy.get_families),
    Route('/graph/{organism_id:str}', endpoint=puppy.get_graph),
    Mount('/static', StaticFiles(directory='static'), name='static')
]

app = Starlette(debug=True, routes=routes, on_startup=[puppy.start])
