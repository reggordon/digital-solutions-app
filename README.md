# Streamlit Punk News

This project is a Streamlit application that fetches and displays the latest punk rock news from Google's News RSS feed. It provides a simple and interactive interface for users to stay updated on punk rock music and culture.

## Project Structure

```
streamlit-punk-news
├── src
│   ├── app.py            # Main entry point of the Streamlit application
│   ├── fetcher.py        # Functions to fetch and parse punk rock news from RSS feed
│   └── components
│       └── news_card.py  # Component for displaying individual news articles
├── requirements.txt      # Python dependencies for the project
├── .gitignore            # Files and directories to be ignored by Git
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd streamlit-punk-news
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the Streamlit application, execute the following command:

```bash
streamlit run src/app.py
```

This will start the Streamlit server and open the application in your default web browser.

Quick start (recommended)

1. Make the included launcher executable:

```bash
chmod +x ./run.sh
```

2. Run the launcher. It will create a virtualenv if needed and install requirements:

```bash
./run.sh
```

Notes
- The launcher prefers a `.venv` virtual environment directory. If you already have a `venv` directory
   the script will use it.
- The app caches RSS fetches for 10 minutes to avoid repeated network calls.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.