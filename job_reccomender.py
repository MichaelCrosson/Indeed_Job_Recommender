# Libraries
import openai
import spacy
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from tqdm.notebook import tqdm
from gensim.corpora import Dictionary
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load('en_core_web_md')

# ChatGPT API key
# Enter your API key here
openai.api_key=""

# Load files from scraping
stop_words = nlp.Defaults.stop_words
job_reviews = pd.read_csv('company_reviews.csv')
job_listings = pd.read_csv('job_listings.csv')

# Function to remove punctuation, split merged words, keep both parts, remove stop words, and reduce spaces
def clean_review(text):
    if isinstance(text, str):
        # Split merged words
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

        # Convert text to lowercase
        text = text.lower()

        # Remove punctuation and replace with space if it is a period
        text = re.sub(r'[^\w\s]', ' ', text)

        # Remove stop words
        text = ' '.join([word for word in text.split() if word.lower() not in stop_words])

        # Reduce multiple spaces to a single space
        text = re.sub(r'\s+', ' ', text)
        return text
    return None

# Apply the function to the 'Review' column
job_reviews['Cleaned_Review'] = job_reviews['Review'].apply(clean_review)
job_listings['Cleaned_Description'] = job_listings['Description'].apply(clean_review)

# Drop duplicates
job_reviews = job_reviews.drop_duplicates(subset=['Company', 'Cleaned_Review'])
job_listings = job_listings.drop_duplicates(subset='Description')

# Drop rows with NaN values
job_listings = job_listings.dropna(subset=['Title'])

"""User Input and Analysis"""

# Accept User inputs for resume and job aspects
resume = input("Enter your resume: ")
blurb = input("Enter your preferences for a job: ")

# Prefrence flags
# Set to false if looking for internships and part-time jobs as well
fulltime_flag = True
blurb_weight = 1
resume_weight = 1
skill_weight = 1

# Resume summarization code
content = f"""
Analyze the following resume and provide a summary of the key points, specific technical skills (list out skills like Python and such), and qualifications. Only respond with a summary of the resume, do not add anything else.
{resume}
"""

completion = openai.chat.completions.create(
messages=[
    {
        "role": "user",
        "content": content,
    }
],
model="gpt-3.5-turbo",
)

resume_summary = completion.choices[0].message.content.replace('\\n',' ').replace('\n',' ').replace('_',' ')
print(resume_summary)

# Desired job aspects summarization code
content = f"""
Analyze the following aspects a person wants in a job and provide a summary of the key points and desires. Only respond with the aspects and single spaces in between, do not add anything else.
{blurb}
"""

completion = openai.chat.completions.create(
messages=[
    {
        "role": "user",
        "content": content,
    }
],
model="gpt-3.5-turbo",
)

blurb_summary = completion.choices[0].message.content.replace('\\n',' ').replace('\n',' ').replace('_',' ')
blurb_summary = re.sub(r'\s+', ' ', blurb_summary)

print(blurb_summary)

# Handle filtering for internships based on flag
if fulltime_flag == True:
    terms = ['intern', 'internship', 'coop', 'co-op', 'parttime', 'part-time', 'contract', 'contractor']
    for i in terms:
      job_listings = job_listings[~job_listings['Title'].str.contains(i, case=False, na=False)]

"""For Job Listings (B-O-W)"""

# Create documents list
documents = [resume_summary] + job_listings['Cleaned_Description'].tolist()

# Initialize CountVectorizer
count_vectorizer = CountVectorizer(stop_words='english')

# Fit and transform the documents
sparse_matrix = count_vectorizer.fit_transform(documents)

# Convert the sparse matrix to a dense matrix
doc_term_matrix = sparse_matrix.todense()

# Calculate the total sum of all counts row-wise, avoiding division by zero
total_sum = np.where(doc_term_matrix.sum(axis=1) == 0, 1, doc_term_matrix.sum(axis=1))

# Normalize the document-term matrix
normalized_matrix = doc_term_matrix / total_sum

# Handle any remaining NaN values by replacing them with 0
normalized_matrix = np.nan_to_num(normalized_matrix)

