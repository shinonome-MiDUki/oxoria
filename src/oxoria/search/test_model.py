from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer
from torch import Tensor
import torch.nn.functional as F
import faiss
import numpy as np

from oxoria.search.langugae_processing_variables import LanguageProcessingVariables as LPVar

def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

input_texts = [
    "かわいい猫の写真",
    "美味しいカレーの店",
    "おすすめの旅行先",
    "かわいいアイドルの画像",
    "人気の映画ランキング",
    "夏休み海水浴の写真",
    "美味しいスイーツの店",
    "おすすめの本"
]

model_dir = LPVar.MODEL_DIR
# ONNX
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = ORTModelForFeatureExtraction.from_pretrained(
    model_dir, 
    file_name=LPVar.MODEL_NAME
    )
batch_dict = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')


for i, (key, tensor) in enumerate(batch_dict.items()):
    print(f"[{i}][batch_dict] {key}: {tensor.size()}")


outputs = model(**batch_dict)

for i, (key, tensor) in enumerate(outputs.items()):
    print(f"[{i}][outputs] {key}: {tensor.size()}")

embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

embeddings_np = embeddings.cpu().detach().numpy().astype(np.float32)
normalized_embeddings_np = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)
print("normalized_embeddings_np shape:", normalized_embeddings_np.shape)

import time
timer_start = time.time()

# クエリテキストを定義します。
query_text = ["直木賞"]  # クエリテキストの例

# クエリテキストをトークナイズし、モデルが処理できる形式にします。
query_dict = tokenizer(query_text, max_length=512, padding=True, truncation=True, return_tensors='pt')

# モデルを実行して出力を取得します。
query_output = model(**query_dict)

# `average_pool`関数を使って、クエリの埋め込みベクトルを計算します。
query_embeddings = average_pool(query_output.last_hidden_state, query_dict['attention_mask'])

# クエリの埋め込みベクトルをNumPy配列に変換します。
query_embeddings_np = query_embeddings.cpu().detach().numpy().astype(np.float32)
normalized_query_embeddings_np = query_embeddings_np / np.linalg.norm(query_embeddings_np, axis=1, keepdims=True)
# ベクトルの次元数を設定
dimension = normalized_embeddings_np.shape[1]

# IndexFlatL2インデックスの初期化とデータ追加
index_flat_l2 = faiss.IndexFlatL2(dimension)
index_flat_l2.add(normalized_embeddings_np)  # 正規化済みで追加
print("Number of vectors in the IndexFlatL2:", index_flat_l2.ntotal)

# 上位3つの近いベクトルを検索するための設定（k=3）
k = 5

# 各インデックスに対して検索を実行し、結果を取得
D_l2, I_l2 = index_flat_l2.search(normalized_query_embeddings_np, k)

# 結果を表示する関数
def display_results(D, I, input_texts, index_type):
    print(f"Results for {index_type}:")
    for i in range(k):
        print(f"  Rank: {i+1}, Index: {I[0][i]}, Distance: {D[0][i]}, Text: '{input_texts[I[0][i]]}")

# 各インデックスタイプの結果を表示
display_results(D_l2, I_l2, input_texts, "IndexFlatL2")

print(f"Search completed in {time.time() - timer_start:.4f} seconds")