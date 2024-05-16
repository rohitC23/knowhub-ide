import streamlit as st
import pandas as pd
import sys
from io import StringIO
from streamlit_option_menu import option_menu
import os

def main():
    # Set up Streamlit page configuration
    st.set_page_config(
        page_title="knowhub",
        page_icon=":page_with_curl:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    choice = option_menu(None, ["KnowHub Python IDE", "KnowHub Quizzes"],
                         icons=['house', "list-task"],
                         menu_icon=None, default_index=0, orientation="horizontal",
                         styles={
                             "container": {"padding": "0!important", "background-color": "#fafafa"},
                             "icon": {"font-size": "25px"},
                             "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px",
                                          "--hover-color": "#eee","font-family": "Noto Sans Variable, sans-serif"},
                             "nav-link-selected": {"background-color": "#1976D2"},
                         }
                         )
    if choice == "KnowHub Python IDE":
        home()
    elif choice == "KnowHub Quizzes":
        quiz()


def home():
    import streamlit as st
    import matplotlib.pyplot as plt
    from io import BytesIO

    def run_code(i, code, shared_variables):
        try:
            # Capture stdout to capture text output
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            # Execute the user's code with access to shared variables
            exec(code, shared_variables)

            # Get the text output
            text_output = sys.stdout.getvalue()

            # Reset the standard output
            sys.stdout = old_stdout

            # Store the output in shared_variables
            output_key = f"output_{i}"
            shared_variables[output_key] = text_output

            # Check if any plots were created
            if plt.get_fignums():
                # Save the plot as an image
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)

                # Store the plot image in shared_variables
                shared_variables[output_key] = buf.getvalue()
                plt.close("all")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    def ide():
        st.title("Knowhub Python IDE")

        # Initialize session state
        if "code_blocks" not in st.session_state:
            st.session_state.code_blocks = {}
        if "shared_variables" not in st.session_state:
            st.session_state.shared_variables = {}

        # Get the number of code blocks from the user
        num_code_blocks = st.number_input("How many code blocks do you need?", min_value=1, max_value=10, value=1,
                                          step=1)

        for i in range(num_code_blocks):
            st.write(f"#### Code Block {i + 1}")

            # Applying css
            st.markdown(
                """
                <style>
                %s
                </style>
                """ % open("style.css").read(),
                unsafe_allow_html=True
            )

            # Get code input
            code = st.text_area(f"Enter your Python code for Block {i + 1} here:", height=350)

            # Save code to session state
            if f"code_block_{i + 1}" not in st.session_state.code_blocks:
                st.session_state.code_blocks[f"code_block_{i + 1}"] = {"code": code}

            # Run code block if button clicked
            if st.button(f"Run Block {i + 1}"):
                run_code(i + 1, code, st.session_state.shared_variables)

            # Display the output of the code block
            output_key = f"output_{i + 1}"
            if output_key in st.session_state.shared_variables:
                st.success(f"Output of Code Block {i + 1}: ")
                output = st.session_state.shared_variables[output_key]
                if isinstance(output, str):
                    st.code(output)
                elif isinstance(output, bytes):
                    st.image(BytesIO(output))

    ide()


def quiz():
    def quizzes():
        st.title("KnowHub Python Quiz")

        # Create a navigation bar with quiz options
        quiz_selection = option_menu("Choose quiz topic", ["Basics", "Strings","Lists"],
                                icons=["list-task", "list-task", "list-task"],
                                menu_icon="info-circle", default_index=0, orientation="horizontal",
                                 styles={
                                     "container": {"padding": "0!important", "background-color": "#fafafa"},
                                     "icon": {"font-size": "25px"},
                                     "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px",
                                                  "--hover-color": "#eee",
                                                  "font-family": "Noto Sans Variable, sans-serif"},
                                     "nav-link-selected": {"background-color": "#1976D2"},
                                 }
                                )

        # Read the selected Excel sheet with questions and answers
        if quiz_selection == "Basics":
            file_path = os.path.join(os.getcwd(), "QuizFiles", "Basics.xlsx")
            df = pd.read_excel(file_path)
        elif quiz_selection == "Strings":
            file_path = os.path.join(os.getcwd(), "QuizFiles", "Strings.xlsx")
            df = pd.read_excel(file_path)
        elif quiz_selection == "Lists":
            file_path = os.path.join(os.getcwd(), "QuizFiles", "Lists.xlsx")
            df = pd.read_excel(file_path)
        else:
            st.error("Quiz not found.")

        # Applying css
        st.markdown(
            """
            <style>
            %s
            </style>
            """ % open("style.css").read(),
            unsafe_allow_html=True
        )

        # Clear submitted answers if quiz selection changes
        if 'submitted_answers' in st.session_state and st.session_state.quiz_selection != quiz_selection:
            if not st.session_state.test_submitted:
                st.error("Great effort! To access this quiz, please submit the current test.")
                st.stop()

            st.session_state.submitted_answers = {i: "" for i in range(len(df))}
            st.session_state.test_submitted = False

        # Create a session state to persist submitted answers and track test submission
        if 'submitted_answers' not in st.session_state:
            st.session_state.submitted_answers = {i: "" for i in range(len(df))}
            st.session_state.test_submitted = False
        st.session_state.quiz_selection = quiz_selection

        # Display text areas for each question
        for i, row in df.iterrows():
            st.write(f"#### Question {i+1}:")
            for line in row['Questions'].split('\n'):
                st.write(line)
            st.session_state.submitted_answers[i] = st.text_area(f"Enter your answer for Question {i+1} here:", value=st.session_state.submitted_answers[i], height=350)

        # Button to submit answers
        if st.button("Submit Test"):
            # Evaluate submitted answers
            evaluate_answers(df, st.session_state.submitted_answers)
            st.session_state.test_submitted = True

        # Display the "Clear Input Answers" button only if the test has been submitted
        if st.session_state.test_submitted:
            if st.button("Clear Input Answers", key="clear_input_answers"):
                st.session_state.submitted_answers = {i: "" for i in range(len(df))}
                st.session_state.test_submitted = False
                st.rerun()

    def evaluate_answers(df, submitted_answers):
        correct_answers = 0
        total_questions = len(df)

        for i, row in df.iterrows():
            answer = row['Answers']
            submitted_answer = submitted_answers[i]

            # Check if the submitted answer is a single-line print statement
            if submitted_answer.strip().startswith("print(") and submitted_answer.strip().endswith(")"):
                submitted_answer = submitted_answer.strip()[6:-1]  # Remove 'print(' and ')' from the answer
                submitted_answer = submitted_answer.strip()

            try:
                # Capture stdout to capture text output
                old_stdout = sys.stdout
                sys.stdout = StringIO()

                # Execute the user's code
                exec(submitted_answer)

                # Get the text output
                text_output = sys.stdout.getvalue()

                # Reset the standard output
                sys.stdout = old_stdout

                # Compare user's output with the answer
                if str(text_output).strip() == str(answer).strip():
                    correct_answers += 1
            except Exception as e:
                pass

        score = correct_answers / total_questions * 100
        if score > 50:
            st.success(f"Congratulations! You aced the test with an impressive score of {score:.2f}%")
        else:
            st.error(f"Keep going! You made progress by scoring {score:.2f}% on the test!")

    quizzes()


if __name__ == "__main__":
    main()