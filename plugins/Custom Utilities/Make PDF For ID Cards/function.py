import json
from io import BytesIO
from os import startfile
from pathlib import Path
from base64 import b64encode
from tkinter import messagebox
import xml.etree.ElementTree as ET

from requests import get
from svglib.svglib import svg2rlg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics import renderPDF


def driver(folders: list[str] = [], params: str = ""):
    for folder in folders:
        try:
            main(folder, json.loads(params))
        except Exception as e:
            messagebox.showerror("Error", str(e))


TEMPLATE_PATH = Path(__file__).parent / "cache"
if not TEMPLATE_PATH.exists():
    TEMPLATE_PATH.mkdir(exist_ok=True)


def svg_to_pdf(svg_files, output_file_path):
    c = canvas.Canvas(str(output_file_path), pagesize=A4)
    drawings = [svg2rlg(BytesIO(file)) for file in svg_files]
    for drawing in drawings:
        renderPDF.draw(drawing, c, 0, 0)
        c.showPage()
    c.save()


def get_file_from_figma(figma_api_key, file_id, format, frame="0:1"):
    if figma_api_key is None:
        messagebox("Error", "figma_api_key not found")
        exit(1)
    response = get(get(f"https://api.figma.com/v1/images/{file_id}/", params={"ids": frame, "format": format, "svg_outline_text": "false"}, headers={"X-Figma-Token": figma_api_key}).json()["images"]["0:1"])
    return response.content


def convert_rect_to_image(svg_file_path, image_file_path):
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(svg_file_path)
    root = tree.getroot()
    root.attrib.update({"xmlns:xlink": "http://www.w3.org/1999/xlink"})
    for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
        if rect.attrib.get("height") == "842" and rect.attrib.get("width") == "595":
            continue
        image = ET.Element("image")
        image.attrib.update(rect.attrib)
        image.attrib.pop("fill", None)
        image.attrib.update(
            {
                # "xlink:href": image_file_path,
                "xlink:href": f"data:image/jpeg;base64,{b64encode(open(image_file_path, 'rb').read()).decode('utf-8')}",
                "preserveAspectRatio": "none",
            }
        )
        root.append(image)

    return ET.tostring(root)


def main(file_path, params):
    CWD = Path(file_path)
    if not (CWD / "front.jpg").exists() or not (CWD / "back.jpg").exists():
        raise FileNotFoundError("front.jpg or back.jpg not found in the folder")
    if not (TEMPLATE_PATH / "id_card_template.svg").exists():
        file = get_file_from_figma(params["figma_api_key"], params["id_card_file_code"], "svg")
        open(TEMPLATE_PATH / "id_card_template.svg", "wb").write(file)
    else:
        file = open(TEMPLATE_PATH / "id_card_template.svg", "rb").read()
    correctedSvg = {
        "front": convert_rect_to_image(BytesIO(file), CWD / "front.jpg"),
        "back": convert_rect_to_image(BytesIO(file), CWD / "back.jpg"),
    }

    output_file_path = CWD / "id_card.pdf"
    svg_to_pdf([correctedSvg["front"], correctedSvg["back"]], output_file_path)
    startfile(output_file_path)


if __name__ == "__main__":
    driver(["."])
