"""Python 3.14.7 (main, Aug 10 2026, 00:00:00) [GCC 16.1.1 20260515 (Red Hat 16.1.1-2)] on linux"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import random

"""
defs des filles
"""
class Maillon:
    def __init__(self, valeur, suivant=None):
        self.valeur = valeur
        self.suivant = suivant
class FileChainee:
    def __init__(self):
        self.tete = None
        self.queue = None

    def est_vide(self):
        if not self.tete:
            return True
        return False

    def enfiler(self, valeur):
        m = Maillon(valeur)
        if self.est_vide():
            self.queue = m
            self.tete = m
        else:
            self.queue.suivant = m
            self.queue = m

    def defiler(self):
        if self.est_vide():
            raise IndexError("bloup vide pas marcher")
        ot = self.tete
        self.tete = ot.suivant
        if not self.tete:
            self.queue = None
        return ot.valeur

"""
Animaux
"""
class Thon:
    def __init__ (self , x, y, ocean):
        self.x = x
        self.y = y
        self.age_gestation = 0
        self.temps_gestation = 3
        self.ocean = ocean
        self.alive = True

    def to_dict(self):
        return {
            "type": str(self),
            "age_gestation": self.age_gestation,
            "temps_gestation": self.temps_gestation,
        }

    def die(self):
        """tue le thon"""
        self.alive = False

    def __str__(self):
        return "T"

    def agir(self):
        """fait bouger le thon si possible et reproduire"""
        empty_neighbours = []
        for neighbour_x, neighbour_y in self.ocean.get_neighbors(self.x, self.y):
            neighbour = self.ocean.get_place(neighbour_x, neighbour_y)
            if not (type(neighbour) == Thon or type(neighbour) == Requin):
                empty_neighbours.append((neighbour_x, neighbour_y))
        if len(empty_neighbours) > 0:
            old_coord_x, old_coord_y = (self.x, self.y)
            self.ocean.move_entity(self,
                                   *random.choice(empty_neighbours))  # bouge si vide
            if self.age_gestation >= self.temps_gestation:
                self.ocean.spawn_thuna(old_coord_x, old_coord_y)  # reproduction
                self.age_gestation = 0
            else:
                self.age_gestation += 1
class Requin:
    def __init__ (self , x, y, ocean):
        self.x = x
        self.y = y
        self.age_gestation = 0
        self.temps_gestation = 5
        self.energie = 4 # Energie de depart
        self.ocean = ocean
        self.alive = True

    def to_dict(self):
        return {
            "type": str(self),
            "age_gestation": self.age_gestation,
            "temps_gestation": self.temps_gestation,
            "energie": self.energie,
        }

    def die(self):
        """tue le pauvre requin qui a pas pu manger"""
        self.alive = False

    def __str__(self):
        """j'ai vrm besoin de mettre un commentaire là ?"""
        return "R"

    def eat_tuna(self, tuna):
        """fait manger un thon au requin"""
        self.ocean.empty_coords(tuna.x, tuna.y)
        tuna.die()
        self.energie = 4
        self.ocean.move_entity(self, tuna.x, tuna.y)

    def agir(self):
        """fait agir un requin (selon l'énoncé)"""
        if self.energie <= 0:
            self.die()
            self.ocean.empty_coords(self.x, self.y)
            return

        thunas_neighbours = []
        empty_neighbours = []
        for neighbour_x, neighbour_y in self.ocean.get_neighbors(self.x, self.y):
            neighbour = self.ocean.get_place(neighbour_x, neighbour_y)
            if type(neighbour) == Thon:
                thunas_neighbours.append(neighbour)
            elif not type(neighbour) == Requin:
                empty_neighbours.append((neighbour_x, neighbour_y))

        if len(thunas_neighbours) > 0:
            old_coord_x, old_coord_y = (self.x, self.y)
            self.eat_tuna(random.choice(thunas_neighbours)) # mange un thon
            if self.age_gestation >= self.temps_gestation:
                self.ocean.spawn_shark(old_coord_x, old_coord_y) # reproduction
                self.age_gestation = 0
            else:
                self.age_gestation += 1
            return
        elif len(empty_neighbours) > 0:
            old_coord_x, old_coord_y = (self.x, self.y)
            self.ocean.move_entity(self, *random.choice(empty_neighbours)) # bouge si pas de thon (et a un endroirt vide)
            if self.age_gestation >= self.temps_gestation:
                self.ocean.spawn_shark(old_coord_x, old_coord_y) # reproduction
                self.age_gestation = 0
            else:
                self.age_gestation += 1
        self.energie -= 1

