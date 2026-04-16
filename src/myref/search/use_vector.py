from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer
from torch import Tensor
import numpy as np
import faiss

from myref.search.langugae_processing_variables import LanguageProcessingVariables as LPVar

class UseVector:
    def __init__(self):
        self.model_dir = LPVar.MODEL_DIR
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = ORTModelForFeatureExtraction.from_pretrained(
            self.model_dir, 
            file_name=LPVar.MODEL_NAME
            )
        
    def average_pool(self, 
                     last_hidden_states: Tensor, 
                     attention_mask: Tensor
                     ) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    def create_embedding_np(self, 
                            input_texts: list[str]
                            ) -> np.ndarray:
        batch_dict = self.tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')
        outputs = self.model(**batch_dict)

        embeddings = self.average_pool(outputs.last_hidden_state, 
                                       batch_dict['attention_mask'])
        embeddings_np = embeddings.cpu().detach().numpy().astype(np.float32)
        normalized_embeddings_np = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)
        return normalized_embeddings_np

    def search_vector(self, 
                      query_text: list[str], 
                      target_normalized_embeddings_np: np.ndarray, 
                      k: int = 5
                      ):
        query_dict = self.tokenizer(query_text, max_length=512, padding=True, truncation=True, return_tensors='pt')
        query_output = self.model(**query_dict) 

        query_embeddings = self.average_pool(query_output.last_hidden_state, query_dict['attention_mask'])
        query_embeddings_np = query_embeddings.cpu().detach().numpy().astype(np.float32)
        normalized_query_embeddings_np = query_embeddings_np / np.linalg.norm(query_embeddings_np, axis=1, keepdims=True)
        dimension = target_normalized_embeddings_np.shape[1]

        index_flat_l2 = faiss.IndexFlatL2(dimension)
        index_flat_l2.add(target_normalized_embeddings_np)  
        print("Number of vectors in the IndexFlatL2:", index_flat_l2.ntotal)

        D_l2, I_l2 = index_flat_l2.search(normalized_query_embeddings_np, k)

        return D_l2, I_l2
    
    def get_search_results(self, 
                           query_text: list[str], 
                           target_normalized_embeddings_np: np.ndarray, 
                           search_base: list[str],
                           k: int | None = None
                           ) -> list[str]:
        I_l2 = self.search_vector(query_text=query_text,
                                  target_normalized_embeddings_np=target_normalized_embeddings_np,
                                  k=k)[1]
        search_results = []
        for i in range(k):
            search_results.append(search_base[I_l2[0][i]])
        return search_results
    
    def get_distance_result(self,
                            query_text: list[str], 
                            target_normalized_embeddings_np: np.ndarray, 
                            k: int | None = None
                            ) -> list[float]:
        D_l2 = self.search_vector(query_text=query_text,
                                  target_normalized_embeddings_np=target_normalized_embeddings_np,
                                  k=k)[0]
        search_distance_results = []
        for i in range(k):
            search_distance_results.append(D_l2[0][i])
            
        return search_distance_results