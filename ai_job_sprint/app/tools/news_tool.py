from app.data_pipeline.source_loader import (
    fetch_api_posts,
)


def fetch_latest_posts():

    data = fetch_api_posts(
        base_url=("https://jsonplaceholder." "typicode.com/posts"),
        pages=1,
        page_size=5,
    )

    return data
