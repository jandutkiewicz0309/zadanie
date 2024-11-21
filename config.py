from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def load_article(file_path):
    """Wczytuje artykuł z pliku tekstowego."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Błąd: Plik {file_path} nie został znaleziony.")
        return None


def generate_html(article_text):
    """Wysyła artykuł do OpenAI w celu wygenerowania kodu HTML."""
    if not article_text:
        print("Nie podano treści artykułu.")
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
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"Błąd podczas komunikacji z API OpenAI: {e}")
        return None


def save_html(output_path, html_content):
    """Zapisuje kod HTML do pliku."""
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku: {e}")


def generate_template(template_path):
    """Generuje pusty szablon HTML."""
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
    try:
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(template_content.strip())
        print(f"Szablon zapisano w pliku {template_path}")
    except Exception as e:
        print(f"Błąd podczas generowania szablonu: {e}")


def generate_preview(template_path, article_html, output_path):
    """Łączy szablon z wygenerowanym artykułem i zapisuje jako pełny podgląd."""
    try:
        with open(template_path, 'r', encoding='utf-8') as template_file:
            template = template_file.read()

        full_html = template.replace(
            "<!-- Miejsce na wklejenie artykułu -->", article_html
        )

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(full_html)
        print(f"Podgląd zapisano w pliku {output_path}")
    except Exception as e:
        print(f"Błąd podczas generowania podglądu: {e}")


def main():
    input_file = "artykul.txt"
    article_output_file = "artykul.html"
    template_file = "szablon.html"
    preview_file = "podglad.html"
    
    print("Wczytywanie artykułu...")
    article_text = load_article(input_file)
    if not article_text:
        print("Przerwano działanie programu z powodu braku treści artykułu.")
        return
    
    print("Generowanie kodu HTML...")
    html_content = generate_html(article_text)
    if not html_content:
        print("Nie udało się wygenerować kodu HTML.")
        return
    
    print("Zapisywanie wygenerowanego HTML...")
    save_html(article_output_file, html_content)
    
    print("Generowanie szablonu HTML...")
    generate_template(template_file)
    
    print("Generowanie podglądu artykułu...")
    generate_preview(template_file, html_content, preview_file)
    
    print(f"Zakończono! Pliki zapisane:\n - {article_output_file}\n - {template_file}\n - {preview_file}")


if __name__ == "__main__":
    main()
