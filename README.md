# Chat-Based Access to Legislation - test environment

---

## 1. Project Name
Chat-Based Access to Legislation - test environment

---

## 2. Project Goal / Overview
_What does this project aim to do? Why was it built?_

- Experimental platform for chat-based access to New Zealand legislation
- Uses Retrieval-Augmented Generation (RAG) to ground answers in legislative text
- Built to explore how AI can improve public access to law, while avoiding legal interpretation
- Intended for research, prototyping, and demonstration purposes

---

## Disclaimer

This code was created by an external provider as part of a research and development project. We're sharing it here to encourage open access and collaboration, but it wasn't developed by the Parliamentary Counsel Office, and we are unable to provide support. The code hasn’t been tested for use in live or production environments, and we can’t make any promises about how well it works or how safe or reliable it is. We think it’s a great example of what’s possible. But if you choose to use it, you must do so at your own risk as we’re not responsible for any problems that might result. We recommend testing it carefully in a safe setting before using it in any important or sensitive context.

---

## 3. Getting Started
_How can someone run or use this code?_

- **Recommended: Use Docker Compose for Dependencies**
  1. Ensure you have Docker and Docker Compose installed.
  2. In the project root, run:
     ```bash
     docker-compose up
     ```
     This will start the required dependencies (MongoDB and Chroma) in containers.
  3. **You must still start the frontend and backend servers manually:**
     - Start the frontend:
       ```bash
       cd frontend
       npm install
       npm run dev
       ```
       Access at http://localhost:3000
     - Start the backend:
       ```bash
       cd backend
       poetry install
       poetry shell
       uvicorn main:app --reload
       ```
       Access API docs at http://localhost:8000/docs

- **Manual Setup (for development/advanced use):**
  - You may also run MongoDB and Chroma locally without Docker, but Docker Compose is recommended for convenience.

---

## 4. Data Loading and Preparation

To prepare the system for use, follow these steps:

1. **Parse and Import Legislation Data**
   - Use the CLI tool to parse XML files into JSON and load them into the database.
   - **Arguments:**
     - `leg_paths` (positional, required): One or more paths to legislation files or directories (relative to the data path). Example: `2013/PrivacyAct2013`
     - `--data-path` (optional): Base data directory path. Default is `../../data`.
   - **Example usage:**
     ```bash
     cd backend
     python -m app.parsers.cli <ACT_YEAR>/<ACT_NAME>
     ```
     Replace `<ACT_YEAR>/<ACT_NAME>` with the path to your XML files (e.g., `2013/PrivacyAct2013`).

     To specify a custom data directory:
     ```bash
     python -m app.parsers.cli <ACT_YEAR>/<ACT_NAME> --data-path /path/to/data
     ```

2. **Generate Summaries for Fragments**
   - Use the script to generate AI-powered summaries and context summaries for each fragment.
   - Example:
     ```bash
     cd backend/scripts
     python generate_summaries.py
     ```
   - You may need API keys or environment variables for the LLM provider (see backend README or .env.example).

3. **Generate Embeddings**
   - Use the script to generate embeddings for each fragment.
   - Example:
     ```bash
     python populate_embeddings.py
     ```
   - Optional arguments:
     - `--document-id <ID>`: Only process a specific document.
     - `--batch-size <N>`: Set batch size for embedding generation.

4. **Create the Vector Index**
   - Use the script to create the vector index in Chroma.
   - Example:
     ```bash
     python create_vector_index.py
     ```

---

## 4. Known Limitations / Shortcomings
_Are there any known issues, limitations, or areas that are unfinished or need improvement?_

- Not production-ready; for research/demo only
- Limited to a subset of New Zealand legislation (demo data only)
  The script provided to parse legislation has only been tested on a small number of Acts, and the validation model in the script would need to be expanded to incorporate more Acts.
- The tools and chat experience used in this application are
  pretty limited and have many serious issues that are not documented here. This is not a recommended starting point for any serious chatbot application.

---

## 5. Opportunities for Future Work
_What could be improved or added in the future?_

- We would not recommend continuing to build on this application.

---

## 7. Contributions
_Whether this code is  being actively maintained_

- This codebase is not actively maintained. Contributions are not currently being accepted.

---

## 8. License
_What license applies to this code?_

- This project is licensed under the terms of the MIT license.
- See the LICENSE file included in this repository.

---

## 9. Contact
_Who should someone contact with questions or suggestions?_

- For questions or suggestions, please contact info@boost.co.nz
https://www.boost.co.nz/
