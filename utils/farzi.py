class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __str__(self):
        return f"[meta = {self.metadata}, content = {self.page_content}]"    


class VecStore():
    def __init__(self):
        pass

    def add_documents(self, documents, ids):
        pass

    def as_retriever(self, search_kwargs):
        pass
