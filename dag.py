import requests
from bs4 import BeautifulSoup
import csv
import re
from airflow.operators.python import PythonOperator
import os
from airflow import DAG


# Extraction code

def extract_data(url):
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = [link.get('href') for link in soup.find_all('a', href=True)]
    articles = soup.find_all('article')
    article_data = []
    for index, article in enumerate(articles):
        title = article.find('h2').text.strip() if article.find('h2') else ""
        if article.find(class_="story__excerpt"):
            description = article.find(class_="story__excerpt").text.strip()
        elif article.find(attrs={"data-testid": "card-description"}):
            description = article.find(attrs={"data-testid": "card-description"}).text.strip()
        else:
            description = ""
        article_data.append({'title': title, 'description': description})
    
    return links, article_data

# saving to a csv file
def save_to_csv(data, filename):

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for article in data:
            writer.writerow(article)


# Preprocessing the data

def preprocess_text(text):
    # Remove HTML tags
    cleaned_text = re.sub('<[^<]+?>', '', text)
    
    # Remove punctuation
    cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
    
    # Convert to lowercase
    cleaned_text = cleaned_text.lower()
    
    # Remove extra whitespaces
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text



def preprocess_articles(articles):
    preprocessed_articles = []
    for article in articles:
        title = article['title']
        description = article['description']
        
        # If description is empty, skip this article
        if not description:
            continue
        
        # Preprocess description
        cleaned_description = preprocess_text(description)
        
        preprocessed_articles.append({
            'title': title, 'description': cleaned_description
        })

    return preprocessed_articles


# Git push function
def push():
    os.system('git status')
    os.system('git pull')
    os.system('git status')
    os.system('git add .')
    os.system('git status')
    os.system('git commit -m "Upading the file automatically by dvc"')
    os.system('git status')
    os.system('git push origin main')
    os.system('git status')

# Used for dvc push command
def DVC_PUSH():
    os.system("dvc add extracted_data.csv")
    os.system("dvc push")

urls = ['https://www.dawn.com/','https://www.dawn.com/']
file_name = 'C:/University/Semester 8/MLOPS/Assignments/Assignment 2/mlops_Assignment_2/extracted_data.csv'

def extraction_task(urls):
    print("Data extraction task.......")
    all_articles = []
    for url in urls:
        links, articles = extract_data(url)
        all_articles.extend(articles)
    return all_articles

def preprcessing_task(articles):
    print("Preprocessing article.......")
    preprocessed_articles = preprocess_articles(articles)
    return preprocessed_articles

def saving_to_csv_task(articles,filename):
    print("Saving to csv.......")
    save_to_csv(articles,filename)


# Setting up dag

default_argums = {
    'owner': 'haider'
}

dag = DAG(
    dag_id='mlops_assignment2_DAG',
    default_args=default_argums,
    description='This is mlops assignment 2 DAG where web scraping is done and automitically updaing using dvc',
    tags=['assignment2', 'mlops'],
    catchup=False,
    schedule=None
)


with dag:
    extracting_task = PythonOperator(
        task_id='extracting_task',
        python_callable=extraction_task,
        op_kwargs={'urls': urls},
        provide_context=True
    )

    preprocess_task = PythonOperator(
        task_id='preprocess_task',
        python_callable=preprcessing_task,
        op_kwargs={'data': extracting_task.output},
        # provide_content=True
    )

    saving_task = PythonOperator(
        task_id = 'saving_task',
        python_callable=saving_to_csv_task,
        op_kwargs={'filename': file_name, 'data':preprocess_task.output},
        provide_context = True
    )

    dvc_push_task = PythonOperator(
        task_id = 'dvc_push_task',
        python_callable=DVC_PUSH
    )

    git_push_task = PythonOperator(
        task_id = 'git_push_task',
        python_callable=push
    )


# Execution Sequence 
extracting_task >> preprocess_task >> saving_task >> dvc_push_task >> git_push_task


def main():
    dawn_url = "https://www.dawn.com/"
    bbc_url = "https://www.bbc.com/"

    filename = 'C:/University/Semester 8/MLOPS/Assignments/Assignment 2/mlops_Assignment_2/extracted_data.csv'

    # Data Extraction from dawn
    dawn_links, dawn_articles = extract_data(dawn_url)
    print("Data has been extracted from dawn url")
    # 
    preprocessed_dawn_articles = preprocess_articles(dawn_articles)

    # Data Extraction from BBC
    print("\nExtracted BBC.com data:")
    bbc_links, bbc_articles = extract_data(bbc_url)
    preprocessed_bbc_articles = preprocess_articles(bbc_articles)

    # Concatenate articles from both sources
    all_articles = preprocessed_dawn_articles + preprocessed_bbc_articles
    
    # Save all data to a single CSV file
    save_to_csv(all_articles, 'extracted_data.csv')
    print("All data saved to CSV.")


if __name__ == '__main__':
    main()
