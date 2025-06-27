from langchain_community.document_loaders.csv_loader import UnstructuredCSVLoader

loader = UnstructuredCSVLoader(
    file_path="example_data/mlb_teams_2012.csv", mode="elements"
)
docs = loader.load()

print(docs[0].metadata["text_as_html"])