# Create a DataFrame for the normalized document-term matrix
df = pd.DataFrame(normalized_matrix, columns=count_vectorizer.get_feature_names_out(), index=['attributes'] + [f'review_{i}' for i in range(len(normalized_matrix)-1)])

# Calculate cosine similarities
cosine_sim = cosine_similarity(df.iloc[0:1], df.iloc[1:]).flatten()

# Create a DataFrame to store the results
df_similarity = pd.DataFrame({
    'company': job_listings['Company Name'],
    'job_title': job_listings['Title'],
    'company_location': job_listings['Company Location'],
    'description': job_listings['Description'],
    'cleaned_description': job_listings['Cleaned_Description'],
    'similarity_score': (cosine_sim * resume_weight)
})

# Save the results to a CSV file
df_similarity.to_csv('review_similarity_scores.csv', index=False)

# Group by company and calculate the mean similarity score, displaying the top values
top_jobs = df_similarity.sort_values('similarity_score', ascending = False)

"""For Company Reviews (NMF) Non-negative matrix factorization"""

# Extend the default English stop words with custom stop words
custom_stop_words = list(ENGLISH_STOP_WORDS.union(['work', 'job', 'company', 'employees', 'people', 'lot', 'management','just','make','don','dont','really','good','great','place','overall']))

# Update the TF-IDF vectorizer with the combined stop words
tfidf_vectorizer = TfidfVectorizer(max_features = 3000, ngram_range = (1,3), strip_accents='ascii', stop_words=custom_stop_words)

# Fit and transform the data
tfidf_matrix = tfidf_vectorizer.fit_transform(job_reviews['Cleaned_Review'])

num_topics = 10
nmf_model = NMF(n_components=num_topics, random_state=42)

# Fit the model
nmf_matrix = nmf_model.fit_transform(tfidf_matrix)

