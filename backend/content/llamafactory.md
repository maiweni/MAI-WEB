# llamafactory训练数据排查



## 







1、超参数文件夹：src/llamafactory/hparams

2、如果不使用MCA还有KT，那么才使用普通的的sft，run_sft路径为：src/llamafactory/train/sft/workflow.py

3、使用transformers的 AutoTokenizer.from_pretrained加载，padding_side="right",使用AutoProcessor.from_pretrained，AutoProcessor这个在纯文本模型中用不到，主要是使用在多模态的模型中

