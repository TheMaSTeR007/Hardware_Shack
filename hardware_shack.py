import requests, os, gzip, hashlib, json
from lxml import html


def req_sender(url: str, method: str):
    _response = requests.request(method=method, url=url)
    if _response.status_code != 200:
        print(f"HTTP Request Status code: {_response.status_code}")  # HTTP Status code
        return None
    return _response  # Request Successful


def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory {path} created")


def page_checker(url: str, method: str, path: str) -> str:
    page_hash = hashlib.sha256(string=url.encode()).hexdigest()
    file_path = os.path.join(path, f"{page_hash}.html.gz")
    ensure_directory_exists(path)  # Ensure the directory exists
    if os.path.exists(file_path):
        print("Page exists, Reading it...")  # Page exists
        print(f'File name is : {page_hash}')
        with gzip.open(filename=file_path, mode='rb') as file:
            html_text = file.read().decode(errors='backslashreplace')
        return html_text  # Returning String Text of Response
    else:
        print("Page does not exist, Sending Request...")  # Page does not exist
        _response = req_sender(url=url, method=method)  # Sending HTTP Request

        print(f'File name is : {page_hash}')
        if _response is not None:
            with gzip.open(filename=file_path, mode='wb') as file:
                file.write(_response.content)
                print("Page Saved")
            return _response.text  # Returning String Text of Response


def scraper_func(url: str, method: str, path: str):
    html_response_text = page_checker(url=url, method=method, path=path)  # Get Http response Text

    parsed_html = html.fromstring(html=html_response_text)  # Creating a parsed html file for applying Xpath
    xpath_categories = "//ul[@class= 'nav header-nav header-bottom-nav nav-left  nav-pills nav-size-small nav-uppercase']//a/@href"
    # Returns a list of links of each category
    category_link_list = [category_link for category_link in parsed_html.xpath(xpath_categories)]

    final_output = []
    if not os.path.exists(f"all_links.txt"):
        for link in category_link_list:
            with open('all_links.txt', 'a') as file:
                file.write(link + '/n')

    for link in set(category_link_list):
        sub_category_dict = {}
        if link.count('/') == 5 and 'product-category' in link and 'waterproofing' not in link:
            pass
        elif 'product-category' in link and len(link) > 42:
            print(f'Started working on {link}')
            sub_category_response = page_checker(url=link, method=method, path=os.path.join(project_files_dir, 'Category_Pages'))

            # sub_category_response = req_sender(url=link, method=method)
            if sub_category_response is not None:
                # Sending request for sub category page
                parsed_sub_cat_html = html.fromstring(html=sub_category_response)  # Creating a parsed html file for applying Xpath

                bread_1_link = url
                bread_1_name = 'HOME'
                xpath_bread_2_link = "//nav[@class='woocommerce-breadcrumb breadcrumbs uppercase']/a[2]/@href"
                bread_2_link = parsed_sub_cat_html.xpath(xpath_bread_2_link)[0] if parsed_sub_cat_html.xpath(xpath_bread_2_link) != [] else ''
                xpath_bread_2_name = "//nav[@class='woocommerce-breadcrumb breadcrumbs uppercase']/a[2]/text()"
                bread_2_name = parsed_sub_cat_html.xpath(xpath_bread_2_name)[0] if parsed_sub_cat_html.xpath(xpath_bread_2_name) != [] else ''

                xpath_bread_3_link = "//nav[@class='woocommerce-breadcrumb breadcrumbs uppercase']/a[3]/@href"
                bread_3_link = parsed_sub_cat_html.xpath(xpath_bread_3_link)[0] if parsed_sub_cat_html.xpath(xpath_bread_3_link) != [] else ''
                xpath_bread_3_name = "//nav[@class='woocommerce-breadcrumb breadcrumbs uppercase']/a[3]/text()"
                bread_3_name = parsed_sub_cat_html.xpath(xpath_bread_3_name)[0] if parsed_sub_cat_html.xpath(xpath_bread_3_name) != [] else ''

                xpath_this_category = '//nav[@class="woocommerce-breadcrumb breadcrumbs uppercase"]/text()[last()]'
                this_category_name = parsed_sub_cat_html.xpath(xpath_this_category)[0] if parsed_sub_cat_html.xpath(xpath_this_category) != [] else ''

                sub_category_dict[this_category_name.strip().title()] = [
                    {
                        "name": bread_1_name,
                        "url": bread_1_link
                    },
                    {
                        "name": bread_2_name,
                        "url": bread_2_link
                    }
                ]

                if bread_3_name != '' and bread_3_link != '':
                    sub_category_dict[this_category_name.strip().title()].append({
                        "name": bread_3_name,
                        "url": bread_3_link
                    })
                sub_category_dict[this_category_name.strip().title()].append({
                    "name": this_category_name.strip().title(),
                    "url": link
                })
                final_output.append(sub_category_dict)
                print(f'completed working on {link}', end='\n'+('-'*(len(link)+21)+'\n'))
            else:
                print(f'{link} is not Available.')

    with open('final_output.json', 'w') as file:
        file.write(json.dumps(final_output))


my_url = "https://hardwareshack.in/"
my_method = "GET"
my_path = os.path.dirname(os.path.abspath(__file__))

# Creating Saved Pages Directory for this Project if not Exists
project_name = 'Hardware_Shack'

project_files_dir = f'C:\\Project Files\\{project_name}_Project_Files'
ensure_directory_exists(path=project_files_dir)

scraper_func(url=my_url, method=my_method, path=os.path.join(project_files_dir, 'Main_Page'))
