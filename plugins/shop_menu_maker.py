import requests, os, json
from dotenv import load_dotenv
from io import BytesIO
from tkinter import messagebox, filedialog

from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

plugin_info = {
    "title": "Make Shop Menu",
    "description": "Make Shop Menu from figma design",
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


def get_file_from_figma(file_id, format):
    response = requests.get(requests.get(f"https://api.figma.com/v1/images/{file_id}/", params={"ids": "0:1", "format": format, "svg_outline_text": "false"}, headers={"X-Figma-Token": os.getenv("FIGMA_API_KEY")}).json()["images"]["0:1"])
    return response.content


def replace_text(file, dict_of_replacements):
    for key, value in dict_of_replacements.items():
        file = file.decode().replace(key, str(value) if value else "").encode()
    return file


def svg_to_pdf(svg_file, pdf_file):
    d = svg2rlg(BytesIO(svg_file))
    c = canvas.Canvas(pdf_file, pagesize=A4)
    renderPDF.draw(d, c, 0, 0)
    c.showPage()
    c.save()
    os.startfile(pdf_file)


def main(file_path):
    if not os.path.exists(os.path.join(cwd, "svg_templates", "shop_menu_template.svg")):
        file = get_file_from_figma("jEri2nQqWrng6rRge6v2Sv", "svg")
        open(os.path.join(cwd, "svg_templates", "shop_menu_template.svg"), "wb").write(file)
    else:
        file = open(os.path.join(cwd, "svg_templates", "shop_menu_template.svg"), "rb").read()
    if os.path.exists(os.path.join(file_path, "shop_menu.json")):
        json_file = json.loads(open(os.path.join(file_path, "shop_menu.json"), "r").read())
    else:
        json_file = json.loads(open(filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON Files", "*.json")]), "r").read())
    file = replace_text(file, json_file)
    svg_to_pdf(file, os.path.join(file_path, "shop_menu.pdf"))


if __name__ == "__main__":
    main("")
