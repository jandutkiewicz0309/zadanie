import os
import openai
import logging
from typing import Optional
from dotenv import load_dotenv
import argparse

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_article(file_path: str) -> Optional[str]:
    """Load the article content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None

def generate_html(article_text: str) -> Optional[str]:
    """Send the article to OpenAI API and generate HTML."""
    if not article_text:
        logging.warning("No article text provided.")
        return None

    prompt = (
        "Przekształć poniższy artykuł na kod HTML, spełniając następujące wytyczne:\n"
        "1. Użyj odpowiednich tagów HTML do strukturyzacji treści.\n"
        "2. Wskaż miejsca na obrazki za pomocą <img src='image_placeholder.jpg' alt='prompt do grafiki'>.\n"
        "3. Dodaj podpisy pod obrazkami w tagach <figcaption>.\n"
        "4. Zwróć wyłącznie zawartość pomiędzy <body> i </body>, bez dodatkowych tagów <html>, <head> ani <body>.\n\n"
        "Treść artykułu:\n\n" + article_text
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        html_content = response['choices'][0]['message']['content'].strip()
        logging.info("HTML content successfully generated.")
        return html_content
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        return None

def save_to_file(file_path: str, content: str) -> None:
    """Save content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logging.info(f"File saved: {file_path}")
    except Exception as e:
        logging.error(f"Error saving file {file_path}: {e}")

def validate_html(html_content: str) -> bool:
    """Basic validation to check if the generated HTML meets the requirements."""
    required_tags = ["<img", "alt=", "<figcaption>"]
    if all(tag in html_content for tag in required_tags):
        logging.info("HTML content validation passed.")
        return True
    else:
        logging.warning("HTML content validation failed.")
        return False

def generate_template(template_path: str) -> None:
    """Generate an empty HTML template."""
    template_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Podgląd artykułu</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
                padding: 20px;
                background-color: #f4f4f9;
                color: #333;
            }
            h1, h2 {
                color: #444;
            }
            img {
                max-width: 100%;
                height: auto;
            }
            figure {
                text-align: center;
                margin: 20px 0;
            }
            figcaption {
                font-size: 0.9em;
                color: #555;
            }
        </style>
    </head>
    <body>
        <!-- Miejsce na wklejenie artykułu -->
    </body>
    </html>
    """
    save_to_file(template_path, template_content.strip())

def generate_preview(template_path: str, article_html: str, output_path: str) -> None:
    """Combine the template and article HTML to create a preview."""
    try:
        with open(template_path, 'r', encoding='utf-8') as template_file:
            template = template_file.read()

        full_html = template.replace(
            "<!-- Miejsce na wklejenie artykułu -->", article_html
        )

        save_to_file(output_path, full_html)
    except Exception as e:
        logging.error(f"Error generating preview: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate HTML from article using OpenAI API.")
    parser.add_argument("--input", default="artykul.txt", help="Path to the input text file.")
    parser.add_argument("--output_html", default="artykul.html", help="Path to the output HTML file.")
    parser.add_argument("--template", default="szablon.html", help="Path to the HTML template file.")
    parser.add_argument("--preview", default="podglad.html", help="Path to the preview HTML file.")
    args = parser.parse_args()

    logging.info("Loading article...")
    article_text = load_article(args.input)
    if not article_text:
        logging.error("No article content found. Exiting.")
        return
    
    logging.info("Generating HTML...")
    html_content = generate_html(article_text)
    if not html_content or not validate_html(html_content):
        logging.error("HTML generation failed or validation failed. Exiting.")
        return
    
    logging.info("Saving generated HTML...")
    save_to_file(args.output_html, html_content)
    
    logging.info("Generating HTML template...")
    generate_template(args.template)
    
    logging.info("Generating article preview...")
    generate_preview(args.template, html_content, args.preview)
    
    logging.info(f"Process complete! Files saved:\n - {args.output_html}\n - {args.template}\n - {args.preview}")

if __name__ == "__main__":
    main()