"""
Plateau
"""
class Ocean:
    """2D Grid"""
    def __init__(self, scale):
        self.scale = scale
        self.stats = {}
        self.grid = [[0 for i in range(self.scale)] for j in range(self.scale)]
        self.round = 1

    def to_dict(self):
        return {
            "scale": self.scale,
            "round": self.round,
            "stats": self.stats,
            "grid": [[c.to_dict() if c != 0 else None for c in col] for col in self.grid],
        }

    def get_place(self, x, y):
        """récup la valeure d'une case"""
        return self.grid[x][y]

    def get_neighbors(self, x, y):
        """récup la liste des voisins d'une case (avec les tours de la terre)"""
        neighbors = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx = (x + dx) % self.scale
            ny = (y + dy) % self.scale
            neighbors.append((nx, ny))
        return neighbors

    def move_entity(self, entity, x, y):
        """bouge un animal dans une nouvelle case"""
        if self.__in_bounds(x, y) and self.__is_empty_coords(x, y):
            self.grid[entity.x][entity.y] = 0
            self.grid[x][y] = entity
            entity.x = x
            entity.y = y

    def __str__(self):
        """print le plateau"""
        map = ""
        for i in range(self.scale):
            for j in range(self.scale):
                map += f" {str(self.grid[i][j])} "
            map += "\n"
        return map

    def empty_coords(self, x, y):
        """vide une case"""
        self.grid[x][y] = 0

    def spawn_thuna(self, x, y):
        """force l'apparition d'un thon sur une case"""
        if not self.__in_bounds(x, y): return
        self.grid[x][y] = Thon(x, y, self)

    def __in_bounds(self, x, y):
        """vérifie si sur le plateau"""
        return 0 <= x < self.scale and 0 <= y < self.scale

    def spawn_shark(self, x, y):
        """force l'apparition d'un requin sur une case"""
        if not self.__in_bounds(x, y): return
        self.grid[x][y] = Requin(x, y, self)

    def __is_empty_coords(self, x, y):
        """ vérifie si le contenu d'une case par ses coordonées est vide"""
        return self.grid[x][y] == 0

    def __is_empty(self, place):
        """ vérifie si le contenu d'une case est vide"""
        return place == 0

    def next_step(self):
        """fait avancer le jeu d'une étape"""
        # mets les annimaux dans une file et les fait bouger les uns après les autres
        file = FileChainee()
        for column in self.grid:
            for place in column:
                if not self.__is_empty(place):
                    file.enfiler(place)
        while not file.est_vide():
            animal = file.defiler()
            if animal.alive:
                animal.agir()

        # stats
        nmb_tuna = 0
        nmb_shark = 0
        for column in self.grid:
            for place in column:
                if type(place) == Thon:
                    nmb_tuna += 1
                elif type(place) == Requin:
                    nmb_shark += 1
        self.stats[self.round] = {"thons": nmb_tuna, "shark": nmb_shark}
        print(f"Round {self.round} passé. Thons: {nmb_tuna} sharks: {nmb_shark}")
        self.round += 1

# init nouveau oceannnn
def init():
    scale = 10
    ocean = Ocean(scale)
    [ocean.spawn_thuna(random.randint(0, scale-1), random.randint(0, scale-1)) for _ in range(7)]
    [ocean.spawn_shark(random.randint(0, scale-1), random.randint(0, scale-1)) for _ in range(5)]

    return ocean

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=3600,  # Cache preflight response for 1 hour (3600 seconds)
)

ocean = init()

@app.get("/reset")
def reset():
    global ocean
    ocean = init()
    return ocean.to_dict()

@app.get("/next_round")
def next():
    ocean.next_step()
    return ocean.to_dict()


static_dir = Path(__file__).resolve().parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
