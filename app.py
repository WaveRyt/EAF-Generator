import os
import uuid
import subprocess
from datetime import datetime
from flask import Flask, request, send_file, render_template, redirect, flash, session, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from docx import Document
from PIL import Image
from num2words import num2words
import shutil
from flask_dance.contrib.google import make_google_blueprint, google

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
TEMPLATE_DOCX = os.path.join(BASE_DIR, "EAF_Template.docx")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB

# Flask setup
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-this")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed emails from env
ALLOWED_EMAILS = os.environ.get("ALLOWED_EMAILS", "").split(",")
ALLOWED_EMAILS = [email.strip() for email in ALLOWED_EMAILS if email.strip()]

# Google OAuth setup (updated scopes!)
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_url="/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")


# === UTILITIES ===
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def number_to_words(amount):
    try:
        amt_int = int(float(amount))
    except Exception:
        return ""
    try:
        words = num2words(amt_int, lang="en_IN")
    except Exception:
        words = num2words(amt_int)
    return words.replace("-", " ").title() + " Rupees Only"


def replace_placeholders_in_docx(doc: Document, mapping: dict):
    def replace_in_paragraph(paragraph):
        for run in paragraph.runs:
            for key, val in mapping.items():
                if key in run.text:
                    run.text = run.text.replace(key, val)

    for para in doc.paragraphs:
        replace_in_paragraph(para)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    replace_in_paragraph(para)
    for section in doc.sections:
        for para in section.header.paragraphs:
            replace_in_paragraph(para)
        for table in section.header.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        replace_in_paragraph(para)
        for para in section.footer.paragraphs:
            replace_in_paragraph(para)
        for table in section.footer.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        replace_in_paragraph(para)


def generate_eaf_docx(template_path, out_docx_path, date_str, amount, amount_words, remarks,
                      acc_number="", acc_holder="", bank_name="", ifsc="", branch=""):
    doc = Document(template_path)
    mapping = {
        "{{DATE}}": date_str,
        "{{TOTAL_AMOUNT}}": str(amount),
        "{{TOTAL_AMOUNT_WORDS}}": amount_words,
        "{{Remarks}}": remarks,
        "{{ACCOUNT_NUMBER}}": acc_number,
        "{{ACCOUNT_HOLDER}}": acc_holder,
        "{{BANK_NAME}}": bank_name,
        "{{IFSC}}": ifsc,
        "{{BRANCH}}": branch
    }
    replace_placeholders_in_docx(doc, mapping)
    doc.save(out_docx_path)
    return out_docx_path


def convert_docx_to_pdf(docx_path, pdf_path):
    outdir = os.path.dirname(pdf_path)
    possible_paths = [
        "/usr/bin/libreoffice",
        "/usr/bin/soffice",
        shutil.which("libreoffice"),
        shutil.which("soffice")
    ]
    soffice_path = next((p for p in possible_paths if p and os.path.exists(p)), None)
    if not soffice_path:
        raise RuntimeError("LibreOffice not found. Install it in Dockerfile or system.")

    subprocess.run(
        [soffice_path, "--headless", "--convert-to", "pdf:writer_pdf_Export", "--outdir", outdir, docx_path],
        check=True
    )

    generated_pdf = os.path.join(outdir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
    if generated_pdf != pdf_path:
        os.replace(generated_pdf, pdf_path)

    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF conversion failed")

    return pdf_path


# === ROUTES ===
@app.route("/login")
def login():
    # If not authorized, send to Google login
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Get user info from Google
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Google login failed. Please try again.")
        return redirect(url_for("google.login"))

    data = resp.json()
    email = data.get("email")

    if not email or (ALLOWED_EMAILS and email not in ALLOWED_EMAILS):
        flash("Access denied: your email is not allowed.")
        session.clear()
        return redirect(url_for("login"))

    # Save email in session
    session["user_email"] = email
    return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    user_email = session.get("user_email")

    if not user_email:
        flash("Please log in first.")
        return redirect(url_for("login"))

    # Example: handle form submission or show dashboard
    if request.method == "POST":
        # TODO: handle upload & PDF generation here
        flash("Your file has been processed.")
        return redirect(url_for("uploaded_file", filename="example.pdf"))

    return render_template("index.html", user_email=user_email)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found.")
        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
