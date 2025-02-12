# 📝 Documents Summarization IA Tool

An AI-powered tool for summarizing documents (PDF, TXT, DOCX) using OpenAI's API and LangChain.  
This tool provides options for different summary types and lengths and allows users to download summaries as PDFs.

## Home Page

![image](https://github.com/user-attachments/assets/4de98845-ee93-4a16-927a-a860484b445b)

## Summarizing document

![image](https://github.com/user-attachments/assets/7788aacf-87b5-4165-8c86-03dce9baa017)

## Summary succeeded

![image](https://github.com/user-attachments/assets/b80dcfcf-64fb-42f0-9709-01eabe45d3f8)

## History Page

![image](https://github.com/user-attachments/assets/2b71657b-2ac1-47df-9f41-42cd9353c407)

---

## 🚀 Features
- 📝 Upload documents for AI-generated summaries
- ✨ Choose summary type: **Default, Bullet Points, Key Points**
- 📏 Select summary length: **Concise, Moderate, Detailed**
- 💜 View summary history with timestamps
- 📅 Download summaries as **PDFs**
- 🎨 Dark/Light Mode support
- 📱 Mobile-responsive UI

---

##  **Tech Stack**

- Flask for the web interface and file upload handling.
- OpenAI models for generating summaries.
- LangChain for document preprocessing and chunking.

---

## 📌 **Setup Instructions**

### **1⃣ Install Dependencies**
Ensure you have Python (≥3.8) and pip installed.

Clone the repository and install the required dependencies:
```sh
git clone https://github.com/your-repo/Documents_Summarization_IA_Tool.git
cd Documents_Summarization_IA_Tool
pip install -r requirements.txt
```

---

### **2⃣ Set Up Environment Variables**

Create or edit the `.env`* file in the project root and add your OpenAI API & LangSmith API & Secret keys:

```sh
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
SECRET_KEY=any-secret-key
```

---

### **3⃣ Set Up PDF Generation (Windows Users)**
For downloading summaries as PDFs, **MSYS2** and **Pango** are required.

#### ✅ **Install MSYS2**
Download and install MSYS2 from:  
🔗 [MSYS2 Installation](https://www.msys2.org/#installation)

#### ✅ **Install Pango (Required for WeasyPrint)**
After installing MSYS2, open the MSYS2 shell and run:
```sh
pacman -S mingw-w64-x86_64-pango
```

For **Linux/macOS**, install Pango using:
```sh
sudo apt install libpango1.0-dev  # Ubuntu/Debian
brew install pango  # macOS (Homebrew)
```

---

### **4⃣ Run the Application**
Start the Flask server:
```sh
flask run
```
The app will be accessible at:  
🤾 `http://127.0.0.1:5000/`

---

## 💼 API Documentation

### **1⃣ Upload File**
**Endpoint:** `/upload`  
**Method:** `POST`  
**Description:** Uploads a document and returns the summarized text.  

#### **📄 Request**
- **Headers:** `multipart/form-data`
- **Body Parameters:**
  | Key          | Type      | Description |
  |-------------|----------|-------------|
  | `file`      | `file`   | The document to summarize (TXT, PDF, DOCX, DOC) |
  | `summary_type` | `string` | Options: `default`, `bullet_points`, `key_points` |
  | `summary_length` | `string` | Options: `concise`, `moderate`, `detailed` |
  | `language`  | `string` | Options: `english`, `french` |

#### **📅 Example Request**
```sh
curl -X POST http://127.0.0.1:5000/upload \
  -F "file=@document.pdf" \
  -F "summary_type=default" \
  -F "summary_length=moderate" \
  -F "language=english"
```

#### **📄 Response (Success)**
```json
{
  "summary": "This is a summarized version of your document...",
  "message": "File processed successfully"
}
```

#### **⚠️ Response (Error)**
```json
{
  "error": "No file part"
}
```

---

### **2⃣ Get Summary History**
**Endpoint:** `/history`  
**Method:** `GET`  
**Description:** Retrieves the list of summarized documents.

#### **📅 Example Request**
```sh
curl -X GET http://127.0.0.1:5000/history
```

#### **📄 Response**
```json
[
  {
    "id": 1,
    "filename": "document.pdf",
    "summary_type": "default",
    "summary_length": "moderate",
    "created_at": "2025-02-12T14:30:00Z",
    "summary_content": "This is a summarized version..."
  }
]
```

---

### **3⃣ Download Summary as PDF**
**Endpoint:** `/download_summary/<summary_id>`  
**Method:** `GET`  
**Description:** Generates a PDF of the summary and downloads it.

#### **📅 Example Request**
```sh
curl -X GET http://127.0.0.1:5000/download_summary/1
```

#### **📄 Response**
A downloadable **PDF file**.

---

## 📀 **Future Enhancements**
- ✅ Export summaries in multiple formats (TXT, Word)
- ✅ Add AI-based keyword extraction
- ✅ Enhance UI/UX for a smoother experience

---

## 🤝 **Contributing**
Feel free to submit **pull requests** or open **issues** for bug fixes and feature requests.

---

## 💜 **License**
This project is licensed under the **MIT License**.

---

🚀 Happy Summarizing! 🎉