# Get the top terms per topic
feature_names = tfidf_vectorizer.get_feature_names_out()

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print(f"Topic {topic_idx}:")
        print(", ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))

# Display top words for each topic
display_topics(nmf_model, feature_names, 10)

job_reviews['Dominant_Topic'] = nmf_matrix.argmax(axis=1)

# Group by company and topic, then count the occurrences
topic_counts = job_reviews.groupby(['Company', 'Dominant_Topic']).size().reset_index(name='count')

# Get the top 4 counts for each company
top_4_counts = topic_counts.groupby('Company').apply(lambda x: x.nlargest(6, 'count')).reset_index(drop=True)

# Create a dictionary to map topic numbers to topic names
topic_mapping = {
    0: 'Work Environment Culture',
    1: 'Management Training',
    2: 'Work-Life Balance and Benefits',
    3: 'Opportunities and Career Growth',
    4: 'Pay and Benefits',
    5: 'Work Time and Family Balance',
    6: 'Social Atmosphere and Workplace',
    7: 'Work Experience and Longevity',
    8: 'Working Hours and Flexibility',
    9: 'Team Support Fast Challenging'
}

# Replace the values in 'Dominant_Topic' with actual topic names
top_4_counts['Dominant_Topic'] = top_4_counts['Dominant_Topic'].map(topic_mapping)

top_4_counts = top_4_counts.sort_values(['Company','Dominant_Topic'])

# Concatenate the topic names for each company with a space between them
pivoted_topics = top_4_counts.groupby('Company')['Dominant_Topic'].agg(' '.join).reset_index()

pivoted_topics.drop_duplicates(subset='Dominant_Topic')
print()

# Create documents list
documents = [blurb_summary] + pivoted_topics['Dominant_Topic'].tolist()

# Initialize CountVectorizer
count_vectorizer = CountVectorizer(stop_words='english')

# Fit and transform the documents
sparse_matrix = count_vectorizer.fit_transform(documents)

# Convert the sparse matrix to a dense matrix
doc_term_matrix = sparse_matrix.todense()

# Calculate the total sum of all counts row-wise, avoiding division by zero
total_sum = np.where(doc_term_matrix.sum(axis=1) == 0, 1, doc_term_matrix.sum(axis=1))

# Normalize the document-term matrix
normalized_matrix = doc_term_matrix / total_sum

# Handle any remaining NaN values by replacing them with 0
normalized_matrix = np.nan_to_num(normalized_matrix)

# Create a DataFrame for the normalized document-term matrix
df = pd.DataFrame(normalized_matrix, columns=count_vectorizer.get_feature_names_out(), index=['attributes'] + [f'review_{i}' for i in range(len(normalized_matrix)-1)])

# Calculate cosine similarities
cosine_sim = cosine_similarity(df.iloc[0:1], df.iloc[1:]).flatten()

# Create a DataFrame to store the results
company_similarity = pd.DataFrame({
    'company': pivoted_topics['Company'],
    'dominant_topic': pivoted_topics['Dominant_Topic'],
    'similarity_scores': (cosine_sim * blurb_weight)
})

# Save the results to a CSV file
company_similarity.to_csv('review_similarity_scores.csv', index=False)

# Group by company and calculate the mean similarity score, displaying the top values
top_companies = company_similarity.groupby('company')['similarity_scores'].mean().sort_values(ascending=False).reset_index()

"""Merged Jobs with Tech Skills Weighting"""

# Merge the two DataFrames on the 'company' column
merged_df = pd.merge(top_jobs, top_companies, on='company')

# Calculate the final similarity score by adding the job and company similarity scores
merged_df['final_similarity_score'] = merged_df['similarity_scores'] + merged_df['similarity_score']

# Generate a comprehensive list of skills
skills_list = [
    'Python', 'Java', 'JavaScript', 'SQL', 'C++', 'C#', 'R', 'Ruby', 'PHP', 'Swift', 'Go', 'Kotlin', 'Perl', 'Scala', 'Rust',
    'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js', 'Express', 'TensorFlow', 'PyTorch',
    'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Tableau', 'Power BI', 'Excel', 'AWS', 'Azure',
    'GCP', 'Docker', 'Kubernetes', 'Git', 'Jenkins', 'CI/CD', 'Agile', 'Scrum', 'Kanban', 'Linux', 'Unix', 'Windows',
    'Bash', 'Shell', 'Powershell', 'Hadoop', 'Spark', 'Kafka', 'Elasticsearch', 'MongoDB', 'MySQL', 'PostgreSQL', 'Oracle',
    'SQLite', 'Redis', 'Cassandra', 'GraphQL', 'REST', 'SOAP', 'API', 'Microservices', 'Blockchain', 'Machine Learning',
    'Deep Learning', 'Artificial Intelligence', 'Data Science', 'Data Analysis', 'Big Data', 'Cloud Computing', 'Cybersecurity',
    'DevOps', 'Networking', 'Virtualization', 'IoT', 'Robotics', 'Natural Language Processing', 'Computer Vision', 'AR/VR'
]

# Extract skills from resume_summary
def extract_skills(text, skills_list):
    return [skill for skill in skills_list if skill.lower() in text.lower()]

resume_skills = extract_skills(resume_summary, skills_list)

# Retrieve skills from Cleaned_Description
def extract_skills_from_description(description, skills_list):
    return extract_skills(description, skills_list)

merged_df['description_skills'] = merged_df['cleaned_description'].apply(lambda x: extract_skills_from_description(x, skills_list))

# Calculate the proportion of skills
def calculate_skill_proportion(resume_skills, description_skills):
    if not resume_skills:
        return 0
    matching_skills = set(resume_skills).intersection(description_skills)
    return len(matching_skills) / len(resume_skills)

merged_df['skill_proportion'] = merged_df.apply(lambda row: calculate_skill_proportion(resume_skills, row['description_skills']), axis=1)

merged_df['final_score'] = merged_df['final_similarity_score'] + ((merged_df['skill_proportion'] / 2) * skill_weight)

# Create the final DataFrame with the required columns
final_df = merged_df[['company', 'job_title', 'description', 'final_score', 'skill_proportion']]

# Sort and display the top entries
final_df = final_df.sort_values('final_score', ascending=False)

"""# Final Ranked Output"""

# Output the top companies based on similarity to blurb and company reviews
print(top_companies.head(5))

# Output the top company roles based on similarity to resume and job postings
print(top_jobs.head(5))

# Output the top averaged roles based on all information
print(final_df.head(5))
