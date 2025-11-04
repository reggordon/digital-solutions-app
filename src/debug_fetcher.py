from fetcher import fetch_digital_solutions

if __name__ == '__main__':
    articles = fetch_digital_solutions()
    print('COUNT:', len(articles))
    for i, a in enumerate(articles[:20]):
        title = a.get('title', '<no title>')
        link = a.get('link', '<no link>')
        published = a.get('published', '')
        image = a.get('image', '')
        print(f"{i+1}. {title}\n   {published}\n   {link}\n   image: {image}\n")
