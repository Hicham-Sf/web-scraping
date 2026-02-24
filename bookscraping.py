from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time  # Good practice to add delays [cite: 354]

# 1. FIX: Use the correct URL for this logic [cite: 158, 177]
url = 'https://books.toscrape.com/'
rmap = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5} 
book_list = []

for page in range(1, 3):
    if page == 1:
        page_url = url
    else:
        page_url = f"{url}catalogue/page-{page}.html"
    
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser') 
    
    # Find all book containers on the page [cite: 208, 210]
    books = soup.find_all('article', class_='product_pod')

    # 2. FIX: This loop MUST be indented to process books for EACH page
    for book in books:
        if len(book_list) >= 30:
            break

        # Basic Info Extraction [cite: 222, 224, 238]
        title = book.h3.a['title']
        price_text = book.find('p', class_='price_color').text
        price = float(price_text[2:]) # Skip the £ symbol [cite: 236]
        rating_class = book.find('p', class_='star-rating')['class'][1]
        rating = rmap.get(rating_class, 0)

        # 3. FIX: Detail Extraction MUST be inside the loop to get info for every book
        link = book.h3.a['href'] 
        if 'catalogue/' not in link:
            link = 'catalogue/' + link 
        detail_url = url + link 

        detail_response = requests.get(detail_url)
        detail_soup = BeautifulSoup(detail_response.text, 'html.parser') 

        # Extract Stock [cite: 272, 273]
        stock_tag = detail_soup.find('p', class_='instock availability')
        stock = int(re.search(r'\((\d+)', stock_tag.text).group(1)) if stock_tag else 0 

        # Extract Category [cite: 281, 287]
        breadcrumb = detail_soup.find('ul', class_='breadcrumb')
        category = breadcrumb.find_all('li')[2].text.strip() if breadcrumb else "N/A"

        # Extract Description [cite: 290, 298]
        desc_div = detail_soup.find('div', id='product_description')
        description = desc_div.find_next('p').text.strip() if desc_div else "N/A"

        # Append the full data for this book [cite: 330]
        book_list.append({
            'Title': title,
            'Price': price,
            'Stock': stock,
            'Rating': rating,
            'Category': category,
            'Description': description
        })
        
        # Respect the server by waiting briefly [cite: 354]
        time.sleep(0.1)

# 4. Save and Print Results [cite: 331, 332, 333]
book_df = pd.DataFrame(book_list)
book_df.to_csv('books_data.csv', index=False)

print(f"Successfully scraped {len(book_df)} books!")
print("CSV file 'books_data.csv' has been created on your Desktop.")