import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv
from f_icon import create_icon

ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=ROOT / ".env")


plugin_info = {
    "title": "Movie Thumbnails",
    "description": "Create thumbnails for movies",
    "type": ["DIRECTORY_BACKGROUND", "DIRECTORY"],
    "menu_name": "abd Utils",
}


def get_movie_poster(movie_name):
    params = {
        "query": movie_name,
        "api_key": os.getenv("TMDB_API_KEY"),
    }
    response = requests.get("https://api.themoviedb.org/3/search/movie", params=params).json()
    if not response["results"]:
        return None
    return requests.get("https://image.tmdb.org/t/p/w500" + response["results"][0]["poster_path"]).content  # backdrop = backdrop_path


def get_movies(folder_path) -> dict[Path, tuple[str, str]]:
    folder = Path(folder_path)
    movies = {}
    for path in folder.iterdir():
        if path.is_dir():
            if re.match(r".*?(\d{4})", path.name):
                match = re.match(r"^(.*?)[\s(]?(\d{4})", path.name)
                if match:
                    name, year = match.groups()
                    name = name.strip(" ([")
                    movies[path] = (name, year)
            else:
                movies[path] = (path.name, "")
    return movies


def driver(folders, params):
    folder_path = folders[0]
    movies = get_movies(folder_path)
    for path, movie in movies.items():
        if (path / "poster.ico").exists():
            continue
        if poster := get_movie_poster(movie[0]):
            with open(path / "poster.jpg", "wb") as f:
                f.write(poster)
            create_icon(str(path / "poster.jpg"), str(path))
            os.remove(path / "poster.jpg")
        else:
            print(f"Failed to get poster for {movie[0]}")
            continue


if __name__ == "__main__":
    driver(["."], {})
