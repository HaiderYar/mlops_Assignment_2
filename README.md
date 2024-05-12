# Airflow Data Extraction Pipeline

This project automates a data extraction lifecycle from extracting data, transforming it, saving it while versioning the data with DVC and code with Git.

## How To Run?
- Install the necessary libraries from `requirements.txt` file
- Run the following to install Apache Airflow in a Python virtual environment:
```bash
pip install apache-airflow
```
- Set the Airflow environment variable:
```bash
export AIRFLOW_HOME="path to the root of this cloned repo"
```

- Initialize Airflow's database:
```bash
airflow db init
```
- Run the following in a separate console to start the Airflow scheduler:
```bash
airflow scheduler
```
- Run the following in another separate console and open the Airflow user interface at `http://localhost:8080`:
```bash
airflow webserver -p 8080
```
- Find the DAG with the name specified in the code and toggle the pause button to activate the DAG.
- Click the play button on the top right to manually trigger the DAG run.

## DAG Documentation

### Extract Task:
Extracts data from a list of URLs (`urls`) using the `extract_data` function. Each URL is processed sequentially, and the extracted data is combined.

### Preprocess Task:
Preprocesses the extracted data using the `clean_data` function. This task ensures that the text data is cleaned and formatted consistently.

### Save Task:
Saves the preprocessed data to a CSV file specified by filename. The data is saved in the format of 'title', 'description'.

### DVC Push Task:
Adds the CSV file (`data/extracted.csv`) to the DVC repository using `dvc add` command and pushes the changes to the remote Google Drive storage using `dvc push`.

### Git Push Task:
Performs Git operations to push the changes made to the Git repository. It includes commands to pull changes, add files, commit changes, and push to the remote repository.

## DAG Execution Order
The tasks are executed sequentially in the following order:

`extract_task >> preprocess_task >> save_task >> dvc_push_task >> git_push_task`

The DAG is configured to run manually (`schedule=None`) and does not have a specific schedule for automatic execution.

## Points To Note
- Place all/any DAGs in the `/dags` folder for Airflow to detect.
- Run `airflow dags list` to check if Airflow properly picks up DAGs from the DAG bag (dag folder which contains all DAGs).
