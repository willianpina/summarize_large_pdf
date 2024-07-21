### PDF SUMMARIZER

This project is a Streamlit application that allows the upload of PDF files and generates summaries of the content, along with the option to convert the summary into audio. The application is simple and intuitive, offering a user-friendly interface for users who want to quickly summarize documents and listen to the generated summaries.

#### Features

- **PDF Upload**: Allows users to upload PDF files directly into the application.
- **Summary Generation**: Uses a text processing module to generate a summary of the PDF content.
- **Audio Conversion**: Converts the generated summary into audio using the `gTTS` (Google Text-to-Speech) library.
- **Audio Download**: Provides a download link for the generated audio file.
- **File Clearing**: Option to delete the uploaded file and reset the progress bar.

#### How to Use

1. **Upload PDF**: Click the upload button and select the PDF file you want to summarize.
2. **View Summary**: After uploading, the application will process the PDF and display the summary on the screen.
3. **Listen to Summary**: The generated summary will be converted into audio, which can be listened to directly in the application.
4. **Download Audio**: A download link will be provided so that the audio can be saved locally.
5. **Delete File**: Use the button to delete the uploaded file and reset the progress bar.

#### Technologies Used

- **Streamlit**: Framework for creating interactive web applications.
- **tempfile**: Library for handling temporary files.
- **gTTS**: Library for text-to-speech conversion.
- **base64**: Library for encoding and decoding data in Base64.
- **PDFSummarizer**: Custom class for summarizing PDF file content.

#### Requirements

- Python 3.6 or higher
- Libraries listed in the `requirements.txt` file

#### How to Run

1. Clone the repository:
    ```bash
    git clone https://github.com/willianpina/summarize_large_pdf.git
    ```
2. Navigate to the project directory:
    ```bash
    cd your-repository
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the application:
    ```bash
    streamlit run app.py
    ```

#### Contributions

Contributions are welcome! Feel free to open issues or submit pull requests.

#### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Developed by [Willian Pina](https://github.com/willianpina).
