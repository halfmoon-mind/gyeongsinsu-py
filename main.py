import requests
from bs4 import BeautifulSoup
import concurrent.futures
import csv

def scrapNews(link):
    try:
        raw_data = requests.get(link)
        soup = BeautifulSoup(raw_data.text, "html.parser")
        title = soup.select_one("#title_area").get_text(strip=True)
        content = soup.select_one("#dic_area").get_text(strip=True)
        category = soup.select_one("#contents > div.media_end_categorize > a > em").get_text(strip=True)
        date = soup.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span").get_text(strip=True)
        if content == "":
            return None
        return {'title':title, 'date':date, 'content':content, 'category':category}
    except :
        return None

def save_news_to_csv(news_list, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['title', 'date', 'content', 'category']
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for news in news_list:
            if news:
                writer.writerow(news)

# set date to scrapping
def scrapNewsWithDate(date):
    link_list = []
    for i in range(1, 6):
        raw_data = requests.get("https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=009&listType=paper&date="+date+"&page="+str(i))
        # Parse the HTML content
        soup = BeautifulSoup(raw_data.text, "html.parser")
        main_content = soup.select_one("#main_content > div.list_body.newsflash_body")
        elements_with_firstlist = main_content.find_all(class_='firstlist')
        for element in elements_with_firstlist:
            result = BeautifulSoup(str(element), 'html.parser')
            links = result.find_all('a', href=True)
            for link in links:
                if len(link_list) == 0 or link_list[-1] != link['href']:
                    link_list.append(link['href'])
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=10)
    threads = []
    all_news = []
    for link in link_list:
        threads.append(pool.submit(scrapNews, link))
    for p in concurrent.futures.as_completed(threads):
        if p.result() is not None:
            all_news.append(p.result())

    save_news_to_csv(all_news, f"news_{date}.csv")


if __name__ == "__main__":
    scrapNewsWithDate("20240418")
