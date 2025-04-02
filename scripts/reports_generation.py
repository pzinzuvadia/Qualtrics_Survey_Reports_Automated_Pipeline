# This file contains the function to generate reports for students based on the data csv files from processed_data directory.
# We generate function where we have complete records, only students and only supervisors records.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet


# paragraph styles used in pdf generation
para_style2=ParagraphStyle('My Para style',
#fontName='Times-Roman',
#backColor='#F1F1F1',
fontSize=10,
borderColor='black',
borderWidth=1,
borderPadding=(5,5,5),
leading=13,
alignment=0
)
para_style1=ParagraphStyle('My Para style',
#fontName='Times-Roman',
#backColor='#F1F1F1',
fontSize=18,
borderColor='black',
#borderWidth=1,
borderPadding=(3,3,13),
leading=17,
alignment=1
)


# ---------------------------------------
#       FOR COMPLETE RECORDS ONLY!
# ---------------------------------------
# Function to generate reports for students where we have complete records (both student and supervisor data available).
# This function is used internal in generate_report_for_student function.
def generate_report_with_supervisor(dataset, stu_fname, stu_last, improv, streng):
    """
    Generate a PDF report that includes a bar chart comparing student and supervisor ratings,
    along with the supervisor's written feedback.
    
    Parameters:
    - dataset: A list containing two NumPy arrays:
         [0]: Student ratings (array of 27 scores)
         [1]: Supervisor ratings (array of 27 scores)
    - stu_fname: Student's first name as a string.
    - stu_last: Student's last name as a string.
    - improv: Supervisor's feedback on areas for improvement.
    - streng: Supervisor's feedback on strengths.
    """
    # Create output directory if it doesn't exist.
    output_dir = "Reports/complete_reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Validate supervisor feedback. Replace empty or 'nan' values with a default message.
    if not improv.strip() or improv.lower() == 'nan':
        improv = "No feedback provided by the supervisor."
    if not streng.strip() or streng.lower() == 'nan':
        streng = "No feedback provided by the supervisor."
    
    # Define colors and styling for the chart.
    student_color = '#000000'      # Black for student ratings
    supervisor_color = '#a6192e'     # Scarlet for supervisor ratings
    # (Optional background and grid colors defined below are not actively used.)
    background_color = '#f8f9fa'     # Light Gray
    grid_color = '#dee2e6'           # Subtle Gray Grid Lines

    # Create a figure and axis for the bar chart.
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Compute y-axis positions for the 27 skills.
    num_skills = len(dataset[0])
    y_positions = np.arange(num_skills) * 2.0

    # Remove top and right borders for a cleaner look.
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Plot horizontal bars:
    # - Supervisor ratings (wider bars)
    ax.barh(y_positions, dataset[1], height=1.5, color=supervisor_color, label="Supervisor Rating")
    # - Student ratings (narrower bars)
    ax.barh(y_positions, dataset[0], height=0.9, color=student_color, label="Student Rating")

    # Calculate the difference between supervisor and student ratings.
    differences = dataset[1] - dataset[0]
    max_score = 7  # Fixed maximum score for x-axis
    chart_end_position = max_score + 1  # Extra space for labels

    # Add difference labels for each skill.
    for i, diff in enumerate(differences):
        abs_diff = abs(diff)
        if diff > 0:
            label_text = f'+{abs_diff} Supervisor'
        elif diff < 0:
            label_text = f'+{abs_diff} Student'
        else:
            label_text = ' '  # No difference
        ax.text(chart_end_position, y_positions[i], label_text,
                va='center', ha='left', fontsize=10, color='black')

    # Set x-axis limits and ticks.
    ax.set_xlim(0, chart_end_position + 1)
    ax.set_xticks(range(0, 8))
    
    # Create generic labels for skills (Skill 1, Skill 2, etc.).
    skill_labels = [f"Skill {i}" for i in range(1, num_skills + 1)]
    ax.set_yticks(y_positions)
    ax.set_yticklabels(skill_labels)

    # Add axis labels and title.
    ax.set_xlabel('Score', fontname="Arial", fontsize=12)
    ax.set_ylabel('Skill', fontname="Arial", fontsize=12)
    ax.set_title('Comparison of Student and Supervisor Skill Ratings', fontname="Arial", fontsize=14)

    # Add legend below the chart.
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=10)

    plt.tight_layout()

    # Save the bar chart as a PNG image.
    chart_filename = f"{output_dir}/{stu_fname}_{stu_last}.png"
    plt.savefig(chart_filename, dpi=500, bbox_inches='tight')
    plt.close()

    # Create the PDF report

    # Initialize the canvas for the PDF report.
    pdf_filename = f"{output_dir}/{stu_fname}_{stu_last}.pdf"
    my_canvas = canvas.Canvas(pdf_filename, pagesize=letter)
    my_canvas.rect(10, 10, 590, 770, stroke=1, fill=0)
    my_canvas.setLineWidth(0.3)

    # Register and set the Arial font (ensure that Arial.ttf is available in the working directory).
    pdfmetrics.registerFont(TTFont('Arial', './Arial.ttf'))
    my_canvas.setFont('Arial', 18)

    # Define paragraph styles (using ReportLab's sample style sheet).
    styles = getSampleStyleSheet()
    para_style1 = styles["Title"]
    para_style2 = styles["Normal"]

    # Create the report title paragraph.
    p1 = Paragraph(f'Intern - Supervisor Skill Survey Report<BR/>{stu_fname} {stu_last}', para_style1)
    
    # Draw a static image (assumed to be in the working directory).
    my_canvas.drawImage('skills.png', 30, 405, width=350, height=330)
    
    # Draw the previously saved chart image on the PDF.
    my_canvas.drawImage(chart_filename, 30, 40, width=550, height=350)

    # Change font for the feedback text.
    my_canvas.setFont('Helvetica', 10)
    p2 = Paragraph(
        f'''<b>Supervisor's Written Feedback </b><BR/>
            <font size=8><b>Strengths:</b><BR/>{streng}<BR/>
            <b>Areas for Improvement:</b><BR/>{improv}</font>''', 
        para_style2
    )

    # Wrap and position the paragraphs.
    p1.wrapOn(my_canvas, 350, 2)
    p1.drawOn(my_canvas, 148, 740)
    p2.wrapOn(my_canvas, 200, 2)
    p2.drawOn(my_canvas, 390, 463)
    
    # Save the PDF.
    my_canvas.save()


    # Clean up temporary chart image.
    os.remove(chart_filename)


