import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

import pandas as pd

from src.schema.arxiv_schema import ArxivRawMetadata, ArxivMetadata
from src.schema_validator.metrics import MetricProvider

ARXIV_ENTRY_ELMT_TAG = "{http://www.w3.org/2005/Atom}entry"
ARXIV_XML_NS = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

class ArxivRawMetadataParser:
    @classmethod
    def from_xml(cls, entry: ET.Element, metrics_provider: MetricProvider) -> ArxivRawMetadata:
        @staticmethod
        def get_text(el: ET.Element, tag: str) -> str:
            e = el.find(f'atom:{tag}', ARXIV_XML_NS)
            return e.text.strip() if e is not None and e.text else ""
        
        @staticmethod
        def get_authors(el: ET.Element) -> List[Optional[str]]:
            return [
                get_text(author_el, 'name')
                for author_el in el.findall('atom:author', ARXIV_XML_NS)
            ]

        def get_pdf_link(el: ET.Element) -> str:
            for link in el.findall('atom:link', ARXIV_XML_NS):
                if link.attrib.get('title') == 'pdf':
                    return link.attrib['href']
            return ""
        
        counters = metrics_provider.get_counters() if metrics_provider else {}

        return ArxivRawMetadata(
            arxiv_url=get_text(entry, 'id'),
            title=get_text(entry, 'title'),
            summary=get_text(entry, 'summary'),
            published=get_text(entry, 'published'),
            updated=get_text(entry, 'updated'),
            authors=get_authors(entry),
            pdf_url=get_pdf_link(entry),
            primary_category=entry.find('arxiv:primary_category', ARXIV_XML_NS).attrib.get('term', None) \
            if entry.find('arxiv:primary_category', ARXIV_XML_NS) is not None else "",
            **counters
        )

    @staticmethod
    def from_xml_filepath(
        xml_filepath: str,
        metrics_provider: Optional[MetricProvider] = None
    ) -> List[ArxivRawMetadata]:

        tree = ET.parse(xml_filepath)
        root = tree.getroot()

        results = [
            ArxivRawMetadataParser.from_xml(rooti, metrics_provider=metrics_provider)
            for rooti in root if rooti.tag == ARXIV_ENTRY_ELMT_TAG
        ]

        return results

class ArxivMetadataTransformer:
    @staticmethod
    def parse_arxiv_id(arxiv_url: str) -> Tuple[int, str]:
        arxiv_id = arxiv_url.split('/')[-1]
        v_loc = arxiv_id.find('v')
        version = int(arxiv_id[v_loc+1:])
        arxiv_doi = arxiv_id[:v_loc]
        return version, arxiv_doi

    @staticmethod
    def transform(arxiv_raw_metadata: ArxivRawMetadata, metrics_provider: MetricProvider) -> ArxivMetadata:
        version, arxiv_doi = ArxivMetadataTransformer.parse_arxiv_id(arxiv_url=arxiv_raw_metadata.arxiv_url)
        published_yyyy_mm = pd.to_datetime(arxiv_raw_metadata.published).strftime('%Y-%m')

        counters = metrics_provider.get_counters() if metrics_provider else {}

        return ArxivMetadata(
            arxiv_doi=arxiv_doi,
            arxiv_version=version,
            title=arxiv_raw_metadata.title,
            summary=arxiv_raw_metadata.summary,
            published=arxiv_raw_metadata.published,
            updated=arxiv_raw_metadata.updated,
            authors=arxiv_raw_metadata.authors,
            pdf_url=arxiv_raw_metadata.pdf_url,
            primary_category=arxiv_raw_metadata.primary_category,
            published_yyyy_mm=published_yyyy_mm,
            **counters
        )

    @staticmethod
    def transform_from_list(arxiv_raw_metadatas: List[ArxivRawMetadata], metrics_provider: Optional[MetricProvider] = None) -> List[ArxivMetadata]:
        results = [
            ArxivMetadataTransformer.transform(arxiv_raw_metadata=arxiv_raw_metadata, metrics_provider=metrics_provider) for arxiv_raw_metadata in arxiv_raw_metadatas
        ]

        return results


if __name__ == "__main__":
    pass
    # for test
    # arxiv_raw_metadatas = ArxivRawMetadataParser.from_xml_filepath(xml_filepath="./tmp_xml/0deb32df.xml")
    # arxiv_metadatas = ArxivMetadataTransformer.transform_from_list(arxiv_raw_metadatas=arxiv_raw_metadatas)
    # arxiv_metadatas[3].to_iceberg_schema()
