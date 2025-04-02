# This file contains the function to download survey data from Qualtrics using the Qualtrics API.
# Data is first extracted and then filtered based on user input. After filtering, the data is saved to CSV files and further processed.
# Importing required libraries

import os
import requests
import sys
import zipfile
import io
import time
from datetime import datetime
import pandas as pd



#  function to download the survey raw data
def download_survey(survey_id: str, datacenter_id: str, api_token: str, output_dir: str = "MySurveys/raw_data") -> None:
    """
    Download survey data for a given survey_id from Qualtrics and extract it.

    Args:
        survey_id: The survey identifier.
        datacenter_id: The data center identifier (e.g., 'sdsu.iad1').
        api_token: The API token for authentication.
        output_dir: Directory where the downloaded survey files will be extracted.
    """
    # Construct the base URL and headers
    base_url = f"https://{datacenter_id}.qualtrics.com/API/v3/surveys/{survey_id}/export-responses/"
    headers = {
        "content-type": "application/json",
        "x-api-token": api_token,
    }

    # Step 1: Initiate the data export
    payload = {
        "format": "csv",
        "seenUnansweredRecode": 0,
        # "useLabels": "true",  # Uncomment to get text values instead of recoded values.
    }
    response = requests.post(base_url, json=payload, headers=headers)
    response_data = response.json()

    progress_id = response_data.get("result", {}).get("progressId")
    if not progress_id:
        print("Error initiating export:", response_data)
        sys.exit(2)

    # Step 2: Poll for export progress until complete or failed
    poll_url = f"{base_url}{progress_id}"
    progress_status = "inProgress"
    file_id = None

    while progress_status not in ["complete", "failed"] and file_id is None:
        time.sleep(1)  # Sleep for a second to avoid overwhelming the server
        poll_response = requests.get(poll_url, headers=headers)
        poll_data = poll_response.json().get("result", {})
        progress_status = poll_data.get("status", progress_status)
        file_id = poll_data.get("fileId")
        percent_complete = poll_data.get("percentComplete", 0)
        # Optional: log progress
        print(f"Export progress: {percent_complete}%")

    if progress_status == "failed":
        raise Exception("Export failed")

    # Step 3: Download the exported file
    download_url = f"{base_url}{file_id}/file"
    download_response = requests.get(download_url, headers=headers, stream=True)

    # Step 4: Extract the downloaded ZIP file
    with zipfile.ZipFile(io.BytesIO(download_response.content)) as zf:
        zf.extractall(output_dir)

    # Optional: log completion
    print("Download and extraction complete")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")


# Function to get the recorded date from the user --> to be used in the get_data_after_recorded_date function.
def get_recorded_date(name: str) -> datetime:
    """
    Prompt the user to enter a date for the given name and return it as a datetime object.
    
    Args:
        name (str): The identifier for which the date is being requested.
    
    Returns:
        datetime: The date provided by the user.
    """
    while True:
        date_str = input(f"Include data from which date onward for {name}? (yyyy-mm-dd): ")
        try:
            recorded_date = datetime.strptime(date_str, "%Y-%m-%d")
            return recorded_date
        except ValueError:
            print("Invalid date format. Please use the format yyyy-mm-dd.")