# This is intermediate function that is used for generating report for complete data.
# This function runs the generate_report_with_supervisor function for each row.
def generate_complete_report(row, output_dir="Reports/complete_reports"):
    """
    Generate a report for a single student based on a row from the CSV.
    """
    # Extract student names
    stu_fname = row['stuFirst'].title()
    stu_last = row['stuLast'].title()
    
    # Extract the 27 self-rating scores (student scores)
    student_scores = row[[f'ssSelf_{i}' for i in range(1, 28)]].values.astype(float)
    
    # Extract the 27 supervisor ratings
    supervisor_scores = row[[f'ssSup_{i}' for i in range(1, 28)]].values.astype(float)
    
    # Create the dataset for the chart (list with two arrays)
    dataset = [student_scores, supervisor_scores]
    
    # Extract supervisor comments for improvement and strengths
    if not isinstance(row['improveText'], str) or row['improveText'] == None or row['improveText'] == 0:
        improv = "No feedback provided by the supervisor."
    else:
        improv = row['improveText']
    
    if not isinstance(row['strengthText'], str) or row['strengthText'] == None or row['strengthText'] == 0:
        improv = "No feedback provided by the supervisor."
    else:
        streng = row['strengthText']
    
    # Wrap names in list-of-list structure if needed to match previous function's indexing
    generate_report_with_supervisor(dataset, stu_fname, stu_last, improv, streng)


# This function reads the csv file and passes the data row by row to subsequent functions for gnerating reports.
# This function is called in main file
def generate_reports_from_complete_csv(csv_path, output_dir):
    """
    Reads the CSV file and generates a report for each student.
    """
    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_path)
    
    # Create output directory if it does not exist
    # output_dir = "Reports/complete_reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Iterate through each row and generate a report
    for index, row in df.iterrows():
        generate_complete_report(row, output_dir)
    print("Report generation for complete records is completed successfully!")
    print("-----------------------------------------------")


