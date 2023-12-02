# YouTube Data Harvesting and Warehousing
### Overview
This project focuses on the extraction, storage, and visualization of YouTube data using a combination of SQL, MongoDB, and Streamlit. The goal is to harvest relevant information from YouTube videos, warehouse it efficiently, and create a user-friendly interface for exploring the data.

### Features
Data Harvesting: Utilize YouTube API to gather essential information from videos, including metadata, statistics, and comments.

Storage with SQL and MongoDB: Implement a robust data warehousing strategy by storing structured data in SQL databases for efficient querying and unstructured data, such as comments, in MongoDB for flexibility.

Streamlit Dashboard: Develop a dynamic and interactive dashboard using Streamlit, allowing users to explore the harvested YouTube data with ease.

Getting Started
Clone the Repository:

bash
Copy code
git clone https://github.com/your-username/youtube-data-warehouse.git
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Configuration:

Obtain YouTube API key and update config.py with your credentials.
Configure SQL and MongoDB connection details in config.py.
Run the Application:

bash
Copy code
streamlit run app.py
Access the Streamlit dashboard at http://localhost:8501 in your web browser.

# Usage
Harvesting Data:

Specify YouTube channels or videos to harvest data from.
Run the data harvesting script to populate the databases.
Exploring Data:

Open the Streamlit dashboard to visualize and analyze the harvested data.
Utilize the interactive interface to filter, sort, and explore insights.
Contribution Guidelines
We welcome contributions to enhance the functionality and usability of this project. Please follow the guidelines outlined in CONTRIBUTING.md.

### License
This project is licensed under the MIT License.

### Acknowledgments
Special thanks to the YouTube API, SQL, MongoDB, and Streamlit communities for their invaluable resources and support.
Feel free to reach out for questions, feedback, or collaboration opportunities. Happy coding!






