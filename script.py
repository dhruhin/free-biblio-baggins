import sys
from ebooklib import epub
from bs4 import BeautifulSoup
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def find_bibliography_hrefs(book):
    """
    Identify chapters related to bibliographies in the table of contents of an EPUB book.

    Args:
        book (epub.EpubBook): The EPUB book object.

    Returns:
        list: A list of hrefs corresponding to bibliography-related chapters.
    """
    # List of common titles for bibliography sections
    bibliography_titles = [
        "bibliography", "references", "works cited", "further reading",
        "related works", "additional reading", "sources", "literature cited",
        "reference list", "citations", "selected bibliography", "recommended reading"
    ]

    # Normalize titles for case-insensitive comparison
    bibliography_titles = [title.lower() for title in bibliography_titles]

    # Initialize a list to store hrefs of bibliography-related chapters
    bibliography_hrefs = []

    # Recursive function to traverse the table of contents
    def traverse_toc(items):
        for item in items:
            if isinstance(item, epub.Link):
                # Normalize the item title for comparison
                item_title = item.title.lower()
                # Check if the item title matches any bibliography title
                if item_title in bibliography_titles:
                    bibliography_hrefs.append(item.href)
            elif isinstance(item, epub.Section):
                # Recursively traverse subitems in sections
                traverse_toc(item.subitems)

    # Start traversing the table of contents
    traverse_toc(book.toc)

    return bibliography_hrefs

def extract_text_from_hrefs(book, hrefs, tags=['p']):
    """
    Extracts and returns the text content from specified tags within the given hrefs in the EPUB book.

    Args:
        book (epub.EpubBook): The EPUB book object.
        hrefs (list): A list of href strings corresponding to the desired chapters.
        tags (list, optional): A list of HTML tag names to extract text from. Defaults to ['p'].

    Returns:
        dict: A dictionary with hrefs as keys and extracted text content as values.
    """
    extracted_texts = {}

    for href in hrefs:
        # Fetch the item using its href
        item = book.get_item_with_href(href)
        if item:
            # Get the raw HTML content
            content = item.get_content()
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            # Extract text from the specified tags
            texts = []
            for tag in tags:
                for element in soup.find_all(tag):
                    texts.append(element.get_text(strip=True))
            # Join the extracted texts with newlines
            extracted_texts[href] = '\n'.join(texts)
        else:
            print(f"Item with href '{href}' not found in the book.")

    return extracted_texts

# Main function
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_epub>")
        sys.exit(1)

    epub_path = sys.argv[1]


    try:
        # Load the EPUB file
        book = epub.read_epub(epub_path, options={'ignore_ncx': True})

        # save_chapters(book, output_dir)
        refs = find_bibliography_hrefs(book)

        # Extract text from the specified hrefs
        extracted_texts = extract_text_from_hrefs(book, refs)

        # Print the extracted texts
        for href, text in extracted_texts.items():
            if len(extracted_texts) == 1:
                print(text)
            else:
                print(f"Text from {href}:\n{text}\n")


    except Exception as e:
        print(f"An error occurred: {e}")

# Unused functions, just leaving for reference

# def print_table_of_contents(book):
#     # Access the table of contents
#     toc = book.toc

#     # Function to recursively print the ToC
#     def print_toc(items, indent=0):
#         for item in items:
#             if isinstance(item, epub.Link):
#                 print(' ' * indent + f'Title: {item.title}, Href: {item.href}')
#             elif isinstance(item, epub.Section):
#                 print(' ' * indent + f'Section: {item.title}')
#                 print_toc(item.subitems, indent + 2)
#             else:
#                 print(' ' * indent + 'Unknown item type')

#     # Print the ToC
#     print_toc(toc)

# # Function to extract table of contents
# def extract_table_of_contents(book):
#     # Iterate through all items in the book
#     for item in book.get_items():
#         # Check if the item is a document (likely a chapter)
#         if item.get_type() == ebooklib.ITEM_DOCUMENT:
#             # Get the content of the item
#             content = item.get_content()
#             # Parse the HTML content using BeautifulSoup
#             soup = BeautifulSoup(content, 'html.parser')
#             # Find the title tag
#             title_tag = soup.find('title')
#             # Extract and print the title text if the title tag exists
#             if title_tag:
#                 print(f'Chapter Title: {title_tag.string}')
#             else:
#                 print('Chapter Title: Untitled')

# def save_chapters(book, output_dir):
#     # Ensure the output directory exists
#     os.makedirs(output_dir, exist_ok=True)

#     # Iterate through all items in the book
#     for item in book.get_items():
#         # Check if the item is a document (likely a chapter)
#         if item.get_type() == ebooklib.ITEM_DOCUMENT:
#             # Use the item's file name for the output file
#             output_path = os.path.join(output_dir, item.file_name)
#             # Ensure the subdirectory exists
#             os.makedirs(os.path.dirname(output_path), exist_ok=True)
#             # Write the content to the output file
#             with open(output_path, 'wb') as f:
#                 f.write(item.get_content())
#             print(f'Saved {item.file_name} to {output_path}')
