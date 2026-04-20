import os
import pickle
from pathlib import Path

import numpy as np
import faiss

from oxoria.global_var import GBVar

class SearchBase():
    def __init__(self):
        self.data_path = Path(GBVar.DATA_DIR)
        if not self.data_path.exists():
            return
        self.search_base_path = self.data_path / "language_model/search_base.pkl"

    def get_base(self) -> list:
        if self.search_base_path.exists():
            with open(self.search_base_path, "rb") as f:
                search_base = pickle.load(f)
        else:
            search_base = []
        return search_base
    
    def set_base(self, 
                 new_search_base: list
                 ) -> None:
        with open(self.search_base_path, "wb") as f:
            pickle.dump(new_search_base, f)
        return
    
class FaissIndexBase:
    def __init__(self):
        self.data_path = Path(GBVar.DATA_DIR)
        if not self.data_path.exists():
            return
        self.faiss_index_path = self.data_path / "language_model/search_data.faiss"

    def write_index(self, 
                    data: faiss.Index
                    ) -> None:
        faiss.write_index(data, str(self.faiss_index_path))

    def add_index(self, 
                  index: faiss.Index, 
                  new_data: np.ndarray
                  ) -> None:
        index.add(new_data)
        self.write_index(index)

    def read_index(self) -> faiss.Index:
        if self.faiss_index_path.exists():
            index = faiss.read_index(str(self.faiss_index_path))
        else:
            index = faiss.IndexFlatL2(768)
        return index