# Function to get data after the recorded date for both intern and supervisor surveys. 
# After filtering and cleaning the data, it saves the cleaned data to CSV files.
def get_data_after_recorded_date(intern_csv: str = "MySurveys/raw_data/SDSU Student Interns Survey.csv",
                                supervisor_csv: str = "MySurveys/raw_data/SDSU Intern Supervisor Evaluation Survey.csv"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load survey data for interns and supervisors, filter out records on or after user-specified dates,
    remove unnecessary columns, and save the cleaned data to CSV files.
    
    Args:
        intern_csv (str): Path to the intern survey CSV file.
        supervisor_csv (str): Path to the supervisor survey CSV file.
    """
    # Read CSV files while skipping the first two rows and parsing the RecordedDate column
    intern_data = pd.read_csv(intern_csv)
    intern_data.drop(0, inplace=True)
    intern_data.drop(1, inplace=True)
    intern_data.reset_index(drop=True, inplace=True)

    supervisor_data = pd.read_csv(supervisor_csv)
    supervisor_data.drop(0, inplace=True)
    supervisor_data.drop(1, inplace=True)
    supervisor_data.reset_index(drop=True, inplace=True)

    # Convert RecordedDate columns to datetime (just in case parsing didn't catch all cases)
    intern_data["RecordedDate"] = pd.to_datetime(intern_data["RecordedDate"], errors='coerce')
    supervisor_data["RecordedDate"] = pd.to_datetime(supervisor_data["RecordedDate"], errors='coerce')
    
    # Sort by RecordedDate and drop rows missing key identifier columns
    # intern_data = (
    #     intern_data.sort_values(by="RecordedDate", ascending=True)
    #                .dropna(subset=["stuFirst", "stuLast"], how="all")
    #                .reset_index(drop=True)
    # )
    intern_data = (
        intern_data.sort_values(by="RecordedDate", ascending=True)
                   .reset_index(drop=True)
    )

    # supervisor_data = (
    #     supervisor_data.sort_values(by="RecordedDate", ascending=True)
    #                    .dropna(subset=["supFirst", "supLast"], how="all")
    #                    .reset_index(drop=True)
    # )
    supervisor_data = (
        supervisor_data.sort_values(by="RecordedDate", ascending=True)
                       .reset_index(drop=True)
    )
    
    # Prompt the user for the cutoff dates
    student_onwards = get_recorded_date("student_surveys")
    supervisor_onwards = get_recorded_date("supervisor_surveys")
    
    # Filter records that are on or after the provided dates
    intern_data = intern_data[(intern_data["RecordedDate"] >= student_onwards) & (intern_data['Finished'] == "1")]
    supervisor_data = supervisor_data[(supervisor_data["RecordedDate"] >= supervisor_onwards) & (supervisor_data['Finished'] == "1")]

    # Filter out important columns necessary for report generation
    intern_data = intern_data[["RecordedDate", "intTitle", "stuFirst", "stuLast", "supLinkFirst", "supLinkLast", "ssSelf_1", "ssSelf_2", "ssSelf_3",
                               "ssSelf_4", "ssSelf_5", "ssSelf_6", "ssSelf_7", "ssSelf_8", "ssSelf_9", "ssSelf_10", "ssSelf_11", "ssSelf_12", "ssSelf_13", 
                               "ssSelf_14", "ssSelf_15", "ssSelf_16", "ssSelf_17", "ssSelf_18", "ssSelf_19", "ssSelf_20", "ssSelf_21", "ssSelf_22", "ssSelf_23", 
                               "ssSelf_24", "ssSelf_25", "ssSelf_26", "ssSelf_27"]].reset_index(drop=True)
    
    supervisor_data = supervisor_data[["RecordedDate", "supFirst", "supLast", "firstNameIntern", "lastNameIntern", "ssSup_1", "ssSup_2", "ssSup_3", "ssSup_4",
                                       "ssSup_5", "ssSup_6", "ssSup_7", "ssSup_8", "ssSup_9", "ssSup_10", "ssSup_11", "ssSup_12", "ssSup_13", "ssSup_14", 
                                       "ssSup_15", "ssSup_16", "ssSup_17", "ssSup_18", "ssSup_19", "ssSup_20", "ssSup_21", "ssSup_22", "ssSup_23", "ssSup_24", 
                                       "ssSup_25", "ssSup_26", "ssSup_27", "improveText", "strengthText"]].reset_index(drop=True)

    intern_data.to_csv("MySurveys/intermediate_results/student_data_filtered_by_date.csv", encoding="utf-8", index=False)
    supervisor_data.to_csv("MySurveys/intermediate_results/supervisor_data_filtered_by_date.csv", encoding="utf-8", index=False)

    # Optional: log completion
    print("Data filtering complete")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")
    return intern_data, supervisor_data


# Function to merge the intern and supervisor datasets based on the standardized name columns.
def merge_datasets(intern_data: pd.DataFrame,
                   supervisor_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge intern and supervisor datasets using an outer join.
    This ensures all data from both datasets is included.
    
    The merge is based on standardized name columns:
      - From intern_data: ["stuFirst", "stuLast", "supLinkFirst", "supLinkLast"]
      - From supervisor_data: ["firstNameIntern", "lastNameIntern", "supFirst", "supLast"]
      
    Args:
        intern_data: DataFrame containing intern data.
        supervisor_data: DataFrame containing supervisor data.
    
    Returns:
        pd.DataFrame: Merged DataFrame combining both datasets.
    """

    # Merging columns from intern_data: ["stuFirst", "stuLast", "supLinkFirst", "supLinkLast"]
    # Merging columns from supervisor_data: ["supFirst", "supLast", "firstNameIntern", "lastNameIntern"]

    intern_data["stuFirst"] = intern_data["stuFirst"].str.lower().str.strip()
    intern_data["stuLast"] = intern_data["stuLast"].str.lower().str.strip()
    intern_data["supLinkFirst"] = intern_data["supLinkFirst"].str.lower().str.strip()
    intern_data["supLinkLast"] = intern_data["supLinkLast"].str.lower().str.strip()

    supervisor_data["supFirst"] = supervisor_data["supFirst"].str.lower().str.strip()
    supervisor_data["supLast"] = supervisor_data["supLast"].str.lower().str.strip()
    supervisor_data["firstNameIntern"] = supervisor_data["firstNameIntern"].str.lower().str.strip()
    supervisor_data["lastNameIntern"] = supervisor_data["lastNameIntern"].str.lower().str.strip()

    # columns header of merged dataframe with suffix _x means of intern_data and _y means of supervisor_data

    merged_data = intern_data.merge(supervisor_data, left_on = ["stuFirst", "stuLast", "supLinkFirst", "supLinkLast"], 
                                        right_on = ["firstNameIntern", "lastNameIntern", "supFirst", "supLast"], how = "outer").reset_index(drop=True)

    merged_data.to_csv("MySurveys/intermediate_results/merged_data.csv", encoding="utf-8", index=False)

    print("Merged Dataset downloaded!")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")
    return merged_data


# Function to filter the merged data to include only records where both student and supervisor data exist.
def complete_records_data(merged_data: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the merged data to include only records where both student and supervisor data exist.
    
    Args:
        merged_data: DataFrame containing the merged student and supervisor survey data.
    """

    # Define key columns that must be present for a complete record
    key_columns = [
        "stuFirst", "stuLast", "supLinkFirst", "supLinkLast",
        "firstNameIntern", "lastNameIntern", "supFirst", "supLast"
    ]
    # merged_data['idx'] = merged_data.index
    merged_data.insert(0, 'idx', merged_data.index)
    # Filter complete records (drop rows with any missing values in key columns)
    complete_records = merged_data.dropna(subset=key_columns, how="any")

    complete_records.drop_duplicates(subset = key_columns, inplace = True)
    
    # Save complete records to CSV for reference
    complete_csv = "MySurveys/intermediate_results/complete_records.csv"
    complete_records.to_csv(complete_csv, index=False)
    print(f"Saved complete records to {complete_csv}")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")
    return complete_records


# Function to get the merged data which has only supervisors data.
def only_supervisor_data(merged_data: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the merged data to include only records where supervisor data exists and no student data.
    
    Args:
        merged_data: DataFrame containing the merged student and supervisor survey data.
    """
    # merged_data['idx'] = merged_data.index
    merged_data.insert(33, 'idx', merged_data.index)
    merged_data = merged_data[(merged_data["firstNameIntern"].notna()) & (merged_data["lastNameIntern"].notna()) & (merged_data["supFirst"].notna()) & (merged_data["supLast"].notna())]
    merged_data = merged_data[(merged_data['stuFirst'].isna()) & (merged_data['stuLast'].isna()) & (merged_data['supLinkFirst'].isna()) & (merged_data['supLinkLast'].isna())]

    merged_data.drop_duplicates(subset = ["firstNameIntern", "lastNameIntern", "supFirst", "supLast"], inplace = True)
    merged_data = merged_data.loc[:, "idx":]

    # Save records to CSV for reference
    only_supervisor_csv = "MySurveys/intermediate_results/only_supervisor_records.csv"
    merged_data.to_csv(only_supervisor_csv, index=False)
    print(f"Saved complete records to {only_supervisor_csv}")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")
    return merged_data


# Function to get the merged data which has only students data.
def only_student_data(merged_data: pd.DataFrame) -> None:
    """
    Filter the merged data to include only records where supervisor data exists and no student data.
    
    Args:
        merged_data: DataFrame containing the merged student and supervisor survey data.
    """

    # merged_data['idx'] = merged_data.index
    merged_data.insert(0, 'idx', merged_data.index)

    merged_data = merged_data[(merged_data['stuFirst'].notna()) & (merged_data['stuLast'].notna()) & (merged_data['supLinkFirst'].notna()) & (merged_data['supLinkLast'].notna())]
    merged_data = merged_data[(merged_data["firstNameIntern"].isna()) & (merged_data["lastNameIntern"].isna()) & (merged_data["supFirst"].isna()) & (merged_data["supLast"].isna())]

    merged_data.drop_duplicates(subset = ["stuFirst", "stuLast", "supLinkFirst", "supLinkLast"], inplace = True)
    merged_data = merged_data.loc[:, :"ssSelf_27"]

    # Save records to CSV for reference
    only_student_csv = "MySurveys/intermediate_results/only_students_records.csv"
    merged_data.to_csv(only_student_csv, index=False)
    print(f"Saved complete records to {only_student_csv}")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")
    return merged_data


# Function to merge only student and only supevisor data based on common student name
def join_only_student_supervisor_data(only_student_data: pd.DataFrame,
                                      only_supervisor_data: pd.DataFrame) -> pd.DataFrame:
    """
    Merge only student and only supervisor data based on common student name.
    
    Args:
        only_student_path: Path to the CSV file containing only student data.
        only_supervisor_path: Path to the CSV file containing only supervisor data.
    """
    # Merging columns from only_student_data: ["stuFirst", "stuLast"]
    # Merging columns from only_supervisor_data: ["firstNameIntern", "lastNameIntern"]
    # columns header of merged dataframe with suffix _x means of only_student_data and _y means of only_supervisor_data

    merged_data = only_student_data.merge(only_supervisor_data, left_on = ["stuFirst", "stuLast"], 
                                        right_on = ["firstNameIntern", "lastNameIntern"], how = "inner")

    merged_data.to_csv("MySurveys/intermediate_results/merged_only_student_supervisor_data.csv", encoding="utf-8", index=False)

    print("Merged ONLY-Dataset downloaded!")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")
    return merged_data


def process_data(merged_data: pd.DataFrame) -> None:
    """
    Process the merged data by removing duplicates, joining unmatched rows and saving to CSV.
    
    Args:
        merged_data: DataFrame containing the merged student and supervisor survey data.
    
    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    complete_records = complete_records_data(merged_data.copy())

    # Working with only student data and only supervisor data
    only_student_data_df = only_student_data(merged_data.copy())

    only_supervisor_data_df = only_supervisor_data(merged_data.copy())

    # Mapping records with same student name (in-case a different supervisor has submitted for student)
    merged_data = join_only_student_supervisor_data(only_student_data_df, only_supervisor_data_df)

    # concatenating complete records and merged_data (only student-supervisor onces)
    processed_completed_data = pd.concat([complete_records, merged_data], ignore_index=True)
    processed_completed_data.to_csv("MySurveys/processed_data/processed_completed_data.csv", encoding="utf-8", index=False)
    print("Processed Completed Data downloaded!")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")

    processed_only_student_data = only_student_data_df[~(only_student_data_df['idx'].isin(merged_data['idx_x']))]
    processed_only_student_data.to_csv("MySurveys/processed_data/processed_only_student_data.csv", encoding="utf-8", index=False)
    print("Processed ONLY Student Data downloaded!")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")

    processed_only_supervisor_data = only_supervisor_data_df[~(only_supervisor_data_df['idx'].isin(merged_data['idx_y']))]
    processed_only_supervisor_data.to_csv("MySurveys/processed_data/processed_only_supervisor_data.csv", encoding="utf-8", index=False)
    print("Processed ONLY Supervisor Data downloaded!")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n")

    print("DATA PROCESSING COMPLETED!")

















