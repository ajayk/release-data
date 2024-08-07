import re

from bs4 import BeautifulSoup
from common import dates, http, releasedata

"""Fetches Amazon RDS versions from the version management pages on AWS docs.

Pages parsed by this script are expected to have version tables with a version in the first column and its release date
in the third column (usually named 'RDS release date').
"""

PRODUCTS = {
    "amazon-rds-mysql": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.Concepts.VersionMgmt.html",
    "amazon-rds-postgresql": "https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-release-calendar.html",
    "amazon-rds-mariadb": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MariaDB.Concepts.VersionMgmt.html",
}
VERSION_REGEX = re.compile(r"(?P<version>\d+(?:\.\d+)*)", flags=re.IGNORECASE)  # https://regex101.com/r/BY1vwV/1

for product_name, url in PRODUCTS.items():
    with releasedata.ProductData(product_name) as product_data:
        response = http.fetch_url(url)
        soup = BeautifulSoup(response.text, features="html5lib")

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) <= 3:
                    continue

                version_match = VERSION_REGEX.search(columns[0].text.strip())
                if version_match:
                    version = version_match.group("version")
                    date = dates.parse_date(columns[2].text)
                    product_data.declare_version(version, date)
