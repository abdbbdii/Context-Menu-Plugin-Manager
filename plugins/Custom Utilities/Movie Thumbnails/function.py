import os
import re
import json
from pathlib import Path

import requests
from f_icon import create_icon

def get_movie_poster(api_key, movie_name, year, type="movie"):
    params = {
        "query": movie_name,
        "api_key": api_key,
    }
    response = requests.get(f"https://api.themoviedb.org/3/search/{type}", params=params).json()
    date_key = "first_air_date" if type == "tv" else "release_date"
    name_key = "name" if type == "tv" else "original_title"
    if response["results"]:
        if year:
            found = []
            for result in response["results"]:
                if result[date_key].startswith(year):
                    found.append(result)
                    print(f"{len(found)}: {result[name_key]} ({result[date_key]})")
            if len(found) == 1:
                return requests.get("https://image.tmdb.org/t/p/w500" + found[0]["poster_path"]).content
            elif len(found) > 1:
                option = input(f"Select the correct movie for {movie_name} ({year}): ")
                return requests.get("https://image.tmdb.org/t/p/w500" + found[int(option) - 1]["poster_path"]).content
        return requests.get("https://image.tmdb.org/t/p/w500" + response["results"][0]["poster_path"]).content  # backdrop = backdrop_path


def get_movies(folder_path) -> dict[Path, tuple[str, str]]:
    folder = Path(folder_path)
    movies = {}
    for path in folder.iterdir():
        if path.is_dir():
            path_name = path.name.replace(".", " ")
            if re.match(r".*?(\d{4})", path_name):
                match = re.match(r"^(.*?)[\s(]?(\d{4})", path_name)
                if match:
                    name, year = match.groups()
                    name = name.strip(" ([")
                    movies[path] = (name, year)
            else:
                movies[path] = (path_name, "")
    return movies


def driver(items: list[str] = [], params: str = ""):
    folder_path = items[0]
    movies = get_movies(folder_path)
    for path, movie in movies.items():
        if (path / "poster.ico").exists():
            continue
        if poster := get_movie_poster(json.loads(params)["tmdb_api_key"], movie[0], movie[1], "movie" if not is_tv(path, movie[0]) else "tv"):
            with open(path / "poster.jpg", "wb") as f:
                f.write(poster)
            create_icon(str(path / "poster.jpg"), str(path))
            os.remove(path / "poster.jpg")
        else:
            print(f"Failed to get poster for {movie[0]}")
            continue


def is_tv(folder_path: Path | str, name: str):
    files_found = 0
    folder = Path(folder_path)
    for path in folder.iterdir():
        path_name = path.name.replace(".", " ")
        if not path.is_dir() and (path_name.startswith(name)) and not path.name.endswith(".srt"):
            files_found += 1
            if files_found > 1:
                return True

    return False


if __name__ == "__main__":
    driver(["."])
