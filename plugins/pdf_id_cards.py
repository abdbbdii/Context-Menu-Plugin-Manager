import xml.etree.ElementTree as ET
from io import BytesIO
from base64 import b64encode
import os, requests
from dotenv import load_dotenv
from tkinter import messagebox

from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

plugin_info = {
    "title": "Make PDF For ID Cards",
    "description": "Make PDF For ID Cards from figma design",
    "type": ["DIRECTORY_BACKGROUND"],
    "manu_name": "abd Utils",
}


def driver(folders, params):
    for folder in folders:
        try:
            main(folder)
        except Exception as e:
            messagebox.showerror("Error", str(e))


cwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
load_dotenv(dotenv_path=os.path.join(cwd, ".env"))


def svg_to_pdf(svg_file1, svg_file2, pdf_file):
    drawing1 = svg2rlg(svg_file1)
    drawing2 = svg2rlg(svg_file2)
    c = canvas.Canvas(pdf_file, pagesize=A4)
    renderPDF.draw(drawing1, c, 0, 0)
    c.showPage()
    renderPDF.draw(drawing2, c, 0, 0)
    c.showPage()
    c.save()
    os.startfile(pdf_file)


def get_file_from_figma(file_id, format):
    response = requests.get(requests.get(f"https://api.figma.com/v1/images/{file_id}/", params={"ids": "0:1", "format": format}, headers={"X-Figma-Token": os.getenv("FIGMA_API_KEY")}).json()["images"]["0:1"])
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


def main(file_path):
    if not os.path.exists(os.path.join(file_path, "front.jpg")) or not os.path.exists(os.path.join(file_path, "back.jpg")):
        raise FileNotFoundError("front.jpg or back.jpg not found in the folder")
    if not os.path.exists(os.path.join(cwd, "id_card_template.svg")):
        file = get_file_from_figma("mOlDFFrDYUrhUcqQFGPaVV", "svg")
        open(os.path.join(cwd, "id_card_template.svg"), "wb").write(file)
    else:
        file = open(os.path.join(cwd, "id_card_template.svg"), "rb").read()
    correctedSvg = {
        "front": convert_rect_to_image(BytesIO(file), os.path.join(file_path, "front.jpg")),
        "back": convert_rect_to_image(BytesIO(file), os.path.join(file_path, "back.jpg")),
    }
    svg_to_pdf(BytesIO(correctedSvg["front"]), BytesIO(correctedSvg["back"]), os.path.join(file_path, "id_card.pdf"))


if __name__ == "__main__":
    main("")
