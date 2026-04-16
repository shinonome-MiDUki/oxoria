from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from optimum.onnxruntime import ORTQuantizer

class Quantumization:
    def __init__(self, model_id: str, save_dir: str):
        self.model_id = model_id
        self.save_dir = save_dir

    def quantize_model(self) -> None:
        model = ORTModelForFeatureExtraction.from_pretrained(self.model_id, export=True)
        tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        quantizer = ORTQuantizer.from_pretrained(model)
        dqconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)
        quantizer.quantize(save_dir=self.save_dir, quantization_config=dqconfig)

        tokenizer.save_pretrained(self.save_dir)

        return
    