# ---------------------------------------
#       FOR STUDENTS RECORDS ONLY!
# ---------------------------------------
# Function to generate reports for students where we have only students records (only students data available).
# This function is used internal in generate_report_for_student function.
def generate_report_without_supervisor(dataset, stu_fname, stu_last):
    """
    Generates a PDF report for a student where only student ratings are available.
    
    Parameters:
      dataset : pandas.DataFrame
          DataFrame containing student data. The first column is assumed to contain
          the student ratings, and the DataFrame index holds the skill names.
      stu_fname : list
          Student first name(s); this function uses the first element's first character.
      stu_last : list
          Student last name(s); this function uses the first element's first character.
    """
    """
    create a new directory for storing the reports
    """
    output_dir = "Reports/only_students_reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    """
    plotting the bar charts and saving them as image in the reports folder
    """
   # Shiny colors and background settings
    student_color = '#a6192e'  # Scarlet/Red for student rating bars

    fig, ax = plt.subplots(figsize=(15, 6))
    y_positions = np.arange(len(dataset)) * 2.0  # Spacing between bars

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Plot horizontal bar chart using the first column of dataset as student ratings
    ax.barh(y_positions, dataset.iloc[:, 0], height=0.8, color=student_color, label='Student Rating')

    # Set labels using the DataFrame index (assumed to be the skill names)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(dataset.index)
    ax.set_xlabel('Score', fontname="Arial", fontsize=12)
    ax.set_ylabel('Skill', fontname="Arial", fontsize=12)
    ax.set_title('Student Ratings', fontname="Arial", fontsize=14)

    # Legend placed below the x-axis
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.03), ncol=1, fontsize=10)
    plt.tight_layout()

    # Save the chart as an image in the Reports folder.
    img_filename = f'{output_dir}/{stu_fname[0]}_{stu_last[0]}.png'
    plt.savefig(img_filename, dpi=500, bbox_inches='tight')
    plt.close()

    # Create a PDF canvas and store the report in the Reports directory.
    pdf_filename = f"{output_dir}/{stu_fname[0]}_{stu_last[0]}.pdf"
    my_canvas = canvas.Canvas(pdf_filename, pagesize=letter)
    my_canvas.rect(10, 10, 590, 770, stroke=1, fill=0)
    my_canvas.setLineWidth(0.3)

    # Register and set the Arial font (make sure Arial.ttf is available)
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    styles = getSampleStyleSheet()
    para_style1 = styles['Title']
    para_style2 = styles['BodyText']

    # Draw the title and student information at the top of the PDF
    my_canvas.setFont('Arial', 18)
    title_paragraph = Paragraph(
        f'''Intern - Supervisor Skill Survey Report<BR/>{stu_fname[0]} {stu_last[0]}''',
        para_style1
    )
    title_paragraph.wrapOn(my_canvas, 350, 2)
    title_paragraph.drawOn(my_canvas, 148, 740)

    # Draw the skills image (assumes 'skills.png' is available in the working directory)
    my_canvas.drawImage('skills.png', 30, 405, width=350, height=330)

    # Draw the generated bar chart image
    my_canvas.drawImage(img_filename, 30, 40, width=550, height=350)

    # Draw the supervisor feedback section indicating no supervisor report was provided
    my_canvas.setFont('Helvetica', 10)
    feedback_paragraph = Paragraph(
        '''<b>Supervisor's Written Feedback</b><BR/>
         <font size=8>
         <b>Strengths:</b><BR/>No supervisor report provided.<BR/>
         <b>Areas for Improvement:</b><BR/>No supervisor report provided.
         </font>''',
        para_style2
    )
    feedback_paragraph.wrapOn(my_canvas, 200, 200)
    feedback_paragraph.drawOn(my_canvas, 390, 463)

    additional_feedback = Paragraph(
        'No supervisor report provided.',
        para_style2
    )
    additional_feedback.wrapOn(my_canvas, 200, 50)
    additional_feedback.drawOn(my_canvas, 390, 415)

    my_canvas.save()

    # Remove the temporary image file created for the bar chart
    os.remove(img_filename)



# This is intermediate function that is used for generating report for only students data.
# This function runs the generate_report_without_supervisor function for each row.
def generate_only_student_report(row, output_dir="Reports/only_students_reports"):
    """
    Generate a report for a single student based on a row from the CSV.
    """
    # Extract student names
    stu_fname = [row['stuFirst'].title()]
    stu_last = [row['stuLast'].title()]
    
    # Extract the 27 self-rating scores (student scores)
    student_scores = row[[f'ssSelf_{i}' for i in range(1, 28)]].values.astype(float)
    
    # Extract the 27 supervisor ratings
    # supervisor_scores = row[[f'ssSup_{i}' for i in range(1, 28)]].values.astype(float)
    # Define 27 skill names (you can customize these labels if you have specific skill names)
    skill_names = [f"Skill {i}" for i in range(1, 28)]
    
    # # Create the dataset for the chart (list with two arrays)
    # dataset = [student_scores]
     # Create the dataset as a DataFrame with one column for ratings and skill names as the index.
    dataset = pd.DataFrame(student_scores, index=skill_names, columns=["Rating"])
    
    # Extract supervisor comments for improvement and strengths
    # if not isinstance(row['improveText'], str) or row['improveText'] == None or row['improveText'] == 0:
    #     improv = "No feedback provided by the supervisor."
    # else:
    #     improv = row['improveText']
    
    # if not isinstance(row['strengthText'], str) or row['strengthText'] == None or row['strengthText'] == 0:
    #     improv = "No feedback provided by the supervisor."
    # else:
    #     streng = row['strengthText']
    
    # Wrap names in list-of-list structure if needed to match previous function's indexing
    generate_report_without_supervisor(dataset, stu_fname, stu_last)


# This function reads the csv file and passes the data row by row to subsequent functions for generating reports.
# This function is called in main file
def generate_reports_from_only_student_csv(csv_path, output_dir):
    """
    Reads the CSV file and generates a report for each student.
    """
    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_path)
    
    # Create output directory if it does not exist
    # output_dir = "Reports/complete_reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Iterate through each row and generate a report
    for index, row in df.iterrows():
        generate_only_student_report(row, output_dir)
    print("Report generation for only students records is completed successfully!")
    print("-----------------------------------------------")


# ---------------------------------------
#       FOR SUPERVISOR RECORDS ONLY!
# ---------------------------------------
# Function to generate reports for students where we have only supervisor records (only supervisor data available).
# This function is used internal in generate_report_for_student function.
def generate_report_without_student(dataset, stu_fname, stu_last, improv, streng):
    """
    Generates a PDF report for a student where only supervisor ratings are available.
    
    Parameters:
      dataset : pandas.DataFrame
          DataFrame containing student data. The first column is assumed to contain
          the student ratings, and the DataFrame index holds the skill names.
      stu_fname : list
          Student first name(s); this function uses the first element's first character.
      stu_last : list
          Student last name(s); this function uses the first element's first character.
      - improv: Supervisor's feedback on areas for improvement.
      - streng: Supervisor's feedback on strengths.
    """
    """
    create a new directory for storing the reports
    """
    output_dir = "Reports/only_supervisor_reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    """
    plotting the bar charts and saving them as image in the reports folder
    """
   # Shiny colors and background settings
    student_color = '#a6192e'  # Scarlet/Red for student rating bars

    fig, ax = plt.subplots(figsize=(15, 6))
    y_positions = np.arange(len(dataset)) * 2.0  # Spacing between bars

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Plot horizontal bar chart using the first column of dataset as student ratings
    ax.barh(y_positions, dataset.iloc[:, 0], height=0.8, color=student_color, label='Supervisor Rating')

    # Set labels using the DataFrame index (assumed to be the skill names)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(dataset.index)
    ax.set_xlabel('Score', fontname="Arial", fontsize=12)
    ax.set_ylabel('Skill', fontname="Arial", fontsize=12)
    ax.set_title('Supervisor Ratings', fontname="Arial", fontsize=14)

    # Legend placed below the x-axis
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.03), ncol=1, fontsize=10)
    plt.tight_layout()

    # Save the chart as an image in the Reports folder.
    img_filename = f'{output_dir}/{stu_fname[0]}_{stu_last[0]}.png'
    plt.savefig(img_filename, dpi=500, bbox_inches='tight')
    plt.close()

    # Create a PDF canvas and store the report in the Reports directory.
    pdf_filename = f"{output_dir}/{stu_fname[0]}_{stu_last[0]}.pdf"
    my_canvas = canvas.Canvas(pdf_filename, pagesize=letter)
    my_canvas.rect(10, 10, 590, 770, stroke=1, fill=0)
    my_canvas.setLineWidth(0.3)

    # Register and set the Arial font (make sure Arial.ttf is available)
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    styles = getSampleStyleSheet()
    para_style1 = styles['Title']
    para_style2 = styles['BodyText']

    # Draw the title and student information at the top of the PDF
    my_canvas.setFont('Arial', 18)
    title_paragraph = Paragraph(
        f'''Intern - Supervisor Skill Survey Report<BR/>{stu_fname[0]} {stu_last[0]}''',
        para_style1
    )
    title_paragraph.wrapOn(my_canvas, 350, 2)
    title_paragraph.drawOn(my_canvas, 148, 740)

    # Draw the skills image (assumes 'skills.png' is available in the working directory)
    my_canvas.drawImage('skills.png', 30, 405, width=350, height=330)

    # Draw the generated bar chart image
    my_canvas.drawImage(img_filename, 30, 40, width=550, height=350)

    # Draw the supervisor feedback section indicating no supervisor report was provided
    my_canvas.setFont('Helvetica', 10)
    feedback_paragraph = Paragraph(
        f'''<b>Supervisor's Written Feedback </b><BR/>
            <font size=8><b>Strengths:</b><BR/>{streng}<BR/>
            <b>Areas for Improvement:</b><BR/>{improv}</font>''', 
        para_style2
    )
    feedback_paragraph.wrapOn(my_canvas, 200, 2)
    feedback_paragraph.drawOn(my_canvas, 390, 463)

    additional_feedback = Paragraph(
        'No student report provided.',
        para_style2
    )
    additional_feedback.wrapOn(my_canvas, 200, 50)
    additional_feedback.drawOn(my_canvas, 390, 415)

    my_canvas.save()

    # Remove the temporary image file created for the bar chart
    os.remove(img_filename)



# This is intermediate function that is used for generating report for only students data.
# This function runs the generate_report_without_supervisor function for each row.
def generate_only_supervisor_report(row, output_dir="Reports/only_supervisor_reports"):
    """
    Generate a report for a single student based on a row from the CSV.
    """
    # Extract student names
    stu_fname = [row['firstNameIntern'].title()]
    stu_last = [row['lastNameIntern'].title()]
    
    # Extract the 27 self-rating scores (student scores)
    supervisor_scores = row[[f'ssSup_{i}' for i in range(1, 28)]].values.astype(float)
    
    # Extract the 27 supervisor ratings
    # supervisor_scores = row[[f'ssSup_{i}' for i in range(1, 28)]].values.astype(float)
    # Define 27 skill names (you can customize these labels if you have specific skill names)
    skill_names = [f"Skill {i}" for i in range(1, 28)]
    
    # # Create the dataset for the chart (list with two arrays)
    # dataset = [student_scores]
     # Create the dataset as a DataFrame with one column for ratings and skill names as the index.
    dataset = pd.DataFrame(supervisor_scores, index=skill_names, columns=["Rating"])
    
    # Extract supervisor comments for improvement and strengths
    if not isinstance(row['improveText'], str) or row['improveText'] == None or row['improveText'] == 0:
        improv = "No feedback provided by the supervisor."
    else:
        improv = row['improveText']
    
    if not isinstance(row['strengthText'], str) or row['strengthText'] == None or row['strengthText'] == 0:
        improv = "No feedback provided by the supervisor."
    else:
        streng = row['strengthText']
    
    # Wrap names in list-of-list structure if needed to match previous function's indexing
    generate_report_without_student(dataset, stu_fname, stu_last, improv, streng)


# This function reads the csv file and passes the data row by row to subsequent functions for generating reports.
# This function is called in main file
def generate_reports_from_only_supervisor_csv(csv_path, output_dir):
    """
    Reads the CSV file and generates a report for each student.
    """
    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_path)
    
    # Create output directory if it does not exist
    # output_dir = "Reports/complete_reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Iterate through each row and generate a report
    for index, row in df.iterrows():
        generate_only_supervisor_report(row, output_dir)
    print("Report generation for only supervisor records is completed successfully!")
    print("-----------------------------------------------")














