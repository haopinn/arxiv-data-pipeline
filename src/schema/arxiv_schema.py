from typing import List, Optional

from src.schema.base import DataModelMixin

class ArxivRawMetadata(DataModelMixin):
    arxiv_url: str
    title: str = ""
    summary: str = ""
    published: str = ""
    updated: str = ""
    authors: List[Optional[str]] = []
    pdf_url: str = ""
    primary_category: str = ""

class ArxivMetadata(DataModelMixin):
    arxiv_doi: str
    arxiv_version: int
    title: str = ""
    publishded: str = ""
    updated: str = ""
    authors: List[str] = []
    pdf_url: str = ""
    primary_category: str = ""
    published_yyyy_mm: str = ""

if __name__ == "__main__":
    pass
    # for dev
    # # 定義 partition spec：用 published_yyyy_mm 欄位作為 identity partition
    # arxiv_partition_spec = PartitionSpec(fields=[
    #     PartitionField(
    #         source_id=arxiv_schema.find_field("published_yyyy_mm").field_id, 
    #         field_id=0,
    #         name="published_yyyy_mm", 
    #         transform=IdentityTransform())
    # ])
