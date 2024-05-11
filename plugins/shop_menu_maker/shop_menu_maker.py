from requests import get
from os import startfile, getenv
import json
from dotenv import load_dotenv
from io import BytesIO
from tkinter import messagebox
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

plugin_info = {
    "title": "Make Shop Menu",
    "description": "Make Shop Menu from figma design",
    "type": ["FILES"],
    "menu_name": "abd Utils",
}


def driver(files, params):
    for file in files:
        try:
            main(file)
        except Exception as e:
            messagebox.showerror("Error", str(e))


ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=ROOT / ".env")
TEMPLATE_PATH = ROOT / "assets" / "templates"


def get_file_from_figma(file_id, format, frame="0:1"):
    response = get(get(f"https://api.figma.com/v1/images/{file_id}/", params={"ids": frame, "format": format, "svg_outline_text": "false"}, headers={"X-Figma-Token": getenv("FIGMA_API_KEY")}).json()["images"]["0:1"])
    return response.content


def svg_to_pdf(svg_files, output_file_path):
    c = canvas.Canvas(output_file_path, pagesize=A4)
    drawings = [svg2rlg(BytesIO(file)) for file in svg_files]
    for drawing in drawings:
        renderPDF.draw(drawing, c, 0, 0)
        c.showPage()
    c.save()


def main(file_path):
    figma_file_ids = {
        "small": "jEri2nQqWrng6rRge6v2Sv",
        "large": "jEri2nQqWrng6rRge6v2Sv",
    }
    json_file = json.loads(open(file_path, "r").read())
    CWD = Path(file_path).parent

    for key, value in figma_file_ids.items():
        if not Path(TEMPLATE_PATH / f"shop_menu_template_{key}.svg").exists():
            file = get_file_from_figma(value, "svg")
            open(TEMPLATE_PATH / f"shop_menu_template_{key}.svg", "wb").write(file)
    for key in figma_file_ids.keys():
        file = open(TEMPLATE_PATH / f"shop_menu_template_{key}.svg", "rb").read()
        for key_, value in json_file.items():
            file = file.decode().replace(key_, str(value) if value else "").encode()
        svg_to_pdf([file], CWD / f"shop_menu_{key}.pdf")
        startfile(CWD / f"shop_menu_{key}.pdf")

    # doing for flex
    if not Path(TEMPLATE_PATH / f"shop_menu_template_flex.svg").exists():
        flex_file = get_file_from_figma("5zRMQEXHL0SMV1rDZuRCWK", "svg")
        open(TEMPLATE_PATH / f"shop_menu_template_flex.svg", "wb").write(flex_file)
    flex_file = open(TEMPLATE_PATH / f"shop_menu_template_flex.svg", "rb").read()

    data = []
    files = []
    vals = list(filter(lambda x: x is not None, json_file.values()))
    l = []
    for a in vals:
        l.append(a)
        if len(l) == 3:
            data.append({f":0{i+1}": l[i] for i in range(len(l))})
            l = []
    data.append({f":{'{:02d}'.format(i+1)}": l[i] for i in range(len(l))})

    for group_data in data:
        file_ = flex_file.decode()
        for key_, value in group_data.items():
            file_ = file_.replace(key_, str(value))
        files.append(file_.encode())

    svg_to_pdf(files, CWD / f"shop_menu_flex.pdf")
    startfile(CWD / f"shop_menu_flex.pdf")


if __name__ == "__main__":
    main("")
